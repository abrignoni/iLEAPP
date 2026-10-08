"""Privacy helpers for public test-case and result snapshot metadata."""


def snapshot_author_email(author_email):
    """Keep GitHub noreply identities; redact other emails from snapshots."""
    if isinstance(author_email, str) and author_email.casefold().endswith(
            "@users.noreply.github.com"):
        return author_email
    return "N/A"
