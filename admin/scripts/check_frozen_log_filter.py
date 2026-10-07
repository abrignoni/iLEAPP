"""Run a built iLEAPP over JSON logs and verify its compiled filter is bundled.

Usage: python admin/scripts/check_frozen_log_filter.py path/to/ileapp
For a source check, pass: python3 ileapp.py
"""
import json
from contextlib import closing
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.log_filter import ahocorasick  # pylint: disable=wrong-import-position


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    command = sys.argv[1:]
    messages = ['Take screenshot', 'TAKE SCREENSHOT', 'unrelated', 'Take screenshot']
    with tempfile.TemporaryDirectory(prefix='ileapp-filter-smoke-') as tmp:
        root = Path(tmp)
        evidence, output = root / 'input', root / 'output'
        evidence.mkdir()
        output.mkdir()
        records = [{'timestamp': '2026-10-07T12:00:00+00:00', 'eventMessage': message}
                   for message in messages]
        (evidence / 'logarchive.json').write_text(json.dumps(records), encoding='utf-8')
        profile = root / 'logarchive.ilprofile'
        profile.write_text(json.dumps({'leapp': 'ileapp', 'format_version': 1,
                                       'plugins': ['logarchive']}), encoding='utf-8')
        result = subprocess.run(command + ['-t', 'fs', '-i', str(evidence), '-o', str(output),
                                '-m', str(profile), '--custom_output_folder', 'filter-smoke'],
                                capture_output=True, text=True, encoding='utf-8',
                                errors='replace', timeout=120, check=False)
        if result.returncode:
            raise AssertionError(result.stdout[-4000:] + result.stderr[-2000:])
        mode = ('compiled multi-pattern prefilter' if ahocorasick is not None
                else 'SQLite fallback (compiled matcher unavailable)')
        assert mode in result.stdout, result.stdout[-4000:]
        report = output / 'filter-smoke'
        assert (report / 'index.html').is_file()
        with closing(sqlite3.connect(report / '_lava_artifacts.db')) as db:
            assert db.execute('SELECT count(*) FROM logarchive').fetchone()[0] == 4
            selected = db.execute('SELECT event_message FROM logarchive_artifacts '
                                  'ORDER BY rowid').fetchall()
            assert selected == [(message,) for message in messages if message != 'unrelated']
        assert 'Artifact had errors' not in result.stdout, result.stdout[-4000:]
        print(f'PASS: built iLEAPP selects the expected rows using {mode}')


if __name__ == '__main__':
    main()
