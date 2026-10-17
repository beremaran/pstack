import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0, str(Path(__file__).parent))
from host_cli import command
import run


class SupervisorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='pstack-supervisor-')
        self.root = Path(self.temp.name)
        self.worker = self.root / 'worker'
        self.worker.write_text('#!' + sys.executable + '''
import os, pathlib, sys, time
p = pathlib.Path.cwd()
mode = (p / 'mode').read_text() if (p / 'mode').exists() else 'pass'
if mode == 'sleep': time.sleep(30)
if mode == 'error': sys.exit(3)
if mode == 'auth':
    print('{"type":"turn.failed","error":{"message":"authentication_failed"}}')
    sys.exit(0)
if mode == 'pass': (p / 'done').write_text('verified artifact')
print('worker report')
''')
        self.worker.chmod(0o700)
        (self.root / 'brief.md').write_text('Work only in this test project.')
        self.config = {'agent': 'codex', 'project': '.', 'brief': 'brief.md',
                       'executable': str(self.worker), 'maxAttempts': 2,
                       'maxSeconds': 10, 'iterationSeconds': 3,
                       'check': [sys.executable, '-c', 'from pathlib import Path; raise SystemExit(0 if Path("done").exists() else 1)']}
        self.path = self.root / 'config.json'
        self.state = self.root / 'state'
        self.write_config()

    def tearDown(self):
        self.temp.cleanup()

    def write_config(self):
        self.path.write_text(json.dumps(self.config))

    def test_cli_parent_model_alias_is_not_sent_as_an_invented_model_id(self):
        self.config['model'] = 'inherit-parent'
        self.write_config()
        with self.assertRaisesRegex(ValueError, 'cannot inherit'):
            run.run(self.path, self.state)
        self.assertFalse(self.state.exists())

    def test_each_adapter_passes_brief_without_shell_or_permission_bypass(self):
        for agent in ['claude', 'codex', 'opencode', 'pi']:
            argv, stdin = command(agent, self.root / 'brief.md')
            self.assertEqual(argv[0], agent)
            self.assertNotIn('--dangerously-skip-permissions', argv)
            self.assertNotIn('--dangerously-bypass-approvals-and-sandbox', argv)
            if agent in ['claude', 'codex']:
                self.assertEqual(stdin, 'Work only in this test project.')
            else:
                self.assertIsNone(stdin)
                self.assertTrue(any(str(self.root / 'brief.md') in arg for arg in argv))

    def test_independent_check_controls_success_on_last_allowed_attempt(self):
        self.config['maxAttempts'] = 1
        self.write_config()
        state = run.run(self.path, self.state)
        self.assertEqual(state['status'], 'passed')
        self.assertEqual(len(state['attempts']), 1)
        self.assertEqual(state['lastCheck']['exitCode'], 0)
        self.assertTrue((self.state / 'after-1.log').exists())
        self.assertEqual(self.state.stat().st_mode & 0o777, 0o700)
        self.assertEqual((self.state / 'agent-1.log').stat().st_mode & 0o777, 0o600)

    def test_resume_verifies_completed_last_worker_before_attempt_cap(self):
        self.config['maxAttempts'] = 1
        self.write_config()
        state = run.run(self.path, self.state)
        # Simulate interruption after worker completion but before the final check was saved.
        state['status'] = 'running'
        state['lastCheck'] = {'exitCode': 1}
        run.save(self.state, state)
        resumed = run.run(self.path, self.state)
        self.assertEqual(resumed['status'], 'passed')
        self.assertEqual(len(resumed['attempts']), 1)
        self.assertEqual(resumed['lastCheck']['exitCode'], 0)

    def test_already_done_spends_no_model_turn(self):
        (self.root / 'done').touch()
        state = run.run(self.path, self.state)
        self.assertEqual(state['status'], 'passed')
        self.assertEqual(state['attempts'], [])

    def test_worker_success_without_predicate_never_passes(self):
        (self.root / 'mode').write_text('no-artifact')
        state = run.run(self.path, self.state)
        self.assertEqual(state['status'], 'exhausted')
        self.assertEqual(len(state['attempts']), 2)
        resumed = run.run(self.path, self.state)
        self.assertEqual(resumed['attempts'], state['attempts'])

    def test_nonzero_worker_fails_without_retry(self):
        (self.root / 'mode').write_text('error')
        state = run.run(self.path, self.state)
        self.assertEqual(state['status'], 'agent-failed')
        self.assertEqual(len(state['attempts']), 1)
        self.assertEqual(state['attempts'][0]['exitCode'], 3)

    def test_native_terminal_error_with_zero_exit_stops_without_retry(self):
        (self.root / 'mode').write_text('auth')
        state = run.run(self.path, self.state)
        self.assertEqual(state['status'], 'agent-failed')
        self.assertEqual(len(state['attempts']), 1)
        self.assertTrue(state['attempts'][0]['nativeTerminalError'])

    def test_timeout_kills_child(self):
        self.config['iterationSeconds'] = 1
        self.write_config()
        (self.root / 'mode').write_text('sleep')
        started = time.monotonic()
        state = run.run(self.path, self.state)
        self.assertEqual(state['status'], 'agent-failed')
        self.assertEqual(state['attempts'][0]['status'], 'timeout')
        self.assertLess(time.monotonic() - started, 4)

    def test_large_brief_cannot_block_timeout_when_worker_ignores_stdin(self):
        self.config['iterationSeconds'] = 1
        self.write_config()
        (self.root / 'brief.md').write_text('Task instructions.\n' * 100000)
        (self.root / 'mode').write_text('sleep')
        started = time.monotonic()
        state = run.run(self.path, self.state)
        self.assertEqual(state['attempts'][0]['status'], 'timeout')
        self.assertLess(time.monotonic() - started, 4)

    def test_stop_ends_current_worker(self):
        (self.root / 'mode').write_text('sleep')
        def stop():
            while not (self.state / 'agent-1.log').exists(): time.sleep(.02)
            (self.state / 'stop').touch()
        thread = threading.Thread(target=stop)
        thread.start()
        state = run.run(self.path, self.state)
        thread.join(timeout=2)
        self.assertEqual(state['status'], 'stopped')
        self.assertEqual(state['attempts'][0]['status'], 'stopped')

    def test_config_and_brief_changes_cannot_reset_existing_budgets(self):
        (self.root / 'mode').write_text('no-artifact')
        run.run(self.path, self.state)
        self.config['maxAttempts'] = 20
        self.write_config()
        with self.assertRaisesRegex(ValueError, 'changed'):
            run.run(self.path, self.state)

    def test_live_orphan_prevents_resume(self):
        (self.root / 'mode').write_text('no-artifact')
        run.run(self.path, self.state)
        state = json.loads((self.state / 'state.json').read_text())
        state['activePid'] = os.getpid()
        run.save(self.state, state)
        with self.assertRaisesRegex(ValueError, 'still alive'):
            run.run(self.path, self.state)

    def test_checker_timeout_is_not_a_task_failure_retry(self):
        self.config.update(iterationSeconds=1, check=[sys.executable, '-c', 'import time; time.sleep(10)'])
        self.write_config()
        state = run.run(self.path, self.state)
        self.assertEqual(state['status'], 'check-timeout')
        self.assertEqual(state['attempts'], [])

    def test_concurrent_supervisor_is_rejected(self):
        import fcntl
        self.state.mkdir()
        with open(self.state / 'lock', 'a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaisesRegex(ValueError, 'Another supervisor'):
                run.run(self.path, self.state)


if __name__ == '__main__':
    unittest.main()
