#!/usr/bin/env python3
"""Copy the portable bundle without overwriting existing skill directories."""
import argparse
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
PROJECT_PATHS = {'claude': '.claude/skills', 'codex': '.agents/skills',
                 'opencode': '.opencode/skills', 'pi': '.pi/skills'}
USER_PATHS = {'claude': '.claude/skills', 'codex': '.agents/skills',
              'opencode': '.config/opencode/skills', 'pi': '.pi/agent/skills'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent', required=True, choices=PROJECT_PATHS)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument('--project', type=Path)
    scope.add_argument('--user', action='store_true')
    scope.add_argument('--dest', type=Path, help='override discovery directory (for staging)')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if args.dest:
        destination = args.dest.expanduser().absolute()
    elif args.user:
        destination = Path.home() / USER_PATHS[args.agent]
    else:
        destination = args.project.expanduser().absolute() / PROJECT_PATHS[args.agent]
    sources = sorted((ROOT / 'skills').iterdir())
    sources = [p for p in sources if (p / 'SKILL.md').is_file()]
    # Preflight all conflicts so an existing bundle is never partly replaced.
    conflicts = [destination / p.name for p in sources if os.path.lexists(destination / p.name)]
    if conflicts:
        print('Refusing existing paths; review updates in a fresh staging directory:', file=sys.stderr)
        print('\n'.join(str(p) for p in conflicts), file=sys.stderr)
        return 1
    if args.dry_run:
        print(f'Would copy {len(sources)} skills to {destination}')
        return 0
    created = []
    try:
        destination.mkdir(parents=True, exist_ok=True)
        for source in sources:
            target = destination / source.name
            # Claim the directory atomically; never merge into a concurrent install.
            target.mkdir()
            created.append(target)
            shutil.copytree(source, target, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns('node_modules', '__pycache__'))
        notices = destination / 'pstack-notices'
        if not os.path.lexists(notices):
            notices.mkdir()
            created.append(notices)
            for source in (ROOT / 'upstream').glob('*-LICENSE'):
                shutil.copy2(source, notices / source.name)
            for source in (ROOT / 'upstream').glob('*-lock.json'):
                shutil.copy2(source, notices / source.name)
    except Exception:
        for path in reversed(created):
            shutil.rmtree(path)
        raise
    print(f'Copied {len(sources)} skills to {destination}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
