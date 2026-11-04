"""Rows of the MobileBluetooth LE device tables that an earlier state held and the current state does not.

Shared by bluetoothPairedLE.py and bluetoothOther.py. A device is one Uuid; a row with no Uuid is
compared by all its values. Of the rows an earlier log state holds and the current state does not, one
per device is kept, the one from the newest state, with where in the log it was read.
"""

import os
import sqlite3

from scripts.ilapfuncs import logfunc
from scripts.sqlite_wal import (EARLIER_VERSION, KIND_COMMITTED, KIND_EARLIER, KIND_UNCOMMITTED,
                                NOT_IN_CURRENT, rows_not_in_current)

_WAL_KINDS = (KIND_COMMITTED, KIND_EARLIER, KIND_UNCOMMITTED)
STATE_CURRENT = 'Current'
STATE_NOT_IN_CURRENT = 'Not in current state'


def _read_from(name, item):
    """Where a row was read, in words: the database file without its log, or states of the write-ahead log."""
    parts = []
    if item.first_state is not None:
        first, last = item.first_state, item.last_state
        if first == 0:
            # State 0 is the database file read without its log (sqlite_wal.WalStates.states).
            text = f'{name} without its -wal'
            parts.append(text if last == 0 else f'{text}, through {name}-wal committed state {last}')
        else:
            states = f'state {first}' if first == last else f'states {first} to {last}'
            parts.append(f'{name}-wal, committed {states}')
    if item.earlier_generation:
        first, last = item.earlier_generation
        commits = f'commit {first}' if first == last else f'commits {first} to {last}'
        parts.append(f'{name}-wal, previous log generation, left-over {commits}')
    return '; '.join(parts)


def _rank(item):
    """Orders the states a row was read in, newest last."""
    if item.first_state is not None:
        return (2, item.last_state)
    if item.earlier_generation:
        return (1, item.earlier_generation[1])
    return (0, 0)


def rows_only_in_log(db_path, query, uuid_index, label):
    """[(row values, read from)] for the devices the query returns in an earlier log state and not in the
    current one, newest first-seen state per device, ordered by where they were read."""
    try:
        _columns, found, wal = rows_not_in_current(db_path, query, key_columns=(uuid_index,),
                                                   include=_WAL_KINDS)
    except (sqlite3.Error, OSError) as ex:
        logfunc(f'{label}: write-ahead log not read for {os.path.basename(db_path)}: {ex}')
        return []
    logfunc(f'{label}: {wal.summary()}')
    newest = {}
    earlier_versions = 0
    for item in found:
        if item.status == EARLIER_VERSION:
            earlier_versions += 1
            continue
        if item.status != NOT_IN_CURRENT:
            continue
        uuid = item.values[uuid_index]
        device = ('uuid', uuid) if uuid is not None else ('row', item.values)
        if device not in newest or _rank(item) > _rank(newest[device]):
            newest[device] = item
    if earlier_versions:
        logfunc(f'{label}: {earlier_versions} earlier versions of current rows in the log, not listed')
    name = os.path.basename(db_path)
    kept = sorted(newest.values(), key=_rank)
    return [(tuple(item.values), _read_from(name, item)) for item in kept]
