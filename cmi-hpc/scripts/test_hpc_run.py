"""Run the remote script `hpc_run.py` builds under local bash, with a stand-in for sbatch."""
import importlib.util
from pathlib import Path
import shlex
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('hpc_run', ROOT / "hpc_run.py")
hpc_run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hpc_run)


@pytest.mark.parametrize('path', ['../x', 'results/../../x', '/etc/x', '//server/share/x',
                                  'C:/x', 'results\\x', ''])
def test_fetch_rejects_paths_outside_the_run_directory(path):
    with pytest.raises(SystemExit, match='relative path inside the run directory'):
        hpc_run.check_fetch_paths([path])


def test_fetch_accepts_run_relative_paths():
    hpc_run.check_fetch_paths(['results/halo_error_49339/halo_error.json', 'logs/49339.out'])


def test_record_appends_submissions_including_unknown_ones(tmp_path):
    path = tmp_path / 'hpc_job_history'
    hpc_run.record(path, '4242', 'run-1', 'run-1:smoke:120000', ['job/a.sh', '-k', 'a and b'])
    hpc_run.record(path, 'submission_unknown', 'run-1', 'run-1:smoke:120100', ['job/a.sh'])

    first, second = path.read_text(encoding='utf-8').splitlines()
    assert first.split(' ', 1)[1] == "4242 run-1 run-1:smoke:120000 job/a.sh -k 'a and b'"
    assert second.split(' ', 1)[1] == 'submission_unknown run-1 run-1:smoke:120100 job/a.sh'


def test_git_env_points_windows_git_at_a_wsl_worktree(tmp_path):
    (tmp_path / '.git').write_text('gitdir: /mnt/c/Users/me/repo/.git/worktrees/wt\n')
    env = hpc_run.git_env(tmp_path, windows=True, base={'PATH': 'p'})
    assert env['GIT_DIR'] == 'C:\\Users\\me\\repo\\.git\\worktrees\\wt'
    assert env['GIT_WORK_TREE'] == str(tmp_path)
    assert env['PATH'] == 'p'


@pytest.mark.parametrize('gitfile, windows, base', [
    ('gitdir: C:/Users/me/repo/.git/worktrees/wt\n', True, {}),  # Windows-made worktree
    ('gitdir: /mnt/c/Users/me/repo/.git/worktrees/wt\n', False, {}),  # running inside WSL
    ('gitdir: /mnt/c/Users/me/repo/.git/worktrees/wt\n', True, {'GIT_DIR': 'mine'}),
    (None, True, {}),  # main checkout: .git is a directory
])
def test_git_env_leaves_other_checkouts_alone(tmp_path, gitfile, windows, base):
    if gitfile is None:
        (tmp_path / '.git').mkdir()
    else:
        (tmp_path / '.git').write_text(gitfile)
    assert hpc_run.git_env(tmp_path, windows=windows, base=base) == base


def test_recent_duplicates_matches_same_command_within_a_day(tmp_path):
    path = tmp_path / 'hpc_job_history'
    argv = ['job/a.sh', '--pdb_id', '6l3r_E']
    path.write_text(
        "2026-10-25T14:55:01Z 51893 run-0 run-0:smoke:145500 job/a.sh --pdb_id 6l3r_E\n"
        "2026-10-25T15:00:00Z 51894 run-0 run-0:smoke:150000 job/a.sh --pdb_id 6lrd_A\n"
        "2026-10-23T15:00:00Z 51000 run-9 run-9:smoke:150000 job/a.sh --pdb_id 6l3r_E\n",
        encoding='utf-8')
    now = hpc_run.datetime.datetime(2026, 10, 25, 15, 19, tzinfo=hpc_run.datetime.timezone.utc)
    hits = hpc_run.recent_duplicates(path, argv, now)
    assert [line.split()[1] for line in hits] == ['51893']
    assert hpc_run.recent_duplicates(tmp_path / 'missing', argv, now) == []


def test_submit_refuses_a_recent_duplicate_without_force(tmp_path, monkeypatch, capsys):
    path = tmp_path / 'hpc_job_history'
    hpc_run.record(path, '51893', 'run-0', 'run-0:smoke:145500', ['job/a.sh', '-x'])
    monkeypatch.setattr(hpc_run, 'ledger_path', lambda: path)
    def upload(tag):
        raise AssertionError('must stop before uploading')
    monkeypatch.setattr(hpc_run, 'upload', upload)
    with pytest.raises(SystemExit) as exc:
        hpc_run.main(['submit', 'job/a.sh', '-x'])
    assert exc.value.code == 3
    assert '51893' in capsys.readouterr().out
    monkeypatch.setattr(hpc_run, 'upload', lambda tag: 'run-1')
    monkeypatch.setattr(hpc_run, 'remote', lambda *a, **k: subprocess.CompletedProcess([], 0, 'JOB=7\n', ''))
    hpc_run.main(['submit', '--force', 'job/a.sh', '-x'])
    assert 'job_id=7' in capsys.readouterr().out


@pytest.mark.skipif(shutil.which('bash') is None, reason='needs bash')
def test_submit_records_arguments_literally(tmp_path):
    run = tmp_path / 'run'
    (run / 'src').mkdir(parents=True)
    bin_dir = tmp_path / 'bin'
    bin_dir.mkdir()
    sbatch = bin_dir / 'sbatch'
    sbatch.write_text('#!/bin/sh\necho "4242;cluster"\n')
    sbatch.chmod(0o755)
    marker = tmp_path / 'expanded'
    argv = ['job/submit_pytest.sh', '-k', 'a and b', f'$(touch {marker})', '${X:?boom}']
    comment = 'run-1:smoke:120000'

    script = hpc_run.submit_script(str(run), comment, ['K=v w'], ['--time=00:05:00'], argv)
    r = subprocess.run(['bash', '-s'], input=script, capture_output=True, text=True,
                       env={'PATH': f'{bin_dir}:/usr/bin:/bin'})

    assert r.returncode == 0, r.stderr
    assert 'JOB=4242' in r.stdout
    assert not marker.exists()
    assert (run / 'job_history').read_text() == f'4242 {comment} {shlex.join(argv)}\n'


@pytest.mark.parametrize('requested', [None, 7])
def test_exec_normalizes_script_and_forwards_result(tmp_path, monkeypatch, capsys, requested):
    script = tmp_path / 'query.sh'
    script.write_bytes(b'echo co\runt\r\n')

    def remote(payload, timeout):
        assert payload == b'echo count\n'
        assert timeout == (120 if requested is None else requested)
        return subprocess.CompletedProcess([], 3, 'results\n', 'warning\n')

    monkeypatch.setattr(hpc_run, 'remote', remote)
    argv = ['exec', str(script)] + ([] if requested is None else ['--timeout', str(requested)])
    with pytest.raises(SystemExit) as exc:
        hpc_run.main(argv)
    assert exc.value.code == 3
    captured = capsys.readouterr()
    assert captured.out == 'results\n'
    assert captured.err == 'warning\n'


def test_exec_timeout_exits_124(tmp_path, monkeypatch, capsys):
    script = tmp_path / 'query.sh'
    script.write_bytes(b'true\n')

    def remote(payload, timeout):
        raise subprocess.TimeoutExpired('ssh', timeout)

    monkeypatch.setattr(hpc_run, 'remote', remote)
    with pytest.raises(SystemExit) as exc:
        hpc_run.main(['exec', str(script), '--timeout', '7'])
    assert exc.value.code == 124
    captured = capsys.readouterr()
    assert captured.out == ''
    assert '7' in captured.err and len(captured.err.splitlines()) == 1
