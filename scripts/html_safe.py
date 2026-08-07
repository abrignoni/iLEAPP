"""Helpers for safely emitting evidence-derived values into ``html_columns`` cells.

Columns listed in an artifact's ``__artifacts_v2__`` ``html_columns`` are written to
the HTML report **without** the framework's ``html.escape`` (see
``scripts/artifact_report.py`` ``write_artifact_data_table`` -- the ``html_no_escape``
branch). Any evidence-derived text placed in such a cell is therefore an
HTML/JavaScript injection sink: malicious content in a parsed return renders live in
the examiner's report (stored XSS, CWE-79).

Route every evidence-derived value in an ``html_columns`` cell through these helpers so
the dynamic parts are escaped while the tool's own structural markup (``<br>``,
``<table>``) is preserved.

**A report links to nothing outside its own folder.** A remote destination in a
report is a disclosure channel: an ``<img src="https://...">`` is fetched the moment
the report is opened, with no click, which tells whoever controls that host that the
account is under examination, when, and from which IP address. An ``<a href>`` needs a
click but reaches the same place. Reports are read on analyst workstations and mailed
to counsel, so no ``href`` or ``src`` may leave the report folder -- not ``http``,
``https``, ``ftp``, and not ``mailto``/``tel``, which hand the subject's own address or
number to a mail client or dialer.

Evidence URLs are still *evidence*, so nothing is dropped: they are rendered as escaped
text the examiner can read and copy. Only the anchor goes away. Report-relative
destinations -- ``media/<file>`` thumbnails, files an artifact writes beside the report
-- stay clickable through ``safe_local_link()``; they resolve offline and reach nothing.
"""

import html
from urllib.parse import urlparse, quote


def esc(value):
    """HTML-escape a single evidence value for safe use in text or an attribute.

    ``None`` becomes ``''``. ``quote=True`` escapes ``"`` and ``'`` as well, so the
    result is safe in both element-text and double-quoted-attribute contexts.
    """
    if value is None:
        return ''
    return html.escape(str(value), quote=True)


def safe_url(url, text=None, target=None):      # pylint: disable=unused-argument
    """Render an evidence URL as escaped text. **Never returns a link.**

    A URL read out of an extraction names a host chosen by whoever wrote the data, so
    it is exactly the destination a report must not reach; see the module docstring.
    The URL itself is evidence and is preserved verbatim as escaped text, so an
    examiner can read it, copy it, and open it deliberately elsewhere.

    ``text`` overrides the visible string when the caller has a better label than the
    raw URL. ``target`` is accepted and ignored: it exists so the call sites that
    passed it before this became text-only keep working.
    """
    url = '' if url is None else str(url).strip()
    return esc(text if text is not None else url)


def _is_report_relative(path, allow_parent=False):
    """True when ``path`` names something reachable from the report folder.

    Rejects a URL scheme, a protocol-relative ``//host`` and an absolute path, so a
    crafted media name cannot turn a report cell into a remote fetch. ``..`` is
    rejected too unless ``allow_parent`` is set: media_to_html() genuinely emits
    ``../data/...`` to reach the extraction folder next to the report, and that is a
    deliberate part of the report layout rather than an escape.
    """
    if path.startswith(('/', '\\')):
        return False
    normalized = path.replace('\\', '/')
    if normalized.startswith('//'):
        return False
    if not allow_parent and '..' in normalized.split('/'):
        return False
    try:
        if urlparse(path).scheme:
            return False
    except ValueError:
        return False
    return True


def safe_local_path(path, allow_parent=False):
    """Percent-encode a report-relative path for use in an ``href``/``src`` attribute.

    Returns ``''`` when the path is not report-relative, so a crafted media filename
    can neither point the report at a remote host nor reach outside the report folder.
    The encoded result is HTML-escaped as well, so it is safe inside a quoted
    attribute. Use this for the attribute value; use safe_local_link() when you want
    the whole anchor.
    """
    path = '' if path is None else str(path).strip()
    if not path or not _is_report_relative(path, allow_parent):
        return ''
    return esc(quote(path, safe='/.'))


def safe_local_link(path, text=None):
    """Build an ``<a href>`` to a file inside the report folder.

    This is the only helper that still emits an anchor. The destination must be
    report-relative -- no scheme, no protocol-relative ``//host``, no absolute path,
    and no ``..`` escaping the folder -- so following it can never leave the report.
    Anything else is returned as escaped text with no anchor.
    """
    path = '' if path is None else str(path).strip()
    label = esc(text if text is not None else path)
    if not path or not _is_report_relative(path):
        return label
    return f'<a href="{esc(path)}" target="_blank">{label}</a>'


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
