"""Candidate-only fixed rejection diagnostics preserve table and tree parsing."""
import io
import pathlib
import sys
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
from scripts.artifacts import sysdiagnoseProcess as artifact  # pylint: disable=wrong-import-position


class RejectedProcessRows(unittest.TestCase):
    def test_rejections_preserve_surrounding_table_and_tree(self):
        source = '/synthetic/capture/ps.txt'
        relative = 'capture/ps.txt'
        root = 'root 0 0 10 1 4004 0.0 0.0 31 0 100 20 - ?? Ss 1:25PM 0:00.00 /sbin/root --accepted'
        child = 'mobile 501 0 11 10 4004 0.0 0.0 31 0 200 30 - ?? S Tue9AM 0:00.00 /bin/child --accepted'
        short = 'mobile 501 0 99 10 4004 0.0 0.0 31 0 200 30 - ?? S Tue9AM SHORT_SECRET'
        bad_pid = 'mobile 501 0 BAD_PID 10 4004 0.0 0.0 31 0 200 30 - ?? S Tue9AM 0:00.00 PID_SECRET'
        bad_parent = 'mobile 501 0 99 BAD_PARENT 4004 0.0 0.0 31 0 200 30 - ?? S Tue9AM 0:00.00 PPID_SECRET'
        text = '\n'.join(['USER UID PRSNA PID PPID FLAGS CPU MEM PRI NI VSZ RSS WCHAN TT STAT STARTED TIME COMMAND',
                          root, short, bad_pid, bad_parent, child, '   ']) + '\n'
        context = mock.Mock()
        context.get_files_found.return_value = [source]
        context.get_relative_path.return_value = relative
        def streams(_files, name):
            self.assertEqual(_files, [source])
            self.assertEqual(name, 'ps.txt')
            yield io.StringIO(text), source
        expected = [(10, 1, 'root', '/sbin/root --accepted', '0', 'Ss', '1:25PM', relative),
                    (11, 10, 'mobile', '/bin/child --accepted', '501', 'S', 'Tue9AM', relative)]
        with mock.patch.object(artifact, 'get_sysdiagnose_files', side_effect=streams), \
             mock.patch.object(artifact, 'logfunc') as log, \
             mock.patch.object(artifact, '_render_tree', return_value=b'owned-test-png') as render, \
             mock.patch.object(artifact, 'check_in_embedded_media', return_value='test-media-ref') as media:
            headers, rows, returned = artifact.sysdiagnoseProcess.__wrapped__(context)
            self.assertEqual(headers, ('PID', 'Parent PID', 'User', 'Command', 'UID', 'STAT', 'STARTED', 'Source File'))
            self.assertEqual(rows, expected)
            self.assertEqual([[type(v) for v in row] for row in rows], [[int, int, str, str, str, str, str, str]] * 2)
            self.assertEqual(returned, source)
            tree_headers, tree_rows, tree_source = artifact.sysdiagnoseProcessTree.__wrapped__(context)
            self.assertEqual(tree_headers, ('Capture', ('Tree', 'media')))
            self.assertEqual(tree_rows, [(relative, 'test-media-ref')])
            self.assertEqual(tree_source, source)
            render.assert_called_once_with(relative, [(0, 10, 'root', '/sbin/root --accepted'),
                                                     (1, 11, 'mobile', '/bin/child --accepted')],
                                           {'root': '#5b7ea6', 'mobile': '#6a9e6a'})
            media.assert_called_once_with(source, b'owned-test-png', 'sysdiagnose_process_tree.png',
                                          force_type='image/png', force_extension='png')
            messages = [call.args[0] for call in log.call_args_list]
            self.assertEqual(messages, ['Skipping ps.txt process row: fewer than 18 fields',
                                        'Skipping ps.txt process row: PID or parent PID is not an integer',
                                        'Skipping ps.txt process row: PID or parent PID is not an integer'] * 2)
            self.assertFalse(any(value in '\n'.join(messages) for value in [source, 'SHORT_SECRET', 'PID_SECRET',
                                                                           'PPID_SECRET', 'BAD_PID', 'BAD_PARENT',
                                                                           '/sbin/root', '/bin/child']))


if __name__ == '__main__':
    unittest.main()
