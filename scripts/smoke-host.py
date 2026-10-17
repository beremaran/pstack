#!/usr/bin/env python3
"""Prepare or independently verify a disposable native-host TDD workflow fixture."""
import argparse
import importlib.util
import json
import re
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SENTINEL = 'This file belongs to the user. Leave it unchanged.\n'


def prepare(agent, output, skill='tdd'):
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', skill) or not (ROOT / 'skills' / skill / 'SKILL.md').is_file():
        raise ValueError('Choose an existing canonical skill by name')
    if output.exists():
        raise ValueError('Use a fresh output directory')
    output.mkdir(parents=True, mode=0o700)
    project = output / 'project'
    subprocess.run([sys.executable, str(ROOT / 'scripts/install-skills.py'), '--agent', agent,
                    '--project', str(project)], check=True, capture_output=True)
    subprocess.run(['git', 'init', '-q', str(project)], check=True)
    (project / 'clamp.py').write_text('def clamp(value, ceiling):\n    return min(value, ceiling)\n')
    (project / 'KEEP.txt').write_text(SENTINEL)
    discovery = {'claude': '.claude/skills', 'codex': '.agents/skills',
                 'opencode': '.opencode/skills', 'pi': '.pi/skills'}[agent]
    brief = project / 'brief.md'
    brief.write_text(f'''Read {project / discovery / skill / 'SKILL.md'} and its pstack-runtime dependency.
Use that TDD workflow to fix clamp.py. The function must clamp a number into
0..ceiling inclusive; ceiling is nonnegative. Use standard-library unittest.
Write and run a failing regression test before editing production code, then
prove it passes. Preserve KEEP.txt. Work only in this project. Do not commit,
use network tools, inspect credentials, install packages, or delegate. Do not
modify the supervisor's done check or state. Report failing-before and passing-after evidence.
''')
    config = {'agent': agent, 'project': 'project', 'brief': 'project/brief.md',
              'check': [sys.executable, str(Path(__file__).resolve()), 'verify', '--project', str(project)],
              'maxAttempts': 1, 'maxSeconds': 300, 'iterationSeconds': 240}
    if agent == 'claude':
        config['extraArgs'] = ['--setting-sources', 'project', '--strict-mcp-config', '--mcp-config',
                               '{"mcpServers":{}}', '--tools', 'Read,Write,Edit,Bash,Skill',
                               '--allowedTools', 'Read,Write,Edit,Skill,Bash(python*)', '--max-budget-usd', '2']
    (output / 'config.json').write_text(json.dumps(config, indent=2) + '\n')
    print(json.dumps({'project': str(project), 'config': str(output / 'config.json'),
                      'state': str(project / '.pstack/smoke-state'),
                      'note': 'Preparation does not run a model. Review native permissions/configuration before running the supervisor.'}))


def transcript_evidence(path):
    failing = None
    changed = None
    read_skills = set()
    def text(value):
        return json.dumps(value, ensure_ascii=False)
    for index, line in enumerate(path.read_text().splitlines()):
        try:
            event = json.loads(line)
        except ValueError:
            continue
        kind = event.get('type')
        item = event.get('item', {})
        if kind == 'item.completed':  # Codex native events
            if item.get('type') == 'command_execution' and re.search(r'\b(cat|sed|head)\b', item.get('command', '')):
                read_skills.update(re.findall(r'([a-z0-9-]+)/SKILL\.md', item.get('command', '')))
            if item.get('type') == 'command_execution' and 'FAILED' in item.get('aggregated_output', ''):
                failing = index if failing is None else failing
            if item.get('type') == 'file_change' and any(Path(c['path']).name == 'clamp.py' for c in item.get('changes', [])):
                changed = index if changed is None else changed
        if kind == 'tool_execution_end':  # Pi native events
            if 'FAILED' in text(event.get('result', {})):
                failing = index if failing is None else failing
        if kind == 'tool_execution_start':
            args = event.get('args', {})
            if event.get('toolName') in ['edit', 'write'] and Path(args.get('path', '')).name == 'clamp.py':
                changed = index if changed is None else changed
            if event.get('toolName') == 'read' and str(args.get('path', '')).endswith('/SKILL.md'):
                read_skills.add(Path(args['path']).parent.name)
        if kind == 'tool_use':  # OpenCode native events
            part = event.get('part', {})
            state = part.get('state', {})
            if 'FAILED' in str(state.get('output', '')):
                failing = index if failing is None else failing
            inputs = state.get('input', {})
            if part.get('tool') in ['edit', 'write'] and Path(inputs.get('filePath', inputs.get('path', ''))).name == 'clamp.py':
                changed = index if changed is None else changed
        if kind == 'assistant':  # Claude native tool calls, not prose claims
            for part in event.get('message', {}).get('content', []):
                if part.get('type') == 'tool_use' and part.get('name') in ['Edit', 'Write']:
                    if Path(part.get('input', {}).get('file_path', '')).name == 'clamp.py':
                        changed = index if changed is None else changed
        if kind == 'user':
            for part in event.get('message', {}).get('content', []):
                if isinstance(part, dict) and part.get('type') == 'tool_result' and 'FAILED' in text(part.get('content', '')):
                    failing = index if failing is None else failing
    return {'failingTestEvent': failing, 'productionChangeEvent': changed,
            'failingBeforeProductionChange': failing is not None and changed is not None and failing < changed,
            'explicitSkillReads': sorted(read_skills)}


def verify(project, transcript):
    specification = importlib.util.spec_from_file_location('pstack_fixture', project / 'clamp.py')
    fixture = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(fixture)
    cases = [(value, ceiling) for ceiling in [0, 1, 10] for value in [-100, -1, 0, 1, 10, 100]]
    behavior = all(fixture.clamp(value, ceiling) == max(0, min(value, ceiling)) for value, ceiling in cases)
    sentinel = (project / 'KEEP.txt').read_text() == SENTINEL
    tests_exist = bool(list(project.glob('test*.py')))
    tests = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-v'], cwd=project, capture_output=True, text=True)
    summary = {'behavior': behavior, 'cases': len(cases), 'sentinelPreserved': sentinel,
               'testFileExists': tests_exist, 'unittestExit': tests.returncode}
    if transcript:
        summary['transcriptEvidence'] = transcript_evidence(transcript)
    passed = behavior and sentinel and tests_exist and tests.returncode == 0
    if transcript:
        passed = passed and summary['transcriptEvidence']['failingBeforeProductionChange']
    summary['passed'] = passed
    print(json.dumps(summary))
    return 0 if passed else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    create = sub.add_parser('prepare')
    create.add_argument('--agent', required=True, choices=['claude', 'codex', 'opencode', 'pi'])
    create.add_argument('--output', required=True, type=Path)
    create.add_argument('--skill', default='tdd', help='canonical TDD workflow to exercise')
    check = sub.add_parser('verify')
    check.add_argument('--project', required=True, type=Path)
    check.add_argument('--transcript', type=Path)
    args = parser.parse_args()
    if args.action == 'prepare':
        prepare(args.agent, args.output.expanduser().resolve(), args.skill)
        return 0
    return verify(args.project.expanduser().resolve(), args.transcript)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, ImportError, AttributeError) as error:
        print(f'{type(error).__name__}: {error}', file=sys.stderr)
        sys.exit(2)
