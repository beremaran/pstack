#!/usr/bin/env python3
"""Test update staging and review gates in an isolated synthetic upstream and port."""
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('upstream', Path(__file__).with_name('upstream.py'))
upstream = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(upstream)
REAL_ROOT = upstream.ROOT


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='pstack-update-')
        self.base = Path(self.temp.name)
        self.source = self.base / 'source'
        self.port = self.base / 'port'
        self.source.mkdir()
        self.port.mkdir()
        subprocess.run(['git', 'init', '-q', str(self.source)], check=True)
        self.run_git('config', 'user.name', 'Test')
        self.run_git('config', 'user.email', 'test@example.invalid')
        self.skill = '---\nname: demo\ndescription: Test an upstream update.\n---\n\n# Demo\n\nBaseline guidance.\n\nTail stays.\n'
        self.put('pstack/skills/demo/SKILL.md', self.skill)
        for pack in upstream.PACKS:
            self.put(pack + '/.cursor-plugin/plugin.json', '{"version":"1.0.0"}\n')
            self.put(pack + '/LICENSE', 'MIT fixture\n')
        self.old = self.commit('base')
        (self.port / 'skills/demo').mkdir(parents=True)
        (self.port / 'skills/demo/SKILL.md').write_text(self.skill.replace('# Demo', 'Read [pstack runtime](../pstack-runtime/SKILL.md).\n\n# Demo'))
        shutil.copytree(REAL_ROOT / 'skills/pstack-runtime', self.port / 'skills/pstack-runtime',
                        ignore=shutil.ignore_patterns('node_modules', '__pycache__'))
        (self.port / 'upstream').mkdir()
        (self.port / 'scripts').mkdir()
        shutil.copy2(REAL_ROOT / 'scripts/validate-skills.py', self.port / 'scripts/validate-skills.py')
        for name in ['plugin.json', '.claude-plugin/plugin.json', '.claude-plugin/marketplace.json',
                     '.agents/plugins/marketplace.json', 'package.json', 'opencode.json']:
            target = self.port / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REAL_ROOT / name, target)
        upstream.ROOT = self.port
        upstream.LOCK = self.port / 'upstream/pstack-lock.json'
        upstream.write_json(upstream.LOCK, {'repository':'fixture', 'commit':self.old,
                                           'sourceFiles':upstream.inventory(self.source, self.old),
                                           'skills':[{'skill':'demo','source':'pstack/skills/demo'}]})
        self.output = self.base / 'stage'

    def tearDown(self):
        upstream.ROOT = REAL_ROOT
        self.temp.cleanup()

    def run_git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.source), *args], text=True).strip()

    def put(self, name, content):
        p = self.source / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)

    def commit(self, message):
        self.run_git('add', '.')
        self.run_git('commit', '-qm', message)
        return self.run_git('rev-parse', 'HEAD')

    def stage(self):
        with redirect_stdout(io.StringIO()):
            upstream.stage(self.source, 'HEAD', self.output)
        return json.loads((self.output / 'plan.json').read_text())

    def decisions(self, plan, decision='accept'):
        for entry in plan['entries']:
            entry.update(decision=decision, reason='Reviewed against portable workflow requirements.')
        upstream.write_json(self.output / 'plan.json', plan)

    def apply(self):
        with redirect_stdout(io.StringIO()):
            upstream.apply(self.output)

    def test_unchanged_source_reports_no_changes(self):
        self.assertEqual(upstream.compare(self.source, 'HEAD')[3], [])

    def test_clean_three_way_merge_preserves_local_adaptation(self):
        self.put('pstack/skills/demo/SKILL.md', self.skill.replace('Baseline guidance.', 'Improved upstream guidance.'))
        new = self.commit('improve')
        plan = self.stage()
        self.assertEqual(plan['entries'][0]['status'], 'clean-merge')
        canonical = self.port / 'skills/demo/SKILL.md'
        self.assertNotIn('Improved upstream', canonical.read_text())
        self.decisions(plan)
        self.apply()
        self.assertIn('Improved upstream', canonical.read_text())
        self.assertIn('pstack-runtime', canonical.read_text())
        self.assertEqual(json.loads(upstream.LOCK.read_text())['commit'], new)
        self.assertTrue((self.port / 'upstream/updates' / (new + '.json')).is_file())

    def test_pending_review_cannot_modify_port_or_lock(self):
        self.put('pstack/skills/demo/SKILL.md', self.skill + '\nNew instruction.\n')
        self.commit('change')
        old_lock = upstream.LOCK.read_bytes()
        self.stage()
        with self.assertRaisesRegex(ValueError, 'decision'):
            self.apply()
        self.assertEqual(upstream.LOCK.read_bytes(), old_lock)

    def test_local_edit_after_staging_is_never_overwritten(self):
        self.put('pstack/skills/demo/SKILL.md', self.skill + '\nNew instruction.\n')
        self.commit('change')
        plan = self.stage()
        self.decisions(plan)
        target = self.port / 'skills/demo/SKILL.md'
        target.write_text('Later local work\n')
        with self.assertRaisesRegex(ValueError, 'Local file changed'):
            self.apply()
        self.assertEqual(target.read_text(), 'Later local work\n')

    def test_conflicts_must_be_resolved(self):
        target = self.port / 'skills/demo/SKILL.md'
        target.write_text(target.read_text().replace('Baseline guidance.', 'Our changed guidance.'))
        self.put('pstack/skills/demo/SKILL.md', self.skill.replace('Baseline guidance.', 'Other changed guidance.'))
        self.commit('conflict')
        plan = self.stage()
        self.assertEqual(plan['entries'][0]['status'], 'conflict')
        self.decisions(plan)
        with self.assertRaisesRegex(ValueError, 'conflict markers'):
            self.apply()

    def test_multiple_conflicts_keep_all_merge_markers(self):
        # Distant conflicting edits produce git merge-file exit 2, not an execution error.
        separator = ''.join(f'Unchanged line {n}.\n' for n in range(20))
        base = self.skill + '\nFirst choice.\n' + separator + 'Second choice.\n'
        self.put('pstack/skills/demo/SKILL.md', base)
        self.old = self.commit('two separated sections')
        lock = json.loads(upstream.LOCK.read_text())
        lock.update(commit=self.old, sourceFiles=upstream.inventory(self.source, self.old))
        upstream.write_json(upstream.LOCK, lock)
        target = self.port / 'skills/demo/SKILL.md'
        target.write_text(base.replace('First choice.', 'Our first choice.').replace('Second choice.', 'Our second choice.'))
        self.put('pstack/skills/demo/SKILL.md', base.replace('First choice.', 'Their first choice.').replace('Second choice.', 'Their second choice.'))
        self.commit('two upstream conflicts')
        plan = self.stage()
        entry = plan['entries'][0]
        self.assertEqual(entry['status'], 'conflict')
        merged = (self.output / entry['merged']).read_text()
        self.assertEqual(merged.count('<<<<<<< '), 2)
        self.assertIn('Their second choice.', merged)

    def test_nested_skill_example_remains_a_resource_not_a_canonical_skill(self):
        self.put('pstack/skills/demo/references/example/SKILL.md', '# Example workflow content\n')
        self.commit('add a bundled example')
        plan = self.stage()
        self.decisions(plan)
        self.apply()
        records = json.loads(upstream.LOCK.read_text())['skills']
        self.assertEqual(records, [{'skill': 'demo', 'source': 'pstack/skills/demo'}])
        self.assertTrue((self.port / 'skills/demo/references/example/SKILL.md').is_file())

    def test_invalid_migration_rolls_back_every_file_and_baseline(self):
        self.put('pstack/skills/demo/SKILL.md', self.skill.replace('name: demo', 'name: Wrong Name'))
        self.commit('invalid common frontmatter')
        before = (self.port / 'skills/demo/SKILL.md').read_bytes()
        old_lock = upstream.LOCK.read_bytes()
        plan = self.stage()
        self.decisions(plan)
        with self.assertRaisesRegex(ValueError, 'validation failed'):
            self.apply()
        self.assertEqual((self.port / 'skills/demo/SKILL.md').read_bytes(), before)
        self.assertEqual(upstream.LOCK.read_bytes(), old_lock)

    def test_new_skill_requires_port_and_validation(self):
        self.put('pstack/skills/new-skill/SKILL.md', self.skill.replace('name: demo', 'name: new-skill'))
        self.commit('add dependency')
        plan = self.stage()
        self.assertEqual(plan['entries'][0]['status'], 'new-needs-port')
        self.decisions(plan)
        with self.assertRaisesRegex(ValueError, 'validation failed'):
            self.apply()
        entry = plan['entries'][0]
        p = self.output / entry['merged']
        p.write_text(p.read_text() + '\nRead [pstack runtime](../pstack-runtime/SKILL.md).\n')
        self.apply()
        skills = json.loads(upstream.LOCK.read_text())['skills']
        self.assertIn('new-skill', [s['skill'] for s in skills])

    def test_upstream_deletion_preserves_local_port_when_explicitly_kept(self):
        (self.source / 'pstack/skills/demo/SKILL.md').unlink()
        self.commit('remove upstream skill')
        plan = self.stage()
        self.decisions(plan, 'keep')
        self.apply()
        self.assertTrue((self.port / 'skills/demo/SKILL.md').exists())

    def test_manifest_and_documentation_changes_require_review_too(self):
        self.put('pstack/README.md', 'Depends on another plugin now.\n')
        self.commit('new integration dependency in prose')
        plan = self.stage()
        self.assertIsNone(plan['entries'][0]['target'])
        self.decisions(plan)
        with self.assertRaisesRegex(ValueError, 'Unmapped'):
            self.apply()
        self.decisions(plan, 'keep')
        self.apply()

    def test_mode_only_updates_are_detected_and_preserve_executability(self):
        target = self.port / 'skills/demo/SKILL.md'
        (self.source / 'pstack/skills/demo/SKILL.md').chmod(0o755)
        self.commit('make helper executable')
        plan = self.stage()
        self.assertEqual(len(plan['entries']), 1)
        self.decisions(plan)
        self.apply()
        self.assertEqual(target.stat().st_mode & 0o777, 0o755)
        self.assertEqual(json.loads(upstream.LOCK.read_text())['sourceModes']['pstack/skills/demo/SKILL.md'], '100755')

    def test_concurrent_apply_is_rejected_without_changing_files(self):
        identity = hashlib.sha256(str(self.port.resolve()).encode()).hexdigest()[:24]
        lockdir = Path(tempfile.gettempdir()) / ('pstack-upstream-apply-' + identity)
        lockdir.mkdir()
        before = upstream.LOCK.read_bytes()
        try:
            with self.assertRaisesRegex(ValueError, 'Another update owns'):
                self.apply()
        finally:
            lockdir.rmdir()
        self.assertEqual(upstream.LOCK.read_bytes(), before)

    def test_stale_lock_rejected(self):
        self.put('pstack/README.md', 'Changed prose.\n')
        self.commit('docs')
        plan = self.stage()
        self.decisions(plan, 'keep')
        upstream.LOCK.write_text(upstream.LOCK.read_text() + '\n')
        with self.assertRaisesRegex(ValueError, 'lock changed'):
            self.apply()


if __name__ == '__main__':
    unittest.main()
