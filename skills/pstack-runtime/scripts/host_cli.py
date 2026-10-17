"""Native, non-interactive CLI adapters. No permission bypass or guessed model IDs."""
from pathlib import Path


def command(agent, brief, *, model=None, executable=None, extra_args=()):
    binary = executable or agent
    brief = str(Path(brief).resolve())
    if agent == 'claude':
        argv = [binary, '-p', '--output-format', 'stream-json', '--verbose',
                '--no-session-persistence', '--permission-mode', 'dontAsk']
        if model:
            argv += ['--model', model]
        argv += list(extra_args)
        return argv, Path(brief).read_text()
    if agent == 'codex':
        argv = [binary, 'exec', '--ephemeral', '--sandbox', 'workspace-write',
                '--skip-git-repo-check', '--json']
        if model:
            argv += ['--model', model]
        return argv + list(extra_args) + ['-'], Path(brief).read_text()
    if agent == 'opencode':
        argv = [binary, 'run', '--standalone', '--format', 'json']
        if model:
            argv += ['--model', model]
        return (argv + list(extra_args) + ['--file', brief,
                'Read the attached task brief and execute only its authorized scope.'], None)
    if agent == 'pi':
        argv = [binary, '--print', '--mode', 'json', '--no-session']
        if model:
            argv += ['--model', model]
        return argv + list(extra_args) + ['@' + brief], None
    raise ValueError(f'Unsupported agent: {agent}')


def terminal_failure(agent, log):
    """Recognize native terminal errors even if a CLI exits zero; never inspect prose claims."""
    import json
    with open(log, encoding='utf-8', errors='replace') as stream:
        for line in stream:
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if not isinstance(record, dict):
                continue
            if agent == 'codex' and record.get('type') == 'turn.failed':
                return True
            if agent == 'claude' and record.get('type') == 'result' and record.get('is_error'):
                return True
            if agent == 'opencode' and record.get('type') == 'error':
                return True
            if agent == 'pi' and record.get('type') == 'message_end':
                message = record.get('message', {})
                if message.get('role') == 'assistant' and message.get('stopReason') in ['error', 'aborted']:
                    return True
    return False
