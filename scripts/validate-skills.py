#!/usr/bin/env python3
"""Validate canonical skills and bundled local Markdown links. Requires PyYAML."""
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote
try:
    import yaml
except ImportError:
    sys.exit('Install PyYAML in a development environment to run this validator.')

ROOT = Path(__file__).resolve().parents[1]
errors = []
skills = sorted((ROOT / 'skills').glob('*/SKILL.md'))
for path in skills:
    text = path.read_text()
    try:
        assert text.startswith('---\n'), 'missing YAML frontmatter'
        front = yaml.safe_load(text.split('---', 2)[1])
        name, description = front['name'], front['description']
        assert name == path.parent.name, 'name differs from directory'
        assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name), 'invalid name'
        assert len(name) <= 64, 'name exceeds 64 characters'
        assert isinstance(description, str) and 0 < len(description) <= 1024, 'invalid description'
        assert set(front) <= {'name', 'description', 'license', 'compatibility', 'metadata'}, 'host-specific frontmatter'
        if path.parent.name != 'pstack-runtime':
            assert '../pstack-runtime/SKILL.md' in text, 'missing runtime contract'
    except Exception as exc:
        errors.append(f'{path.relative_to(ROOT)}: {exc}')
for path in (ROOT / 'skills').rglob('*.md'):
    if {'node_modules', '__pycache__'} & set(path.parts):
        continue
    text = path.read_text()
    # Ignore fenced examples; placeholders in templates are intentional.
    text = re.sub(r'^```.*?^```[^\n]*', '', text, flags=re.M | re.S)
    for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)', text):
        target = target.strip().split(' "', 1)[0].strip('<>')
        if re.match(r'^[a-zA-Z][\w+.-]*:', target) or target.startswith('#'):
            continue
        target = unquote(target.split('#', 1)[0])
        if '<' in target or '{' in target:
            continue
        resolved = (path.parent / target).resolve()
        if not resolved.is_relative_to(ROOT / 'skills') or not resolved.exists():
            errors.append(f'{path.relative_to(ROOT)}: broken bundled link {target}')
    if re.search(r'\.cursor/|subagent_type|cloud_base_branch|api2\.cursor\.sh|SendToUser|update_state', text):
        errors.append(f'{path.relative_to(ROOT)}: unmigrated host API/path')
owners = {}
for lock_path in sorted((ROOT / 'upstream').glob('*-lock.json')):
    lock = json.loads(lock_path.read_text())
    for record in lock['skills']:
        name = record['skill']
        if name in owners:
            errors.append(f'Skill owned by multiple sources: {name}')
        owners[name] = lock_path.name
        if not (ROOT / 'skills' / name / 'SKILL.md').is_file():
            errors.append(f'Missing upstream skill: {name}')
try:
    manifests = {}
    for name in ['plugin.json', '.claude-plugin/plugin.json', '.claude-plugin/marketplace.json',
                 '.agents/plugins/marketplace.json', 'package.json', 'opencode.json']:
        manifests[name] = json.loads((ROOT / name).read_text())
    agent_plugin = manifests['plugin.json']
    claude_plugin = manifests['.claude-plugin/plugin.json']
    package = manifests['package.json']
    assert agent_plugin['$schema'] == 'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json', 'portable manifest schema'
    assert agent_plugin['name'] == claude_plugin['name'] == package['name'], 'manifest names differ'
    assert agent_plugin['version'] == claude_plugin['version'] == package['version'], 'manifest versions differ'
    claude_entry = manifests['.claude-plugin/marketplace.json']['plugins']
    codex_entry = manifests['.agents/plugins/marketplace.json']['plugins']
    assert len(claude_entry) == 1 and claude_entry[0]['name'] == claude_plugin['name'], 'Claude marketplace entry differs'
    assert len(codex_entry) == 1 and codex_entry[0]['name'] == agent_plugin['name'], 'Codex marketplace entry differs'
    assert claude_entry[0]['source'] == './', 'Claude plugin source must be the repository root'
    assert codex_entry[0]['source']['path'] == './', 'Codex plugin source must be the repository root'
    assert package['pi']['skills'] == ['./skills'], 'Pi package skills path'
    assert manifests['opencode.json']['skills'] == ['./skills'], 'OpenCode skills path'
except Exception as exc:
    errors.append(f'host manifests: {exc}')
if errors:
    print('\n'.join(errors), file=sys.stderr)
    sys.exit(1)
print(f'Validated {len(skills)} skills, bundled links, runtime references, dependency inventory, and host manifests.')
