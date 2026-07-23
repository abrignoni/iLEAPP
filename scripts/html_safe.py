"""Helpers for safely emitting evidence-derived values into ``html_columns`` cells.

Columns listed in an artifact's ``__artifacts_v2__`` ``html_columns`` are written to
the HTML report **without** the framework's ``html.escape`` (see
``scripts/artifact_report.py`` ``write_artifact_data_table`` -- the ``html_no_escape``
branch). Any evidence-derived text placed in such a cell is therefore an
HTML/JavaScript injection sink: malicious content in a parsed return renders live in
the examiner's report (stored XSS, CWE-79).

Route every evidence-derived value in an ``html_columns`` cell through these helpers so
the dynamic parts are escaped while the tool's own structural markup (``<a>``, ``<br>``,
``<table>``) is preserved.
"""

import html
from urllib.parse import urlparse

# Schemes we are willing to turn into a live <a href>. Anything else (notably
# javascript: and data:) is rendered as escaped text, never as a clickable link.
ALLOWED_URL_SCHEMES = ('http', 'https', 'mailto', 'tel', 'ftp', 'ftps')


def esc(value):
    """HTML-escape a single evidence value for safe use in text or an attribute.

    ``None`` becomes ``''``. ``quote=True`` escapes ``"`` and ``'`` as well, so the
    result is safe in both element-text and double-quoted-attribute contexts.
    """
    if value is None:
        return ''
    return html.escape(str(value), quote=True)


def safe_url(url, text=None, target='_blank'):
    """Build an ``<a href>`` anchor with an escaped, scheme-checked href.

    Returns the escaped visible text with **no** anchor when the URL is empty or its
    scheme is not allowlisted, so ``javascript:``/``data:`` URLs never become live
    links. ``text`` (the visible label) defaults to the URL itself.
    """
    url = '' if url is None else str(url).strip()
    label = esc(text if text is not None else url)
    if not url:
        return label
    try:
        scheme = urlparse(url).scheme.lower()
    except ValueError:
        return label
    if scheme not in ALLOWED_URL_SCHEMES:
        return label
    rel = ' rel="noopener noreferrer"' if target == '_blank' else ''
    return f'<a href="{esc(url)}" target="{esc(target)}"{rel}>{label}</a>'


def safe_join(values, sep='<br>'):
    """Escape each evidence value and join with a tool-controlled separator.

    The separator is emitted verbatim (it is tool-owned markup, default ``<br>``);
    every joined value is escaped.
    """
    return sep.join(esc(v) for v in values)


def safe_source(text):
    """Escape an evidence text/document body for display as source.

    Real newlines become ``<br>`` for readability *after* escaping, so any markup in
    the evidence (including a literal ``<br>``) is shown inert as text. Use for
    Tier-1 raw bodies -- message/email bodies, whole return pages, notes -- per the
    escape-to-source policy.
    """
    if text is None:
        return ''
    return esc(text).replace('\n', '<br>')
