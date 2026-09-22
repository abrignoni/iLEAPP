"""Every BeautifulSoup call names its parser, and requirements.txt installs it.

BeautifulSoup takes the parser as a string. A module that asks for 'lxml'
therefore imports cleanly on a machine without lxml and fails only when it
parses, with bs4.FeatureNotFound. The runtime-contract job cannot see that: it
installs requirements.txt and imports every module, and the import succeeds.
RLEAPP 2026.4.1 shipped exactly this. Its Meta return reader asked for 'lxml',
requirements.txt did not list it, and every Meta return artifact failed on a
clean install and in the release builds.

A call that names no parser, or a feature several builders share ('html',
'permissive'), gets whichever builder happens to be installed, so one input can
parse differently on two machines. Those calls are refused too.

The parser names and the library behind each were read from the builder
modules of beautifulsoup4 4.8.2 (bs4/builder/_htmlparser.py, _lxml.py and
_html5lib.py). Features that more than one library provides are left out.

The same file runs in all five LEAPP cores.
"""
import ast
import pathlib
import re
import unittest
import warnings

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]

# The code a release ships: the entry points beside the repo root and these packages.
SHIPPED_PACKAGES = ('scripts', 'leapp_functions')

# Parser name -> the distribution that provides it (None: the standard library).
PARSER_LIBRARY = {
    'html.parser': None,
    'lxml': 'lxml',
    'lxml-xml': 'lxml',
    'xml': 'lxml',
    'html5lib': 'html5lib',
}


def declared_distributions(requirements_text):
    """Distribution names in a requirements file, normalised the way pip compares them."""
    names = set()
    for line in requirements_text.splitlines():
        line = line.split('#', 1)[0].strip()
        if not line or line.startswith('-'):
            continue
        match = re.match(r'[A-Za-z0-9][A-Za-z0-9._-]*', line)
        if match:
            names.add(re.sub(r'[-_.]+', '-', match.group(0)).lower())
    return names


def _soup_names(tree):
    """Every name the module binds BeautifulSoup to, including 'import ... as'."""
    names = {'BeautifulSoup'}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == 'bs4':
            names.update(alias.asname for alias in node.names
                         if alias.name == 'BeautifulSoup' and alias.asname)
    return names


def bs4_calls(source, filename='<module>'):
    """(line, parser) for each BeautifulSoup call: the parser is the literal name,
    '' when the call names none, or None when it is not a string literal."""
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', SyntaxWarning)
        tree = ast.parse(source, filename)
    soup_names = _soup_names(tree)
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not ((isinstance(func, ast.Name) and func.id in soup_names)
                or (isinstance(func, ast.Attribute) and func.attr == 'BeautifulSoup')):
            continue
        if len(node.args) > 1:
            arg = node.args[1]
        else:
            arg = next((k.value for k in node.keywords if k.arg == 'features'), None)
        if arg is None:
            parser = ''
        elif isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            parser = arg.value
        else:
            parser = None
        found.append((node.lineno, parser))
    return found


def problems(sources, declared):
    """One message per call that is unnamed, unverifiable, or needs a library
    requirements.txt does not install. `sources` maps a path to its source."""
    out = []
    for path, source in sorted(sources.items()):
        for line, parser in bs4_calls(source, path):
            where = f'{path}:{line}'
            if parser is None:
                out.append(f'{where}: the parser is not a string literal, so what it needs cannot be checked')
            elif parser not in PARSER_LIBRARY:
                named = 'names no parser' if parser == '' else f'names {parser!r}'
                out.append(f'{where}: {named}; name one of {", ".join(sorted(PARSER_LIBRARY))}, '
                           f'or bs4 uses whichever builder happens to be installed')
            elif PARSER_LIBRARY[parser] and PARSER_LIBRARY[parser] not in declared:
                out.append(f'{where}: asks for {parser!r}, which needs {PARSER_LIBRARY[parser]}, '
                           f'and requirements.txt does not list it')
    return out


def shipped_sources():
    """Every module a release ships: the entry points and the shipped packages."""
    paths = sorted(REPO_ROOT.glob('*.py'))
    for package in SHIPPED_PACKAGES:
        paths += sorted((REPO_ROOT / package).rglob('*.py'))
    return {p.relative_to(REPO_ROOT).as_posix(): p.read_bytes() for p in paths}


class Bs4ParserDependencies(unittest.TestCase):

    def test_every_shipped_call_names_a_parser_requirements_install(self):
        declared = declared_distributions((REPO_ROOT / 'requirements.txt').read_text(encoding='utf-8'))
        sources = shipped_sources()
        calls = sum(len(bs4_calls(source, path)) for path, source in sources.items())
        self.assertGreater(calls, 0, 'found no BeautifulSoup call at all, so the scan is not reading the tree')
        self.assertEqual(problems(sources, declared), [])

    def test_an_undeclared_parser_is_refused(self):
        source = "from bs4 import BeautifulSoup\nsoup = BeautifulSoup(data, 'lxml')\n"
        self.assertEqual(len(problems({'m.py': source}, {'beautifulsoup4'})), 1)
        self.assertEqual(problems({'m.py': source}, {'beautifulsoup4', 'lxml'}), [])

    def test_the_standard_library_parser_needs_nothing_declared(self):
        source = "import bs4\nsoup = bs4.BeautifulSoup(data, features='html.parser')\n"
        self.assertEqual(problems({'m.py': source}, set()), [])

    def test_a_call_through_an_alias_is_checked(self):
        source = "from bs4 import BeautifulSoup as Soup\nsoup = Soup(data, 'lxml')\n"
        self.assertEqual(len(problems({'m.py': source}, {'beautifulsoup4'})), 1)

    def test_a_call_that_leaves_the_parser_to_the_machine_is_refused(self):
        for call in ('BeautifulSoup(data)', "BeautifulSoup(data, 'html')", 'BeautifulSoup(data, parser)'):
            with self.subTest(call=call):
                self.assertEqual(len(problems({'m.py': f'soup = {call}\n'}, {'lxml', 'html5lib'})), 1)

    def test_requirement_names_are_read_like_pip(self):
        text = 'beautifulsoup4==4.8.2\nLXML>=5  # parser\n# a comment\n\npdfminer.six\n-r other.txt'
        self.assertEqual(declared_distributions(text), {'beautifulsoup4', 'lxml', 'pdfminer-six'})


if __name__ == '__main__':
    unittest.main()
