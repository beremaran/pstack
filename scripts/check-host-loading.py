#!/usr/bin/env python3
"""Check native skill inventories without asking a model to perform work."""
import argparse
import base64
import json
import os
from pathlib import Path
import queue
import secrets
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {p.parent.name for p in (ROOT / 'skills').glob('*/SKILL.md')}


def stop(process):
    if process.poll() is None:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()


def records(process):
    messages = queue.Queue()
    def read():
        for line in process.stdout:
            try:
                messages.put(json.loads(line))
            except ValueError:
                pass
        messages.put(None)
    threading.Thread(target=read, daemon=True).start()
    return messages


def response(messages, request_id, timeout=20):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            item = messages.get(timeout=max(.01, deadline - time.monotonic()))
        except queue.Empty:
            break
        if item is None:
            raise ValueError('Host exited before returning the inventory')
        if item.get('id') == request_id:
            return item
    raise ValueError('Host inventory request timed out')


def send(process, value):
    process.stdin.write(json.dumps(value) + '\n')
    process.stdin.flush()


def codex(project, temp):
    env = {**os.environ, 'CODEX_HOME': str(temp / 'codex-home')}
    Path(env['CODEX_HOME']).mkdir(mode=0o700)
    with open(temp / 'codex-stderr.log', 'w') as error:
        process = subprocess.Popen(['codex', 'app-server', '--stdio'], cwd=project, env=env,
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=error,
                                   text=True, start_new_session=True)
        messages = records(process)
        try:
            send(process, {'id': 1, 'method': 'initialize', 'params': {'clientInfo': {'name': 'pstack-loader-check', 'version': '1'}}})
            if 'result' not in response(messages, 1):
                raise ValueError('Codex initialization failed')
            send(process, {'method': 'initialized'})
            send(process, {'id': 2, 'method': 'skills/list', 'params': {'cwds': [str(project)], 'forceReload': True}})
            result = response(messages, 2)['result']['data'][0]
            if result.get('errors'):
                raise ValueError('Codex reported skill loading errors')
            return {skill['name'] for skill in result['skills'] if str(project) + '/' in skill['path']}
        finally:
            stop(process)


def pi(project, temp):
    env = {**os.environ, 'PI_CODING_AGENT_DIR': str(temp / 'pi-home'), 'PI_OFFLINE': '1', 'PI_TELEMETRY': '0'}
    with open(temp / 'pi-stderr.log', 'w') as error:
        process = subprocess.Popen(['pi', '--mode', 'rpc', '--no-session', '--offline', '--no-extensions',
                                    '--no-mcp', '--no-prompt-templates', '--no-themes', '--approve'],
                                   cwd=project, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=error, text=True, start_new_session=True)
        messages = records(process)
        try:
            send(process, {'id': 'inventory', 'type': 'get_commands'})
            result = response(messages, 'inventory')
            if not result.get('success'):
                raise ValueError('Pi command inventory failed')
            data = result['data']
            commands = data['commands'] if isinstance(data, dict) else data
            return {command['name'].removeprefix('skill:') for command in commands
                    if command.get('source') == 'skill' or command['name'].startswith('skill:')}
        finally:
            stop(process)


def opencode(project, temp):
    env = {**os.environ, **{key: str(temp / part) for key, part in
                           [('XDG_DATA_HOME', 'data'), ('XDG_STATE_HOME', 'state'),
                            ('XDG_CACHE_HOME', 'cache'), ('XDG_CONFIG_HOME', 'config')]}}
    password = secrets.token_urlsafe(24)
    env['OPENCODE_SERVER_PASSWORD'] = password
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    authorization = 'Basic ' + base64.b64encode(('opencode:' + password).encode()).decode()
    def request(route, timeout):
        query = urllib.parse.urlencode({'location[directory]': str(project)})
        req = urllib.request.Request(f'http://127.0.0.1:{port}{route}?{query}', headers={'Authorization': authorization})
        with urllib.request.urlopen(req, timeout=timeout) as stream:
            return json.load(stream)
    with open(temp / 'opencode-server.log', 'w') as output:
        os.chmod(output.name, 0o600)
        process = subprocess.Popen(['opencode', 'serve', '--hostname', '127.0.0.1', '--port', str(port)],
                                   cwd=project, env=env, stdout=output, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            deadline = time.monotonic() + 30
            while True:
                try:
                    # Unlike skill.list, this read-only endpoint waits for plugin activation.
                    request('/api/integration', 3)
                    data = request('/api/skill', 3)['data']
                    return {skill['name'] for skill in data if str(project) + '/' in skill['path']}
                except urllib.error.HTTPError as error:
                    if error.code in (401, 403):
                        raise ValueError('OpenCode server authentication failed') from None
                    if time.monotonic() >= deadline:
                        raise ValueError('OpenCode plugin activation failed') from None
                except (urllib.error.URLError, TimeoutError, ConnectionError):
                    if process.poll() is not None or time.monotonic() >= deadline:
                        raise ValueError('OpenCode server did not become ready') from None
                time.sleep(.1)
        finally:
            stop(process)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent', required=True, choices=['codex', 'pi', 'opencode', 'claude'])
    parser.add_argument('--claude-init', type=Path, help='existing stream-json startup transcript; no model request is sent')
    args = parser.parse_args()
    if args.agent == 'claude':
        if not args.claude_init:
            parser.error('Claude requires --claude-init from an authorized native session')
        found = None
        for line in args.claude_init.read_text().splitlines():
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if record.get('type') == 'system' and record.get('subtype') == 'init':
                found = {name.removeprefix('pstack:') for name in record.get('skills', [])}
                break
        if found is None:
            raise ValueError('No Claude system/init inventory in transcript')
    else:
        with tempfile.TemporaryDirectory(prefix='pstack-loader-') as directory:
            temp = Path(directory)
            project = temp / 'project'
            subprocess.run([sys.executable, str(ROOT / 'scripts/install-skills.py'), '--agent', args.agent,
                            '--project', str(project)], check=True, capture_output=True)
            subprocess.run(['git', 'init', '-q', str(project)], check=True)
            found = globals()[args.agent](project, temp)
    missing = sorted(EXPECTED - found)
    print(json.dumps({'agent': args.agent, 'expected': len(EXPECTED), 'found': len(EXPECTED & found), 'missing': missing}))
    return 1 if missing else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        print(f'{type(error).__name__}: {error}', file=sys.stderr)
        sys.exit(2)
