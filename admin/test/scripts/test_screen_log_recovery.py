"""HTML logging recovery and lifecycle. Author: @AlexisBrignoni, Codex."""
import errno
import importlib
import inspect
import io
from pathlib import Path
import queue
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
import unittest
from unittest.mock import Mock, patch

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from leapp_functions.app.screen_log import ScreenLogWriter  # pylint: disable=wrong-import-position
from scripts import ilapfuncs  # pylint: disable=wrong-import-position


class ScreenLogRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'Screen_Output.html'
        self.writer = ScreenLogWriter()
        self.addCleanup(self.writer.close)

    def test_session_uses_one_handle_with_immediately_visible_unicode_and_html(self):
        original = open
        handles = []

        def tracked_open(*args, **kwargs):
            handle = original(*args, **kwargs)
            handles.append(handle)
            return handle

        with patch('builtins.open', side_effect=tracked_open):
            with self.writer.session(self.path):
                for message in ['first<br>\n', '<b>é漢字</b><br>\n', '\n<br>\n']:
                    self.writer.write(self.path, message)
                self.assertEqual(self.path.read_text(), 'first<br>\n<b>é漢字</b><br>\n\n<br>\n')
                self.assertEqual(len(handles), 1)
                self.assertFalse(handles[0].closed)
            self.assertTrue(handles[0].closed)

    def test_failed_opens_replay_once_in_order_and_warn_once_per_outage(self):
        for code in [errno.EMFILE, errno.ENFILE]:
            self.writer.close()
            path = self.path.with_name(str(code) + '.html')
            with patch('sys.stdout', new_callable=io.StringIO) as output:
                with patch('builtins.open', side_effect=OSError(code, 'exhausted')):
                    self.writer.write(path, 'one<br>\n')
                    self.writer.write(path, 'two é<br>\n')
                self.assertEqual(output.getvalue().count('HTML log unavailable'), 1)
                self.writer.write(path, 'three<br>\n')
                self.writer.write(path, 'four<br>\n')
            self.assertEqual(path.read_text(), 'one<br>\ntwo é<br>\nthree<br>\nfour<br>\n')

    def test_close_retries_pending_messages_without_needing_another_log_call(self):
        with patch('builtins.open', side_effect=OSError(errno.EMFILE, 'exhausted')):
            self.writer.write(self.path, 'last message<br>\n')
        self.writer.close()
        self.writer.close()
        self.assertEqual(self.path.read_text(), 'last message<br>\n')

    def test_session_releases_handle_on_early_return_and_base_exception(self):
        for error in [RuntimeError('failed'), KeyboardInterrupt()]:
            handle = None
            with self.assertRaises(type(error)):
                with self.writer.session(self.path):
                    handle = self.writer._handle  # pylint: disable=protected-access
                    self.writer.write(self.path, 'before failure<br>\n')
                    raise error
            self.assertTrue(handle.closed)

    def test_nested_sessions_release_only_at_the_outer_exit(self):
        with self.writer.session(self.path):
            with self.writer.session(self.path):
                self.writer.write(self.path, 'nested<br>\n')
                handle = self.writer._handle  # pylint: disable=protected-access
            self.assertFalse(handle.closed)
        self.assertTrue(handle.closed)

    def test_short_write_and_exhaustion_replay_only_unwritten_suffix(self):
        destination = io.BytesIO()
        handle = Mock()
        fail = [False]

        def short_write(data):
            if fail[0]:
                fail[0] = False
                raise OSError(errno.EMFILE, 'exhausted during write')
            size = min(3, len(data))
            destination.write(data[:size])
            fail[0] = True
            return size

        handle.write.side_effect = short_write
        with patch('builtins.open', return_value=handle):
            with self.writer.session(self.path):
                self.writer.write(self.path, 'é first<br>\n')
                self.writer.write(self.path, 'second<br>\n')
                handle.write.side_effect = destination.write
            self.assertEqual(destination.getvalue().decode().replace('\r\n', '\n'), 'é first<br>\nsecond<br>\n')
            handle.close.assert_called_once()

    def test_buffer_bounds_recover_with_an_explicit_omission_notice_in_order(self):
        self.writer.MAX_PENDING_BYTES = 10
        self.writer.MAX_PENDING_MESSAGES = 2
        with patch('builtins.open', side_effect=OSError(errno.EMFILE, 'exhausted')):
            for message in ['one\n', 'two\n', 'three\n', 'four\n']:
                self.writer.write(self.path, message)
        self.writer.write(self.path, 'recovered\n')
        text = self.path.read_text()
        self.assertTrue(text.startswith('one\ntwo\nHTML log buffer full: 2 message(s) omitted;'))
        self.assertTrue(text.endswith('recovered\n'))
        self.assertNotIn('three', text)

    def test_large_healthy_message_is_not_subject_to_the_buffer_limit(self):
        self.writer.MAX_PENDING_BYTES = 10
        text = 'é' * 1000 + '<br>\n'
        self.writer.write(self.path, text)
        self.assertEqual(self.path.read_text(), text)

    def test_unresolved_close_reports_loss_without_leaking_into_the_next_run(self):
        with patch('sys.stdout', new_callable=io.StringIO) as output:
            with patch('builtins.open', side_effect=OSError(errno.EMFILE, 'exhausted')):
                self.writer.write(self.path, 'old report message<br>\n')
                self.writer.close()
            self.assertIn('1 buffered message(s) remain unwritten', output.getvalue())
        other = self.path.with_name('next.html')
        self.writer.write(other, 'new report message<br>\n')
        self.assertEqual(other.read_text(), 'new report message<br>\n')
        self.assertFalse(self.path.exists())

    def test_path_change_drains_the_old_report_before_switching(self):
        with patch('builtins.open', side_effect=OSError(errno.EMFILE, 'exhausted')):
            self.writer.write(self.path, 'old<br>\n')
        other = self.path.with_name('next.html')
        self.writer.write(other, 'new<br>\n')
        self.assertEqual(self.path.read_text(), 'old<br>\n')
        self.assertEqual(other.read_text(), 'new<br>\n')

    def test_unrelated_open_and_write_errors_still_raise_and_close(self):
        with patch('builtins.open', side_effect=PermissionError(errno.EACCES, 'denied')):
            with self.assertRaises(PermissionError):
                self.writer.write(self.path, 'message')
        handle = Mock()
        handle.write.side_effect = OSError(errno.ENOSPC, 'disk full')
        with patch('builtins.open', return_value=handle):
            with self.assertRaises(OSError) as caught:
                with self.writer.session(self.path):
                    self.writer.write(self.path, 'message')
        self.assertEqual(caught.exception.errno, errno.ENOSPC)
        handle.close.assert_called_once()

    def test_concurrent_messages_do_not_interleave_bytes_or_disappear(self):
        def write(number):
            self.writer.write(self.path, f'{number}:é漢字<br>\n')
        with self.writer.session(self.path):
            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(write, range(200)))
        self.assertCountEqual(self.path.read_text().splitlines(), [f'{n}:é漢字<br>' for n in range(200)])

    def test_windows_newline_translation_matches_the_previous_text_writer(self):
        with patch('leapp_functions.app.screen_log.os.linesep', '\r\n'):
            self.writer.write(self.path, 'one\ntwo<br>\n')
        self.assertEqual(self.path.read_bytes(), b'one\r\ntwo<br>\r\n')

    @unittest.skipIf(sys.platform == 'win32', 'RLIMIT_NOFILE is Unix-only')
    def test_real_descriptor_exhaustion_persistent_handle_recovery_and_shutdown(self):
        result = subprocess.run([sys.executable, '-B', __file__, '--descriptor-stress'],
                                cwd=REPO_ROOT, capture_output=True, text=True, timeout=30, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('persistent handle, ordered replay, and shutdown recovery: PASS', result.stdout)


class LoggingIntegrationTests(unittest.TestCase):
    def setUp(self):
        ilapfuncs.close_screen_log()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(ilapfuncs.close_screen_log)
        self.path = Path(self.temp.name) / 'Screen_Output.html'
        self.old_path = ilapfuncs.OutputParameters.screen_output_file_path
        self.addCleanup(setattr, ilapfuncs.OutputParameters, 'screen_output_file_path', self.old_path)
        ilapfuncs.OutputParameters.screen_output_file_path = str(self.path)

    def test_decorator_flushes_on_return_and_unhandled_failure(self):
        @ilapfuncs.screen_log_session
        def run(fail=False):
            ilapfuncs.logfunc('processing message')
            if fail:
                raise RuntimeError('failed')
            return 42
        with patch('sys.stdout', new_callable=io.StringIO):
            self.assertEqual(run(), 42)
            with self.assertRaises(RuntimeError):
                run(True)
        self.assertEqual(self.path.read_text(), 'processing message<br>\n' * 2)
        self.assertIsNone(ilapfuncs._screen_log._handle)  # pylint: disable=protected-access

    def test_console_and_worker_gui_receive_original_messages_once(self):
        messages = queue.Queue()
        with patch.object(ilapfuncs.GuiWindow, 'message_queue', messages):
            with patch('sys.stdout', new_callable=io.StringIO) as console:
                with patch.object(ilapfuncs, '_console_write', console.write):
                    with patch('builtins.open', side_effect=OSError(errno.EMFILE, 'exhausted')):
                        ilapfuncs.logfunc('during exhaustion')
                    ilapfuncs.logfunc('after recovery')
                self.assertEqual(console.getvalue().count('during exhaustion'), 1)
                self.assertEqual(console.getvalue().count('after recovery'), 1)
        queued = ''.join(item[1] for item in list(messages.queue))
        self.assertEqual(queued.count('during exhaustion'), 1)
        self.assertEqual(queued.count('after recovery'), 1)
        self.assertEqual(self.path.read_text(), 'during exhaustion<br>\nafter recovery<br>\n')

    def test_disabled_html_keeps_console_only_behavior_for_non_string_messages(self):
        ilapfuncs.OutputParameters.screen_output_file_path = ''
        with patch('sys.stdout', new_callable=io.StringIO) as console:
            ilapfuncs.logfunc(42)
        self.assertEqual(console.getvalue(), '42\n')
        self.assertFalse(self.path.exists())

    def test_real_processing_entry_point_owns_a_session(self):
        # The directory name can be arbitrary in CI; version_info carries the core.
        from scripts.version_info import leapp_name  # pylint: disable=import-outside-toplevel
        core = leapp_name.lower()
        module = importlib.import_module(core)
        self.assertTrue(hasattr(module.crunch_artifacts, '__wrapped__'))

    def test_actual_processing_early_returns_close_the_log(self):
        from scripts.version_info import leapp_name  # pylint: disable=import-outside-toplevel
        module = importlib.import_module(leapp_name.lower())
        arguments = dict(plugins=[], extracttype='invalid', input_path=self.temp.name,
                         out_params=Mock(), wrap_text=True, loader=Mock(), casedata={},
                         profile_filename=None)
        if 'time_offset' in inspect.signature(module.crunch_artifacts).parameters:
            arguments['time_offset'] = 0
        with patch.object(module, 'logdevinfo', create=True), \
                patch.object(module, 'report_supplied_keychain', create=True), \
                patch('sys.stdout', new_callable=io.StringIO):
            self.assertFalse(module.crunch_artifacts(**arguments))
            self.assertIsNone(ilapfuncs._screen_log._handle)  # pylint: disable=protected-access
            arguments['extracttype'] = 'fs'
            with patch.object(module, 'FileSeekerDir', side_effect=OSError('seeker failed')):
                self.assertFalse(module.crunch_artifacts(**arguments))
            self.assertIsNone(ilapfuncs._screen_log._handle)  # pylint: disable=protected-access
        self.assertIn('seeker failed', self.path.read_text())

    def test_process_exit_retries_pending_output_through_atexit(self):
        code = '''import errno
import sys
from unittest.mock import patch
from scripts import ilapfuncs
ilapfuncs.OutputParameters.screen_output_file_path = sys.argv[1]
with patch('builtins.open', side_effect=OSError(errno.EMFILE, 'exhausted')):
    ilapfuncs.logfunc('saved at process exit')
'''
        result = subprocess.run([sys.executable, '-B', '-c', code, str(self.path)],
                                cwd=REPO_ROOT, capture_output=True, text=True, timeout=30, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn('Exception ignored in atexit', result.stderr)
        self.assertEqual(self.path.read_text(), 'saved at process exit<br>\n')


def descriptor_stress():
    """Exercise actual EMFILE in this child without changing the runner's limits."""
    import resource  # pylint: disable=import-outside-toplevel
    original = resource.getrlimit(resource.RLIMIT_NOFILE)
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        writer = ScreenLogWriter()
        handles = []

        def exhaust():
            while True:
                try:
                    handles.append(open(root / 'held', 'ab'))  # pylint: disable=consider-using-with
                except OSError as exc:
                    assert exc.errno == errno.EMFILE
                    return

        def release():
            for handle in handles:
                handle.close()
            handles.clear()

        try:
            resource.setrlimit(resource.RLIMIT_NOFILE, (64, original[1]))
            path = root / 'persistent.html'
            with writer.session(path):
                writer.write(path, 'before<br>\n')
                exhaust()
                writer.write(path, 'during é<br>\n')
                release()
                assert path.read_text() == 'before<br>\nduring é<br>\n'
            path = root / 'replay.html'
            exhaust()
            writer.write(path, 'one<br>\n')
            writer.write(path, 'two<br>\n')
            release()
            writer.write(path, 'three<br>\n')
            assert path.read_text() == 'one<br>\ntwo<br>\nthree<br>\n'
            path = root / 'shutdown.html'
            exhaust()
            writer.write(path, 'last<br>\n')
            release()
            writer.close()
            assert path.read_text() == 'last<br>\n'
        finally:
            release()
            writer.close()
            resource.setrlimit(resource.RLIMIT_NOFILE, original)
    print('persistent handle, ordered replay, and shutdown recovery: PASS')


if __name__ == '__main__':
    if sys.argv[1:] == ['--descriptor-stress']:
        descriptor_stress()
    else:
        unittest.main()
