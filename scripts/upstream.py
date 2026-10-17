#!/usr/bin/env python3
"""Compare, stage, and explicitly apply reviewed vendored skill updates."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / 'upstream/pstack-lock.json'
PACKS = ('pstack', 'cursor-team-kit')
SOURCE = 'pstack'


def select_source(name):
    global SOURCE, LOCK, PACKS
    SOURCE = name
    LOCK = ROOT / f'upstream/{name}-lock.json'
    PACKS = ('pstack', 'cursor-team-kit') if name == 'pstack' else ()


def git(checkout, *args, check=True):
    result = subprocess.run(['git', '-C', str(checkout), *args], capture_output=True, check=check)
    return result.stdout


def digest(content):
    return hashlib.sha256(content).hexdigest() if content is not None else None


def blob(checkout, ref, path):
    result = subprocess.run(['git', '-C', str(checkout), 'show', f'{ref}:{path}'], capture_output=True)
    if result.returncode:
        raise ValueError(f'Cannot read pinned source object {ref}:{path}; fetch the required history')
    return result.stdout


def modes(checkout, ref):
    rows = git(checkout, 'ls-tree', '-r', '-z', ref, '--', *PACKS).split(b'\0')
    return {row.split(b'\t', 1)[1].decode(): row.split(b' ', 1)[0].decode() for row in rows if row}


def inventory(checkout, ref):
    names = git(checkout, 'ls-tree', '-r', '--name-only', '-z', ref, '--', *PACKS).split(b'\0')
    return {name.decode(): digest(blob(checkout, ref, name.decode())) for name in names if name}


def target_for(source):
    parts = source.split('/')
    if SOURCE == 'mattpocock':
        if len(parts) >= 4 and parts[0] == 'skills':
            return 'skills/mattpocock-' + parts[2] + '/' + '/'.join(parts[3:]), False
        if source == 'LICENSE':
            return 'upstream/mattpocock-LICENSE', False
        return None, True
    pack = parts[0]
    if len(parts) >= 4 and parts[1] == 'skills':
        return 'skills/' + '/'.join(parts[2:]), False
    if source.startswith('pstack/automations/benny/skills/'):
        return 'skills/' + source.removeprefix('pstack/automations/benny/skills/'), False
    if source.startswith('pstack/automations/benny/templates/'):
        return 'skills/setup-benny/templates/' + source.rsplit('/', 1)[1], False
    if len(parts) == 3 and parts[1] == 'agents':
        name = Path(parts[-1]).stem
        if name == 'thermo-nuclear-code-quality-review':
            return 'skills/' + name + '/references/delegate.md', False
        return 'skills/' + name + '/SKILL.md', False
    if parts[-1] == 'LICENSE':
        return 'upstream/' + pack + '-LICENSE', False
    if len(parts) == 3 and parts[1] == 'rules':
        return 'skills/deslop/references/companion-rules.md', True
    # Manifest, guide, artwork, and pack bootstrap changes still require an explicit review.
    return None, True


def local_path(target):
    path = (ROOT / target).resolve()
    if not path.is_relative_to(ROOT) or any(p.is_symlink() for p in [ROOT / target, *(ROOT / target).parents] if p != ROOT.parent):
        raise ValueError(f'Unsafe target path: {target}')
    return path


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')


def compare(checkout, ref):
    lock = json.loads(LOCK.read_text())
    commit = git(checkout, 'rev-parse', '--verify', ref + '^{commit}').decode().strip()
    current = inventory(checkout, commit)
    old_modes = lock.get('sourceModes') or modes(checkout, lock['commit'])
    new_modes = modes(checkout, commit)
    changes = []
    for source in sorted(set(lock['sourceFiles']) | set(current)):
        old, new = lock['sourceFiles'].get(source), current.get(source)
        if old == new and old_modes.get(source) == new_modes.get(source):
            continue
        target, manual = target_for(source)
        changes.append({'source': source, 'kind': 'added' if old is None else 'deleted' if new is None else 'modified',
                        'baseHash': old, 'incomingHash': new, 'baseMode': old_modes.get(source),
                        'incomingMode': new_modes.get(source), 'target': target, 'manual': manual})
    return lock, commit, current, changes


def stage(checkout, ref, output):
    lock, commit, current, changes = compare(checkout, ref)
    output.mkdir(parents=True, exist_ok=False)
    groups = {}
    for change in changes:
        source = change['source']
        for label, revision, expected in [('base', lock['commit'], change['baseHash']),
                                           ('incoming', commit, change['incomingHash'])]:
            if expected is None:
                continue
            content = blob(checkout, revision, source)
            if digest(content) != expected:
                raise ValueError(f'Source does not match recorded hash: {source}')
            path = output / label / source
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        key = change['target'] or '@review/' + source
        groups.setdefault(key, []).append(change)
    entries = []
    for target, sources in groups.items():
        mapped = not target.startswith('@review/')
        local = local_path(target) if mapped else None
        content = local.read_bytes() if local and local.exists() else None
        status = 'review'
        merged = None
        if mapped:
            merged = output / 'merged' / target
            merged.parent.mkdir(parents=True, exist_ok=True)
            first = sources[0]
            if len(sources) == 1 and not first['manual'] and first['kind'] == 'modified' and content is not None:
                ours = output / 'ours' / target
                ours.parent.mkdir(parents=True, exist_ok=True)
                ours.write_bytes(content)
                result = subprocess.run(['git', 'merge-file', '-p', str(ours),
                                         str(output / 'base' / first['source']),
                                         str(output / 'incoming' / first['source'])], capture_output=True)
                if 0 <= result.returncode <= 127:
                    merged.write_bytes(result.stdout)
                    status = 'clean-merge' if result.returncode == 0 else 'conflict'
                else:
                    merged.write_bytes(content)
            elif first['kind'] == 'added' and content is None and len(sources) == 1:
                merged.write_bytes((output / 'incoming' / first['source']).read_bytes())
                status = 'new-needs-port'
            elif content is not None:
                merged.write_bytes(content)
            else:
                merged = None
        entries.append({'target': target if mapped else None, 'sources': sources, 'status': status,
                        'localHash': digest(content), 'localMode': local.stat().st_mode & 0o777 if local and local.exists() else None, 'merged': str(merged.relative_to(output)) if merged else None,
                        'decision': 'pending', 'reason': ''})
    plan = {'source': SOURCE, 'baseCommit': lock['commit'], 'commit': commit, 'lockHash': digest(LOCK.read_bytes()),
            'sourceFiles': current, 'sourceModes': modes(checkout, commit), 'entries': entries}
    # Version metadata is source evidence, never copied into a host manifest blindly.
    plan['versions'] = {}
    if SOURCE == 'mattpocock':
        info = json.loads(blob(checkout, commit, 'package.json'))
        plan['versions']['mattpocock'] = info['version']
        for key in ['dependencies', 'devDependencies']:
            if info.get(key):
                plan.setdefault('declaredDependencies', {})[key] = info[key]
    for pack in PACKS:
        info = json.loads(blob(checkout, commit, pack + '/.cursor-plugin/plugin.json'))
        plan['versions'][pack] = info['version']
        if info.get('dependencies'):
            plan.setdefault('declaredDependencies', {})[pack] = info['dependencies']
    write_json(output / 'plan.json', plan)
    print(json.dumps({'base': lock['commit'], 'incoming': commit, 'sourceChanges': len(changes),
                      'reviewEntries': len(entries), 'plan': str(output / 'plan.json')}))


def _apply(output):
    plan = json.loads((output / 'plan.json').read_text())
    if plan.get('source', 'pstack') != SOURCE:
        raise ValueError('Stage belongs to another upstream source; select the matching --source')
    if digest(LOCK.read_bytes()) != plan['lockHash']:
        raise ValueError('Source lock changed since staging; stage again')
    writes = []
    for entry in plan['entries']:
        decision = entry['decision']
        if decision not in ['accept', 'keep', 'delete']:
            raise ValueError('Every entry needs an accept, keep, or delete decision')
        if not entry['reason'].strip():
            raise ValueError('Every decision needs a review reason, including clean merges')
        if entry['target'] is None:
            if decision != 'keep':
                raise ValueError('Unmapped source changes need a keep decision and review reason')
            continue
        target = local_path(entry['target'])
        before = target.read_bytes() if target.exists() else None
        before_mode = target.stat().st_mode & 0o777 if target.exists() else None
        if digest(before) != entry['localHash'] or before_mode != entry['localMode']:
            raise ValueError(f'Local file changed since staging: {entry["target"]}')
        if decision == 'keep':
            continue
        if decision == 'delete':
            if any(source['kind'] != 'deleted' for source in entry['sources']):
                raise ValueError('Delete is only valid for upstream deletions')
            content = None
        else:
            if not entry['merged']:
                raise ValueError('Accept needs a reviewed merged file')
            merged = (output / entry['merged']).resolve()
            if not merged.is_relative_to((output / 'merged').resolve()):
                raise ValueError('Merged file escaped staging directory')
            content = merged.read_bytes()
            if any(line.startswith((b'<<<<<<< ', b'=======', b'>>>>>>> ')) for line in content.splitlines()):
                raise ValueError('Resolve conflict markers before accepting')
        incoming_modes = {source.get('incomingMode') for source in entry['sources']} - {None}
        if decision == 'accept' and not incoming_modes <= {'100644', '100755'}:
            raise ValueError('Unsupported upstream file mode; adapt its mapping before accepting')
        source = entry['sources'][0]
        changed_mode = len(entry['sources']) == 1 and source.get('baseMode') != source.get('incomingMode')
        mode = (0o755 if incoming_modes == {'100755'} else 0o644) if changed_mode else (before_mode or 0o644)
        writes.append((target, before, content, before_mode, mode))
    lock = json.loads(LOCK.read_text())
    lock.update(commit=plan['commit'], sourceFiles=plan['sourceFiles'], sourceModes=plan['sourceModes'])
    if SOURCE == 'pstack':
        lock.update(pstackVersion=plan['versions']['pstack'], companionVersion=plan['versions']['cursor-team-kit'])
    else:
        lock['version'] = plan['versions']['mattpocock']
    # Reconcile tracked skill entries, including new upstream skills and removed-but-retained ports.
    mappings = {}
    for source in plan['sourceFiles']:
        if source.endswith('/SKILL.md') or '/agents/' in source and source.endswith('.md'):
            target, _ = target_for(source)
            if target and target.endswith('/SKILL.md') and len(target.split('/')) == 3:
                name = target.split('/')[1]
                source_dir = source.rsplit('/', 1)[0] if source.endswith('/SKILL.md') else source
                if name in mappings and mappings[name] != source_dir:
                    raise ValueError(f'Upstream skill name collision requires a mapping update: {name}')
                mappings[name] = source_dir
    lock['skills'] = [{'skill': name, 'source': source,
                       **({'stability': source.split('/')[1]} if SOURCE == 'mattpocock' else {})}
                      for name, source in sorted(mappings.items())]
    # Refuse an acknowledged update that leaves a newly required skill unported.
    future = {str(path.relative_to(ROOT)): content for path, _, content, _, _ in writes}
    for entry in lock['skills']:
        target = 'skills/' + entry['skill'] + '/SKILL.md'
        if target in future and future[target] is None or target not in future and not local_path(target).is_file():
            raise ValueError(f'Required upstream skill is missing: {entry["skill"]}')
    journal_dir = ROOT / 'upstream/updates'
    if SOURCE != 'pstack':
        journal_dir = journal_dir / SOURCE
    journal_path = journal_dir / (plan['commit'] + '.json')
    if journal_path.exists():
        raise ValueError('An update receipt already exists for this commit')
    old_lock = LOCK.read_bytes()
    applied = []
    try:
        for target, before, content, before_mode, mode in writes:
            applied.append((target, before, before_mode))
            if content is None:
                target.unlink(missing_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
                target.chmod(mode)
        # Validate the actual migrated result before advancing the source baseline.
        for entry in lock['skills']:
            if not local_path('skills/' + entry['skill'] + '/SKILL.md').is_file():
                raise ValueError('Incomplete skill migration')
        write_json(LOCK, lock)
        checked = subprocess.run([sys.executable, str(ROOT / 'scripts/validate-skills.py')], capture_output=True)
        if checked.returncode:
            raise ValueError('Port validation failed; changes rolled back. Review staged content and run the validator.')
        journal_dir.mkdir(parents=True, exist_ok=True)
        write_json(journal_path, {'source': SOURCE, 'baseCommit': plan['baseCommit'], 'commit': plan['commit'],
                                  'decisions': [{k: entry[k] for k in ['target', 'sources', 'decision', 'reason']} for entry in plan['entries']]})
    except BaseException:
        LOCK.write_bytes(old_lock)
        for target, before, before_mode in reversed(applied):
            if before is None:
                target.unlink(missing_ok=True)
            else:
                target.write_bytes(before)
                target.chmod(before_mode)
        raise
    print(json.dumps({'commit': plan['commit'], 'updatedFiles': len(writes), 'receipt': str(journal_path.relative_to(ROOT))}))


def apply(output):
    # Keep machine-local locking outside the repository, including during CI and tests.
    identity = hashlib.sha256(str(ROOT.resolve()).encode()).hexdigest()[:24]
    lockdir = Path(tempfile.gettempdir()) / ('pstack-upstream-apply-' + identity)
    try:
        lockdir.mkdir(mode=0o700)
    except FileExistsError:
        raise ValueError(f'Another update owns {lockdir}; inspect an interrupted update before removing a stale lock') from None
    try:
        _apply(output)
    finally:
        lockdir.rmdir()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    for action in ['check', 'stage']:
        command = sub.add_parser(action)
        command.add_argument('--source', choices=['pstack', 'mattpocock'], default='pstack')
        command.add_argument('--checkout', required=True, type=Path)
        command.add_argument('--ref', default='origin/main')
        command.add_argument('--fail-if-changed', action='store_true', help='exit 3 when updates are available')
        command.add_argument('--fetch', action='store_true', help='fetch origin before comparing')
        if action == 'stage':
            command.add_argument('--output', required=True, type=Path)
    apply_command = sub.add_parser('apply')
    apply_command.add_argument('--stage', required=True, type=Path)
    apply_command.add_argument('--source', choices=['pstack', 'mattpocock'], default='pstack')
    args = parser.parse_args()
    select_source(args.source)
    if args.action == 'apply':
        apply(args.stage.expanduser().resolve())
        return
    checkout = args.checkout.expanduser().resolve()
    if args.fetch:
        git(checkout, 'fetch', 'origin')
    if args.action == 'stage':
        stage(checkout, args.ref, args.output.expanduser().resolve())
    else:
        lock, commit, _, changes = compare(checkout, args.ref)
        print(json.dumps({'baseCommit': lock['commit'], 'commit': commit, 'changes': changes}, indent=2))
        if args.fail_if_changed and changes:
            sys.exit(3)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError, KeyError) as exc:
        print(f'{type(exc).__name__}: {exc}', file=sys.stderr)
        sys.exit(1)
