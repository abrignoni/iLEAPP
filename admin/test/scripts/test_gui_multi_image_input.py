"""The window's input field with several disk images picked (the member images of a
RAID set), driven without a window.

The GUI module builds its window when imported, so the functions that handle the
input field are taken from its source and run against stand-ins for the widgets and
dialogs: the file dialog returns several paths, the field shows the first and how many
more, and validation reads them as one raw input. Nothing is drawn.
"""
import ast
import os
import pathlib
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

import scripts.raw_image as raw_image  # pylint: disable=wrong-import-position

GUI_SOURCE = next(REPO_ROOT.glob('*GUI.py'))
FUNCTIONS = ('set_input_selection', 'input_paths', 'ValidateInput', 'select_input')


class _Entry:
    def __init__(self, text=''):
        self.text = text

    def get(self):
        return self.text

    def delete(self, _first, _last=None):
        self.text = ''

    def insert(self, _index, text):
        self.text = text + self.text


class _Errors:
    def __init__(self):
        self.shown = []

    def showerror(self, _title=None, message=None, **_kw):
        self.shown.append(message)


class _History:
    def __init__(self):
        self.paths, self.sets = [], []

    def record_input_path(self, path):
        self.paths.append(path)

    def record_input_set(self, paths, found=()):
        self.sets.append((list(paths), list(found)))


class _Dialogs:
    def __init__(self, picked):
        self.picked = picked

    def askopenfilenames(self, **_kw):
        return tuple(self.picked)

    def askdirectory(self, **_kw):
        return ''


class _Tk:
    @staticmethod
    def splitlist(value):
        return tuple(value)


class _Window:
    tk = _Tk()


def _functions(namespace):
    tree = ast.parse(GUI_SOURCE.read_text(encoding='utf-8'))
    wanted = [node for node in tree.body
              if isinstance(node, ast.FunctionDef) and node.name in FUNCTIONS]
    module = ast.Module(body=wanted, type_ignores=[])
    exec(compile(module, str(GUI_SOURCE), 'exec'), namespace)  # pylint: disable=exec-used
    return namespace


class GuiSeveralImagesTest(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.mkdtemp(prefix='gui_multi_')
        self.addCleanup(shutil.rmtree, self.folder, True)
        self.images = []
        for name in ('disk0.img', 'disk1.img', 'disk2.img'):
            path = os.path.join(self.folder, name)
            with open(path, 'wb') as handle:
                handle.write(b'\0' * 4096)
            self.images.append(path)
        self.out = os.path.join(self.folder, 'out')
        os.makedirs(self.out)
        self.errors = _Errors()
        self.history = _History()
        self.dialogs = _Dialogs(self.images)
        self.ns = _functions({
            'os': os, 'Path': Path, 'tk_msgbox': self.errors, 'tk_filedialog': self.dialogs,
            'history': self.history, 'main_window': _Window(),
            'input_entry': _Entry(), 'output_entry': _Entry(self.out),
            'output_folder_name_entry': _Entry('report'), 'input_selection': [],
            'get_selected_modules': lambda: ['one'],
            'validate_output_folder_available': lambda _o, _n: (True, ''),
            'RAW_IMAGE_SUFFIXES': raw_image.RAW_IMAGE_SUFFIXES,
            'RAW_IMAGE_FILE_PATTERNS': raw_image.RAW_IMAGE_FILE_PATTERNS,
            'RAW_IMAGE_LABEL': raw_image.RAW_IMAGE_LABEL,
            'names_an_image_folder': raw_image.names_an_image_folder,
            'names_raw_images': raw_image.names_raw_images,
            'selected_paths': raw_image.selected_paths,
            'selection_text': raw_image.selection_text,
            'logical_among': raw_image.logical_among,
            'logical_refusal': raw_image.logical_refusal,
        })

    def test_several_images_picked_are_shown_as_the_first_and_how_many_more(self):
        self.ns['select_input']('file')
        self.assertEqual(self.ns['input_entry'].get(), f'{self.images[0]} and 2 more')
        self.assertEqual(self.ns['input_paths'](), self.images)
        self.assertEqual(self.history.sets, [(self.images, [])])
        self.assertEqual(raw_image.PathsTooltip.text(
            type('T', (), {'paths': staticmethod(self.ns['input_paths'])})()).splitlines()[1:],
            self.images)

    def test_several_images_validate_as_one_raw_input(self):
        self.ns['select_input']('file')
        result = self.ns['ValidateInput']()
        self.assertTrue(result[0])
        self.assertEqual(result[1], 'raw')
        self.assertEqual(self.errors.shown, [])

    def test_typing_over_the_field_reads_what_was_typed(self):
        self.ns['select_input']('file')
        self.ns['input_entry'].text = self.images[1]
        self.assertEqual(self.ns['input_paths'](), [self.images[1]])

    def test_one_image_picked_is_one_path_as_before(self):
        self.dialogs.picked = self.images[:1]
        self.ns['select_input']('file')
        self.assertEqual(self.ns['input_entry'].get(), self.images[0])
        self.assertEqual(self.history.paths, [self.images[0]])
        self.assertEqual(self.ns['ValidateInput']()[1], 'raw')

    def test_several_files_that_are_not_images_are_refused(self):
        archive = os.path.join(self.folder, 'extraction.zip')
        with open(archive, 'wb') as handle:
            handle.write(b'PK')
        self.dialogs.picked = [self.images[0], archive]
        self.ns['select_input']('file')
        self.assertFalse(self.ns['ValidateInput']()[0])
        self.assertIn('only as disk images', self.errors.shown[0])

    def test_several_images_are_read_as_raw_whatever_the_first_is_named(self):
        # numbered pieces of two different images: the first one's suffix alone does
        # not name a raw image type
        picked = []
        for name in ('first.002', 'second.003'):
            path = os.path.join(self.folder, name)
            with open(path, 'wb') as handle:
                handle.write(b'\0' * 4096)
            picked.append(path)
        self.dialogs.picked = picked
        self.ns['select_input']('file')
        self.assertEqual(self.ns['ValidateInput']()[1], 'raw')

    def test_logical_evidence_with_other_images_is_refused(self):
        ad1 = str(REPO_ROOT / 'admin' / 'test' / 'data' / 'raw_images' / 'lean-multi-ntfs-c9.ad1')
        self.dialogs.picked = [self.images[0], ad1]
        self.ns['select_input']('file')
        self.assertFalse(self.ns['ValidateInput']()[0])
        self.assertIn('is logical evidence', self.errors.shown[0])

    def test_cancelling_the_dialog_clears_the_field_as_before(self):
        self.dialogs.picked = []
        self.ns['input_entry'].text = 'something'
        self.ns['select_input']('file')
        self.assertEqual(self.ns['input_entry'].get(), '')


if __name__ == '__main__':
    unittest.main()
