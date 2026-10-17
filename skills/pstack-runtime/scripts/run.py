#!/usr/bin/env python3
"""Supervise bounded native-agent iterations with durable state and real checks."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
import time

from host_cli import command, terminal_failure


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def save(directory, state):
    temporary = directory / 'state.tmp'
    temporary.write_text(json.dumps(state, indent=2) + '\n')
    os.chmod(temporary, 0o600)
    temporary.replace(directory / 'state.json')


def load_config(path):
    config = json.loads(path.read_text())
    for key in ['project', 'brief', 'check', 'maxAttempts', 'maxSeconds', 'iterationSeconds']:
        if key not in config:
            raise ValueError(f'Missing configuration field: {key}')
    for key in ['maxAttempts', 'maxSeconds', 'iterationSeconds']:
        if type(config[key]) is not int or config[key] < 1:
            raise ValueError(f'{key} must be a positive integer')
    if not isinstance(config['check'], list) or not config['check'] or not all(isinstance(x, str) for x in config['check']):
        raise ValueError('check must be a nonempty argv array, without a shell')
    for key in ['model', 'executable']:
        if config.get(key) is not None and (not isinstance(config[key], str) or not config[key]):
            raise ValueError(f'{key} must be a nonempty string when supplied')
    if config.get('model') in ['auto', 'inherit-parent']:
        raise ValueError('A CLI cannot inherit the parent model; omit model for its default or supply a confirmed model identifier')
    for key in ['project', 'brief']:
        if not isinstance(config[key], str) or not config[key]:
            raise ValueError(f'{key} must be a nonempty path string')
        value = Path(config[key]).expanduser()
        config[key] = str((path.parent / value).resolve() if not value.is_absolute() else value.resolve())
    if not Path(config['project']).is_dir() or not Path(config['brief']).is_file():
        raise ValueError('project and brief must already exist')
    if config.get('agent') not in ['claude', 'codex', 'opencode', 'pi']:
        raise ValueError('agent must be claude, codex, opencode, or pi')
    if not isinstance(config.get('extraArgs', []), list) or not all(isinstance(x, str) for x in config.get('extraArgs', [])):
        raise ValueError('extraArgs must be an argv array')
    interval = config.get('intervalSeconds', 0)
    if type(interval) not in (int, float) or not math.isfinite(interval) or interval < 0:
        raise ValueError('intervalSeconds must be nonnegative')
    return config


def execute(argv, cwd, log, timeout, state_dir, stdin=None, on_start=None):
    """Stop the process group on timeout/stop. Return status without exposing its output."""
    writer = None
    with open(log, 'wb') as output:
        os.chmod(log, 0o600)
        process = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                                   stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            if on_start:
                on_start(process.pid)
            deadline = time.monotonic() + timeout
            writer = None
            if stdin is not None:
                def feed():
                    try:
                        process.stdin.write(stdin.encode())
                    except (BrokenPipeError, OSError):
                        pass
                    finally:
                        try:
                            process.stdin.close()
                        except (BrokenPipeError, OSError):
                            pass
                writer = threading.Thread(target=feed, daemon=True)
                writer.start()
            while process.poll() is None:
                if (state_dir / 'stop').exists() or time.monotonic() >= deadline:
                    reason = 'stopped' if (state_dir / 'stop').exists() else 'timeout'
                    terminate(process)
                    return {'status': reason, 'exitCode': process.returncode}
                time.sleep(0.1)
            return {'status': 'exited', 'exitCode': process.returncode}
        finally:
            if process.poll() is None:
                terminate(process)
            if writer:
                writer.join(timeout=1)


def terminate(process):
    try:
        os.killpg(process.pid, signal.SIGTERM)
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()
    except ProcessLookupError:
        pass


def run(config_path, state_dir):
    config = load_config(config_path)
    # Include the actual brief in identity: changing instructions requires a fresh state directory.
    identity = hashlib.sha256((json.dumps(config, sort_keys=True) + Path(config['brief']).read_text()).encode()).hexdigest()
    state_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(state_dir, 0o700)
    # OS lock is released after a crash; no stale pid file can unlock another live supervisor.
    import fcntl
    lock = open(state_dir / 'lock', 'a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock.close()
        raise ValueError('Another supervisor owns this state directory')
    try:
        state_path = state_dir / 'state.json'
        if state_path.exists():
            state = json.loads(state_path.read_text())
            if state['configHash'] != identity:
                raise ValueError('Configuration or brief changed; use a fresh state directory')
            if state.get('activePid'):
                try:
                    os.kill(state['activePid'], 0)
                except ProcessLookupError:
                    pass
                else:
                    raise ValueError('A process from the interrupted run is still alive; inspect it before resuming')
            if state['status'] == 'passed':
                return state
        else:
            state = {'configHash': identity, 'agent': config['agent'], 'project': config['project'],
                     'requestedModel': config.get('model') or 'cli-default',
                     'startedAt': timestamp(), 'deadline': time.time() + config['maxSeconds'],
                     'attempts': [], 'status': 'ready'}
        def on_start(pid):
            state['activePid'] = pid
            save(state_dir, state)

        # Resume never resets budgets. An interrupted attempt remains visible and consumes a seat.
        for attempt in state['attempts']:
            if attempt['status'] == 'running':
                attempt['status'] = 'interrupted'
        save(state_dir, state)
        while True:
            remaining = state['deadline'] - time.time()
            if (state_dir / 'stop').exists():
                state['status'] = 'stopped'
                break
            if remaining <= 0:
                state['status'] = 'exhausted'
                break
            # Check before spending another model turn. Only exit 0 means done.
            check_log = state_dir / f'check-{len(state["attempts"])}.log'
            check = execute(config['check'], config['project'], check_log,
                            min(remaining, config['iterationSeconds']), state_dir, on_start=on_start)
            state.pop('activePid', None)
            state['lastCheck'] = {**check, 'log': check_log.name, 'at': timestamp()}
            if check['status'] == 'exited' and check['exitCode'] == 0:
                state['status'] = 'passed'
                break
            if check['status'] != 'exited':
                state['status'] = 'stopped' if check['status'] == 'stopped' else 'check-timeout'
                break
            remaining = state['deadline'] - time.time()
            if remaining <= 0:
                state['status'] = 'exhausted'
                break
            if len(state['attempts']) >= config['maxAttempts']:
                state['status'] = 'exhausted'
                break
            number = len(state['attempts']) + 1
            # Fresh sessions receive the original brief plus a precise previous-check pointer.
            prompt = state_dir / f'brief-{number}.md'
            prompt.write_text(Path(config['brief']).read_text() +
                              f'\n\nSupervisor attempt {number}/{config["maxAttempts"]}. '
                              f'The done check failed. Its local output is at {check_log}. '
                              'Read that evidence and current project state before acting. '
                              'Do not change the done check or declare it passed without running it.\n')
            os.chmod(prompt, 0o600)
            argv, stdin = command(config['agent'], prompt, model=config.get('model'),
                                  executable=config.get('executable'), extra_args=config.get('extraArgs', []))
            attempt = {'number': number, 'status': 'running', 'startedAt': timestamp(),
                       'log': f'agent-{number}.log'}
            state['attempts'].append(attempt)
            state['status'] = 'running'
            save(state_dir, state)
            result = execute(argv, config['project'], state_dir / attempt['log'],
                             min(remaining, config['iterationSeconds']), state_dir, stdin, on_start)
            state.pop('activePid', None)
            attempt.update(result)
            attempt['finishedAt'] = timestamp()
            save(state_dir, state)
            attempt['nativeTerminalError'] = terminal_failure(config['agent'], state_dir / attempt['log'])
            if result['status'] != 'exited' or result['exitCode'] != 0 or attempt['nativeTerminalError']:
                # Auth, permissions, model, and runner failures are not retries of the task.
                state['status'] = 'stopped' if result['status'] == 'stopped' else 'agent-failed'
                break
            # Always check the result of the last allowed attempt before enforcing the seat cap.
            remaining = state['deadline'] - time.time()
            if remaining <= 0:
                state['status'] = 'exhausted'
                break
            check_log = state_dir / f'after-{number}.log'
            check = execute(config['check'], config['project'], check_log,
                            min(remaining, config['iterationSeconds']), state_dir, on_start=on_start)
            state.pop('activePid', None)
            state['lastCheck'] = {**check, 'log': check_log.name, 'at': timestamp()}
            if check['status'] == 'exited' and check['exitCode'] == 0:
                state['status'] = 'passed'
                break
            if check['status'] != 'exited':
                state['status'] = 'stopped' if check['status'] == 'stopped' else 'check-timeout'
                break
            save(state_dir, state)
            wait_until = min(time.time() + config.get('intervalSeconds', 0), state['deadline'])
            while time.time() < wait_until and not (state_dir / 'stop').exists():
                delay = wait_until - time.time()
                if delay <= 0:
                    break
                time.sleep(min(0.1, delay))
        state['updatedAt'] = timestamp()
        save(state_dir, state)
        return state
    finally:
        lock.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['run', 'status', 'stop'])
    parser.add_argument('--config', type=Path)
    parser.add_argument('--state', required=True, type=Path)
    args = parser.parse_args()
    directory = args.state.expanduser().resolve()
    if args.action == 'run':
        if args.config is None:
            parser.error('run requires --config')
        state = run(args.config.expanduser().resolve(), directory)
    elif args.action == 'status':
        state = json.loads((directory / 'state.json').read_text())
    else:
        if not (directory / 'state.json').is_file():
            parser.error('No run exists at --state')
        (directory / 'stop').touch(mode=0o600)
        state = {'status': 'stop-requested'}
    print(json.dumps(state))
    return 0 if state['status'] in ['passed', 'stop-requested'] or args.action == 'status' else 1


if __name__ == '__main__':
    def interrupt(signum, frame):
        raise SystemExit(128 + signum)
    signal.signal(signal.SIGTERM, interrupt)
    signal.signal(signal.SIGINT, interrupt)
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError) as exc:
        # Do not print config content, command output, or credentials on errors.
        print(f'{type(exc).__name__}: {exc}', file=sys.stderr)
        sys.exit(2)
