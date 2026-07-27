"""
Artifact result wrapper for large LEAPP artifact outputs.

Most artifact modules can keep returning the traditional
``(headers, data_list, source_path)`` tuple. Modules that may produce very large
outputs can return ``ArtifactResult`` instead and write rows one at a time:
create the result, set headers and source metadata, call ``add_row()`` in the
same loop that currently builds ``data_list``, then return the result.

``ArtifactResult`` intentionally does not create a private spool format. Writer
mode streams rows into the LAVA SQLite output in bounded batches while the
module is still running. The core artifact processor then replays rows from
that table for HTML, TSV, timeline, and KML outputs when those formats are
requested. This keeps a beginner-friendly module-author contract while avoiding
a second serialization layer.

The traditional reusable list-return path remains unchanged. Advanced callers
can still pass an iterable with ``rows=`` and let the core consume it, but the
recommended shape for new large artifacts is ``add_row()``.

Queue settings are preserved for async iterable insertion, and writer mode
keeps its own per-result batch state so multiple results can coexist.
"""


class ArtifactResult:
    """Container for artifact metadata and rows to be streamed by the core."""

    def __init__(
        self,
        headers=None,
        source_path=None,
        estimated_row_count=None,
        async_write=False,
        queue_size=5000,
        batch_size=10000,
        rows=None,
        writer_metadata=None,
        source_path_formatter=None,
    ):
        self._source_path_formatter = source_path_formatter
        self.headers = headers
        self.source_path = self._format_source_path(source_path)
        self.estimated_row_count = estimated_row_count
        self.async_write = async_write
        self.queue_size = queue_size
        self.batch_size = batch_size
        self.row_count = 0

        self._rows = rows
        self._closed = False
        self._writer_metadata = writer_metadata or {}
        self._write_batch = []
        self._table_name = None
        self._object_columns = None
        self._column_map = None
        self._is_lava_backed = False

    def _format_source_path(self, source_path):
        if source_path and self._source_path_formatter:
            return self._source_path_formatter(source_path)
        return source_path

    def set_headers(self, headers):
        """Set or replace the result headers."""
        self.headers = headers
        return self

    def set_source_path(self, source_path):
        """Set or replace the source path metadata."""
        self.source_path = self._format_source_path(source_path)
        return self

    def set_estimated_row_count(self, estimated_row_count):
        """Set an advisory row count for progress reporting."""
        self.estimated_row_count = estimated_row_count
        return self

    def add_estimated_row_count(self, rows):
        """Increase the advisory row count when a module discovers more input."""
        if rows is None:
            return self
        if self.estimated_row_count is None:
            self.estimated_row_count = 0
        self.estimated_row_count += rows
        return self

    @property
    def progress_ratio(self):
        """Return best-effort row progress, or None when the estimate is unknown."""
        if not self.estimated_row_count:
            return None
        return self.row_count / self.estimated_row_count

    @property
    def is_lava_backed(self):
        """Return True when rows have already been written to the LAVA table."""
        return self._is_lava_backed

    @property
    def table_name(self):
        """Return the LAVA table name used by this result, if initialized."""
        return self._table_name

    @property
    def object_columns(self):
        """Return LAVA object column metadata for this result."""
        return self._object_columns

    @property
    def column_map(self):
        """Return LAVA column mapping metadata for this result."""
        return self._column_map

    def _ensure_writer(self):
        """Create the LAVA artifact table the first time writer mode needs it."""
        if self._is_lava_backed:
            return
        if self._rows is not None:
            raise ValueError("Cannot use add_row() on an ArtifactResult created with rows=")
        if not self.headers:
            raise ValueError("ArtifactResult headers must be set before adding rows")

        from scripts.lavafuncs import lava_process_artifact

        self._table_name, self._object_columns, self._column_map = lava_process_artifact(
            self._writer_metadata.get("category", ""),
            self._writer_metadata.get("module_name", ""),
            self._writer_metadata.get("artifact_name", ""),
            self.headers,
            None,
            func_name=self._writer_metadata.get("func_name"),
            data_views=self._writer_metadata.get("data_views"),
            artifact_icon=self._writer_metadata.get("artifact_icon"),
            source_path=self.source_path,
        )
        self._is_lava_backed = True

    def _flush_batch(self):
        """Write any queued rows to the LAVA table."""
        if not self._write_batch:
            return

        from scripts.lavafuncs import lava_insert_sqlite_data

        rows = self._write_batch
        self._write_batch = []
        inserted_count = lava_insert_sqlite_data(
            self._table_name,
            rows,
            self._object_columns,
            self.headers,
            self._column_map,
            batch_size=self.batch_size,
            async_write=self.async_write,
            queue_size=self.queue_size,
        )
        self.row_count += inserted_count

    def add_row(self, row):
        """Add one row to the result and flush periodically to LAVA."""
        if self._closed:
            raise ValueError("Cannot add a row to a closed artifact result")
        self._ensure_writer()
        self._write_batch.append(row)
        if len(self._write_batch) >= self.batch_size:
            self._flush_batch()
        return self

    def append(self, row):
        """Alias for add_row() for modules that prefer list-like naming."""
        return self.add_row(row)

    def extend(self, rows):
        """Add rows from an iterable."""
        for row in rows:
            self.add_row(row)
        return self

    def set_row_count(self, row_count):
        """Set the exact row count after a streaming writer consumes rows."""
        self.row_count = row_count
        return self

    def flush(self):
        """Flush pending writer rows to LAVA."""
        if self._is_lava_backed:
            self._flush_batch()
        return self

    def close(self):
        """Flush pending rows and finalize streamed LAVA metadata."""
        if self._closed:
            return
        self.flush()
        if self._is_lava_backed:
            from scripts.lavafuncs import lava_update_artifact_record_count

            lava_update_artifact_record_count(
                self._writer_metadata.get("category", ""),
                self._table_name,
                self.row_count,
            )
        self._closed = True

    def cleanup(self):
        """Release any pending writer state."""
        self.close()

    def __len__(self):
        if self.row_count or self._write_batch:
            return self.row_count + len(self._write_batch)
        if isinstance(self._rows, list):
            return len(self._rows)
        return self.estimated_row_count or 0

    def __bool__(self):
        if self._is_lava_backed:
            return True
        if self._write_batch:
            return True
        if self._rows is None:
            return False
        if isinstance(self._rows, list):
            return bool(self._rows)
        return True

    def __iter__(self):
        return iter(self._rows)
