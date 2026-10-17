#!/usr/bin/env python3
"""Exercise staging, resource preservation, and conflict handling without host settings."""
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='pstack-install-') as temp:
    for agent, directory in [('claude', '.claude/skills'), ('codex', '.agents/skills'),
                             ('opencode', '.opencode/skills'), ('pi', '.pi/skills')]:
        project = Path(temp) / agent
        command = [sys.executable, str(ROOT / 'scripts/install-skills.py'),
                   '--agent', agent, '--project', str(project)]
        subprocess.run(command + ['--dry-run'], check=True, capture_output=True)
        assert not project.exists(), 'dry-run wrote to disk'
        subprocess.run(command, check=True)
        target = project / directory
        assert len(list(target.glob('*/SKILL.md'))) == len(list((ROOT / 'skills').glob('*/SKILL.md')))
        for source in (ROOT / 'skills').rglob('*'):
            if source.is_file() and not {'node_modules', '__pycache__'} & set(source.parts):
                assert source.read_bytes() == (target / source.relative_to(ROOT / 'skills')).read_bytes()
        marker = target / 'how/SKILL.md'
        marker.write_text('user-owned local change\n')
        blocked = subprocess.run(command, capture_output=True)
        assert blocked.returncode == 1, 'existing paths were accepted'
        assert marker.read_text() == 'user-owned local change\n', 'local edit was overwritten'
        assert (target / 'pstack-notices/pstack-LICENSE').is_file()
        for notice in (ROOT / 'upstream').glob('*-LICENSE'):
            assert (target / 'pstack-notices' / notice.name).read_bytes() == notice.read_bytes()
        for lock in (ROOT / 'upstream').glob('*-lock.json'):
            assert (target / 'pstack-notices' / lock.name).read_bytes() == lock.read_bytes()
        assert not list(target.rglob('node_modules')), 'runtime caches were copied'
        print(f'{agent}: dry-run, full resource copy, attribution, and overwrite refusal passed')
    # A dangling symlink is also a conflict, not an empty destination.
    project = Path(temp) / 'conflict'
    dest = project / '.agents/skills'
    dest.mkdir(parents=True)
    (dest / 'how').symlink_to(project / 'missing')
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/install-skills.py'),
                             '--agent', 'codex', '--project', str(project)], capture_output=True)
    assert result.returncode == 1 and (dest / 'how').is_symlink()
    assert list(dest.iterdir()) == [dest / 'how'], 'conflicting install partially wrote files'
print('All installer checks passed.')
