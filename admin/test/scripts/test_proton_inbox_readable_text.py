"""Proton Mail Inbox HTML bodies read as lines of text."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts import artifact_report  # pylint: disable=wrong-import-position
from scripts.artifacts import protonMailInbox as proton  # pylint: disable=wrong-import-position

read = proton._body_text_and_links  # pylint: disable=protected-access


class ProtonBodyTextTest(unittest.TestCase):
    def test_a_page_reads_as_lines_of_text(self):
        page = ('<html><head><title>Hidden</title><style>p{color:red}</style></head><body>'
                '<p>Hello&nbsp;<b>wor</b>ld</p><script>var x=1</script>'
                '<div>Two<br>Three <a href="https://example.test/x">link</a></div>'
                '<table><tr><td>A</td><td>B</td></tr></table></body></html>')
        self.assertEqual(read(page), ('Hidden\nHello world\nTwo\nThree link [1]\nA B', '[1] https://example.test/x'))

    def test_an_unclosed_head_keeps_the_body(self):
        self.assertEqual(read('<head><title>T</title><body><p>Kept</p>')[0], 'T\nKept')

    def test_mixed_br_forms_break_in_place(self):
        self.assertEqual(read('a<br>b<br/>c<br />d')[0], 'a\nb\nc\nd')

    def test_an_unclosed_style_shows_the_text_after_it(self):
        self.assertIn('Kept', read('<p>a</p><style>Kept')[0])

    def test_a_style_named_in_a_later_comment_is_still_removed(self):
        self.assertEqual(read('<style>p{}</style><p>a</p><!-- <style -->')[0], 'a')

    def test_no_closing_tag_is_added_to_the_text(self):
        self.assertEqual(read('<p>a</p><script>var s="<style>";')[0], 'a\nvar s="<style>";')

    def test_a_tag_name_in_an_attribute_does_not_keep_style_text(self):
        self.assertEqual(read('<style>p{}</style><a title="<style>" href="u">x</a>')[0], 'x [1]')

    def test_explicit_blank_lines_are_kept_once(self):
        self.assertEqual(read('one<br><br>two')[0], 'one\n\ntwo')
        self.assertEqual(read('<pre>one\n\ntwo</pre>')[0], 'one\n\ntwo')
        self.assertEqual(read('one<br><br><br><br>two<br><br>')[0], 'one\n\ntwo')

    def test_block_edges_make_no_blank_line(self):
        self.assertEqual(read('<div><p>one</p></div><div><p>two</p></div>')[0], 'one\ntwo')

    def test_a_broken_character_reference_before_an_open_style_does_not_raise(self):
        self.assertIn('Hello', read('<p>Hello</p>&#<style>Kept')[0])

    def test_markup_the_parser_refuses_does_not_raise(self):
        self.assertIn('Hello', read('<p>Hello</p><![bogus]>')[0])

    def test_pre_keeps_a_line_end_before_an_inline_tag(self):
        self.assertEqual(read('<pre>one\n<b>two</b></pre>')[0], 'one\ntwo')

    def test_a_body_that_is_not_html_stays_as_stored(self):
        stored = '<b>literal</b>\n  spaced'
        self.assertEqual(proton._message_body(stored, 'text/plain'), (stored, ''))  # pylint: disable=protected-access
        self.assertEqual(proton._message_body('<p>a</p>', 'text/html'), ('a', ''))  # pylint: disable=protected-access
        self.assertEqual(proton._message_body(b'plain', 'text/plain'), ('plain', ''))  # pylint: disable=protected-access

    def test_the_page_escapes_and_shows_breaks(self):
        self.assertEqual(artifact_report.cell_html('<b>a</b>\nb', 'Body', [], ['Body']), '&lt;b&gt;a&lt;/b&gt;<br>b')


if __name__ == '__main__':
    unittest.main()
