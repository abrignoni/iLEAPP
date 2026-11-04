"""Images converted to PNG are not written into the report's evidence copy.

posterboard_wallpaper, springboard_wallpaper and apple_atx_images wrote each converted PNG
beside its source file, inside the report's data folder, which holds the copy of the
extraction the report presents as the source. On the josh-hickman-ios17 path listing that is
250 wallpaper layers and 108 ATX images, each adding a file the extraction never held; and a
layer.HEIC beside a layer.png would have had its conversion saved over the staged layer.png.
These tests run posterboard_wallpaper through the wrapper on exactly that pair and check the
data folder afterwards, then check the shared helpers of both modules.
"""
import hashlib
import io
import os
import pathlib
import shutil
import sys
import tempfile
import types
import unittest
from unittest import mock

from PIL import Image
from pillow_heif import register_heif_opener

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts import lavafuncs  # pylint: disable=wrong-import-position
from scripts.artifacts import apple_atx_images, springboard  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position
from scripts.ilapfuncs import OutputParameters  # pylint: disable=wrong-import-position
from scripts.search_files import FileInfo  # pylint: disable=wrong-import-position

register_heif_opener()
LAYERS = 'private/var/mobile/Containers/Data/Application/A/Library/output.layerStack'


def image_bytes(fmt, colour):
    buffer = io.BytesIO()
    Image.new('RGB', (8, 8), colour).save(buffer, fmt)
    return buffer.getvalue()


def tree_digest(folder):
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(pathlib.Path(folder).rglob('*')) if p.is_file()}


class ConvertedMediaOutOfEvidenceCopyTest(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        Context.clear()
        lavafuncs.initialize_lava(self.tmpdir, self.tmpdir, 'fs')
        self._saved_log_paths = {name: getattr(OutputParameters, name) for name in vars(OutputParameters)
                                 if name.startswith('screen_output_file_path')}
        self.output_params = OutputParameters(self.tmpdir)
        Context.set_output_params(self.output_params)
        patcher = mock.patch('scripts.ilapfuncs.logfunc')
        patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        for name, value in self._saved_log_paths.items():
            setattr(OutputParameters, name, value)
        lavafuncs.lava_db.close()
        lavafuncs.lava_db = None
        lavafuncs.lava_data = None
        lavafuncs.lava_db_path = None
        Context.clear()
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_a_heic_layer_beside_a_png_of_the_same_name(self):
        data = pathlib.Path(self.output_params.data_folder)
        folder = data / LAYERS
        folder.mkdir(parents=True)
        heic = folder / 'layer.HEIC'
        png = folder / 'layer.png'
        heic.write_bytes(image_bytes('HEIF', 'red'))
        png.write_bytes(image_bytes('PNG', 'blue'))
        before = tree_digest(data)
        seeker = types.SimpleNamespace(directory=self.tmpdir, file_infos={
            str(heic): FileInfo(f'{LAYERS}/layer.HEIC', 0, 0), str(png): FileInfo(f'{LAYERS}/layer.png', 0, 0)})
        report_folder = pathlib.Path(self.output_params.output_folder_base, '_HTML', 'iOS Screens')
        report_folder.mkdir(parents=True)

        _, rows, _ = springboard.posterboard_wallpaper(  # pylint: disable=too-many-function-args
            [str(heic), str(png)], str(report_folder), seeker, True, 'UTC')

        self.assertEqual(tree_digest(data), before)
        self.assertEqual(sorted(row[5] for row in rows), ['Converted HEIC to PNG', 'Media checked in'])
        self.assertEqual(len(list(pathlib.Path(self.output_params.media_folder).glob('*.png'))), 2)
        self.assertEqual(list(pathlib.Path(self.output_params.output_folder_base).glob('_converting_*')), [])

    def test_the_helpers_give_each_source_its_own_name_outside_the_data_folder(self):
        for module in (springboard, apple_atx_images):
            work_dir = module._conversion_dir()  # pylint: disable=protected-access
            try:
                self.assertEqual(os.path.dirname(work_dir), self.output_params.output_folder_base)
                first = module._converted_png_path(work_dir, 'a/layer.HEIC')  # pylint: disable=protected-access
                second = module._converted_png_path(work_dir, 'b/layer.HEIC')  # pylint: disable=protected-access
                self.assertNotEqual(first, second)
                self.assertEqual(first.parent, pathlib.Path(work_dir))
            finally:
                shutil.rmtree(work_dir)


if __name__ == '__main__':
    unittest.main()
