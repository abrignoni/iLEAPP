"""admin/scripts/helper_index.py counts the helpers artifact modules import, on a built tree."""
import importlib.util
import pathlib
import tempfile
import textwrap
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / 'scripts' / 'helper_index.py'


def load(root):
    spec = importlib.util.spec_from_file_location('helper_index_under_test', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root
    module.SCRIPTS = root / 'scripts'
    module.ARTIFACTS = root / 'scripts' / 'artifacts'
    module.OUTPUT = root / 'admin' / 'docs' / 'generated' / 'helper_functions_index.md'
    return module


class TestHelperIndex(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.write('scripts/ilapfuncs.py', '''
            def used(path, limit=3):
                """Used by two artifacts."""
            def unused():
                pass
            def _private():
                pass
            from scripts.lavafuncs import media_info
            class Context:
                """The run's state."""
                def get_files_found(self):
                    """Files the artifact matched."""
                def _hidden(self):
                    pass
            class Reader:
                """Reads a <table> of rows."""
                def __init__(self, path, limit=5):
                    pass
                @property
                def known(self):
                    """Whether it is known."""
                @known.setter
                def known(self, value):
                    pass
            ''')
        self.write('scripts/lavafuncs.py', '''
            def media_info(item):
                """Media details for an item."""
            ''')
        self.write('scripts/context.py', '''
            class Context:
                """Handed to every artifact."""
                def get_relative_path(self, path):
                    """The evidence-relative path."""
            ''')
        self.write('scripts/pkg/__init__.py', '')
        self.write('scripts/pkg/child.py', '''
            def child_helper():
                """In a module imported from its package."""
            ''')
        self.write('scripts/starred.py', '''
            def starred_helper():
                pass
            ''')
        self.write('scripts/whole.py', '''
            def thing():
                """A helper imported as a module."""
            ''')
        self.write('scripts/vendor/reader.py', 'def read():\n    pass\n')
        self.write('scripts/own/tool.py', '''
            def typed(x: str | None = None):
                """A first-party helper in a subfolder."""
            ''')
        self.write('scripts/artifacts/helpers.py', '''
            def shared():
                """A helper module beside the artifacts."""
            ''')
        self.write('scripts/artifacts/one.py', '''
            __artifacts_v2__ = {"a": {"name": "A"}}
            from scripts.ilapfuncs import used, Context, media_info, Reader
            from scripts.pkg import child
            from scripts.starred import *
            from scripts.artifacts.helpers import shared
            from scripts import whole
            from scripts.vendor.reader import read
            from scripts.own.tool import typed
            ''')
        self.write('scripts/artifacts/two.py', '''
            __artifacts_v2__ = {"a": {"name": "A"}}
            from scripts.ilapfuncs import used
            import scripts.whole
            ''')
        self.write('scripts/artifacts/not_an_artifact.py', 'from scripts.ilapfuncs import unused\n')

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(text).lstrip('\n'), encoding='utf-8')

    def test_counts_signatures_and_docstrings(self):
        text = load(self.root).build()
        self.assertIn('| 2 | `used` | `used(path, limit=3)` | Used by two artifacts. |', text)
        self.assertIn('| 0 | `unused` | `unused()` | (no docstring) |', text)
        self.assertNotIn('_private', text)
        self.assertIn("| 1 | class `Context` | | The run's state. |", text)
        self.assertIn('| | `Context.get_files_found` | `get_files_found(self)` | Files the artifact matched. |', text)
        self.assertNotIn('_hidden', text)

    def test_helper_modules_beside_artifacts_and_whole_module_imports(self):
        text = load(self.root).build()
        self.assertIn('## `scripts.artifacts.helpers`', text)
        self.assertIn('| 1 | `shared` | `shared()` |', text)
        self.assertIn('Imported as a module by 2 artifact module(s)', text)
        self.assertIn('| 1 | `scripts.vendor.reader` | vendored or generated |', text)
        self.assertIn('## `scripts.own.tool`', text)
        self.assertIn('| 1 | `typed` | `typed(x: str \\| None=None)` |', text)

    def test_constructors_properties_and_escaping(self):
        text = load(self.root).build()
        self.assertIn('| 1 | class `Reader` | `Reader(path, limit=5)` | Reads a &lt;table&gt; of rows. |', text)
        self.assertIn('| | `Reader.known` | property | Whether it is known. |', text)
        self.assertEqual(text.count('`Reader.known`'), 1)

    def test_reexports_context_child_modules_and_star_imports(self):
        text = load(self.root).build()
        self.assertIn('| 1 | `media_info` | `media_info(item)` | Defined in `scripts.lavafuncs`. Media details '
                      'for an item. |', text)
        self.assertIn('## `scripts.context`', text)
        self.assertIn('| | `Context.get_relative_path` | `get_relative_path(self, path)` |', text)
        self.assertIn('## `scripts.pkg.child`', text)
        self.assertIn('## `scripts.starred`', text)
        self.assertIn('Imported with `*` by 1 artifact module(s)', text)
        section = text.split('## `scripts.starred`')[1].split('## ')[0]
        self.assertNotIn('Imported as a module', section)

    def test_check_exit_codes_and_leaves_the_file_alone(self):
        module = load(self.root)
        self.assertEqual(module.main(['--check']), 1)
        self.assertFalse(module.OUTPUT.exists())
        self.assertEqual(module.main([]), 0)
        self.assertEqual(module.main(['--check']), 0)
        written = module.OUTPUT.read_text(encoding='utf-8')
        self.write('scripts/artifacts/three.py', '__artifacts_v2__ = {}\nfrom scripts.ilapfuncs import unused\n')
        self.assertEqual(module.main(['--check']), 1)
        self.assertEqual(module.OUTPUT.read_text(encoding='utf-8'), written)

    def test_most_used_module_comes_first(self):
        text = load(self.root).build()
        self.assertLess(text.index('## `scripts.ilapfuncs`'), text.index('## `scripts.artifacts.helpers`'))


if __name__ == '__main__':
    unittest.main()
