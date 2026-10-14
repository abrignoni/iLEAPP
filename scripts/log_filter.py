"""Conservative multi-pattern gate for the Unified Log collection query.

SQLite remains the final authority for LIKE and equality. A positive AND/OR
expression can only match if at least one of its literal anchors occurs. Test
all anchors in one compiled Aho-Corasick pass per column, then let SQLite check
the original expression for candidate rows. Unsupported queries use plain SQL.
"""
import re

try:
    import ahocorasick
except (ImportError, OSError):
    ahocorasick = None


_SELECT = re.compile(r'\s*SELECT\s+\*\s+FROM\s+logarchive\s+WHERE\s+', re.IGNORECASE)
_TOKEN = re.compile(r"\s+|--[^\n]*|/\*[\s\S]*?\*/|'(?:''|[^'])*'|[A-Za-z_][A-Za-z_0-9]*|[=()]")
_COLUMNS = {'event_message', 'category', 'subsystem', 'process_image_path'}
_FUNCTION = 'ileapp_log_candidate'


def _anchors(expression):
    """Accept only column LIKE/= string atoms joined by positive AND/OR.

    Tokenize comments separately from strings so '--' inside evidence patterns
    is never discarded. Reject every unrecognized token or expression rather
    than guessing how a future query behaves.
    """
    tokens = []
    position = 0
    for match in _TOKEN.finditer(expression):
        if match.start() != position:
            return None
        position = match.end()
        token = match.group()
        if not (token.isspace() or token.startswith(('--', '/*'))):
            tokens.append(token)
    if position != len(expression):
        return None

    patterns = {}
    index = depth = 0
    operand = True
    while index < len(tokens):
        token = tokens[index]
        if operand:
            if token == '(':
                depth += 1
                index += 1
                continue
            if (index + 2 >= len(tokens) or token not in _COLUMNS
                    or tokens[index + 1].upper() not in ('LIKE', '=')
                    or not tokens[index + 2].startswith("'")):
                return None
            literal = tokens[index + 2][1:-1].replace("''", "'")
            # SQLite LIKE stops at NUL. Non-ASCII patterns require SQLite's
            # own case rules; neither is safe to approximate here.
            if not literal.isascii() or '\x00' in literal:
                return None
            anchor = (max(re.split(r'[%_]', literal), key=len)
                      if tokens[index + 1].upper() == 'LIKE' else literal)
            # A wildcard-only or empty-string branch can match without an anchor.
            if not anchor:
                return None
            patterns.setdefault(token, set()).add(anchor.lower())
            index += 3
            operand = False
        elif token == ')' and depth:
            depth -= 1
            index += 1
        elif token.upper() in ('AND', 'OR'):
            operand = True
            index += 1
        else:
            return None
    return patterns if patterns and not operand and depth == 0 else None


def accelerate_query(db, query):
    """Register a connection-local gate and return (query, acceleration status)."""
    if ahocorasick is None:
        return query, 'SQLite fallback (compiled matcher unavailable)'
    prefix = _SELECT.match(query)
    patterns = _anchors(query[prefix.end():]) if prefix else None
    if patterns is None:
        return query, 'SQLite fallback (unsupported filter expression)'
    machines = []
    for anchors in patterns.values():
        # Automaton is supplied by the C extension and exercised by the SQL tests.
        machine = ahocorasick.Automaton()  # pylint: disable=c-extension-no-member
        for anchor in anchors:
            machine.add_word(anchor, 1)
        machine.make_automaton()
        machines.append(machine)

    def candidate(*values):
        for machine, value in zip(machines, values):
            if value is None:
                continue
            # Numeric/blob values can have SQLite-specific coercions. Keep them
            # as candidates and let the unchanged SQL make the decision.
            if not isinstance(value, str):
                return 1
            # Every anchor is ASCII. Unicode lowercasing can add candidates,
            # but cannot remove an ASCII substring needed for a SQL match.
            if next(machine.iter(value.lower()), None) is not None:
                return 1
        return 0

    db.create_function(_FUNCTION, len(patterns), candidate)
    gate = f'{_FUNCTION}({", ".join(patterns)})'
    return (query[:prefix.end()] + gate + ' AND (' + query[prefix.end():] + '\n)',
            'compiled multi-pattern prefilter; original SQLite predicates retained')
