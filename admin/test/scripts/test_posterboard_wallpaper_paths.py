"""PosterBoard Wallpaper's paths match an image layer whatever the case of its extension.

Matching is fnmatch, case-sensitive off Windows. The layers in output.layerStack folders on
the josh-hickman-ios17 path listing all end in .HEIC, so '*.heic' found none of them on
macOS or Linux. Each extension is now a bracket class, which matches both cases with one
pattern, so a file is never matched twice.
"""
import fnmatch
import unittest

from scripts.artifacts import springboard

PATTERNS = springboard.__artifacts_v2__['posterboard_wallpaper']['paths']
FOLDER = ('root/private/var/mobile/tmp/com.apple.mediaanalysisd/PosterConfigurations/A/'
          'com.apple.PhotosUIPrivate.PhotosPosterProvider/configurations/B/versions/0/contents/C/'
          'output.layerStack/')


def matches(path):
    return [pattern for pattern in PATTERNS if fnmatch.fnmatchcase(path, pattern)]


class PosterboardWallpaperPathsTest(unittest.TestCase):

    def test_each_image_layer_matches_once_in_either_case(self):
        for name in ('portrait-layer_background.HEIC', 'portrait-layer_background.heic',
                     'layer.JPG', 'layer.jpg', 'layer.JPEG', 'layer.jpeg', 'layer.PNG', 'layer.png'):
            self.assertEqual(len(matches(FOLDER + name)), 1, name)

    def test_other_files_in_the_folder_do_not_match(self):
        for name in ('Contents.json', 'layer.heic.json'):
            self.assertEqual(matches(FOLDER + name), [], name)


if __name__ == '__main__':
    unittest.main()
