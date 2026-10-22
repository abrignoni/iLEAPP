/* Shared by the offline reader and its fabricated controls; no browser dependencies. */
'use strict';
const ReaderControls = (() => {
  function epoch(value) {
    if (value === null || value === undefined || typeof value === 'boolean' ||
        (typeof value === 'string' && !value.trim())) return null;
    const number = Number(value);
    return Number.isFinite(number) && Number.isFinite(new Date(number * 1000).getTime()) ? number : null;
  }
  const zones = new Map();
  function zone(value) {
    const requested = value === 'System' ? Intl.DateTimeFormat().resolvedOptions().timeZone : value;
    const key = requested || 'UTC';
    if (!zones.has(key)) zones.set(key, new Intl.DateTimeFormat('en-US', {timeZone: key}).resolvedOptions().timeZone);
    return zones.get(key);
  }
  const formatters = new Map();
  function parts(value, timeZone = 'UTC') {
    const number = epoch(value);
    if (number === null) return null;
    const key = zone(timeZone);
    if (!formatters.has(key)) formatters.set(key, new Intl.DateTimeFormat('en-US', {
      timeZone: key, year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', second: '2-digit', fractionalSecondDigits: 3,
      hourCycle: 'h23', timeZoneName: 'longOffset'
    }));
    return Object.fromEntries(formatters.get(key).formatToParts(new Date(number * 1000))
      .filter(part => part.type !== 'literal').map(part => [part.type, part.value]));
  }
  function day(value, timeZone = 'UTC') {
    const p = parts(value, timeZone);
    return p ? p.year.padStart(4, '0') + '-' + p.month + '-' + p.day : '';
  }
  function stamp(value, options = {}) {
    const p = parts(value, options.timeZone || 'UTC');
    if (!p) return 'Date not retained';
    const date = options.dateFormat === 'mdy' ? `${p.month}/${p.day}/${p.year}` :
      options.dateFormat === 'dmy' ? `${p.day}/${p.month}/${p.year}` : `${p.year.padStart(4, '0')}-${p.month}-${p.day}`;
    const hour = options.clock === '12' ? String(Number(p.hour) % 12 || 12).padStart(2, '0') : p.hour;
    const suffix = options.clock === '12' ? (Number(p.hour) < 12 ? ' AM' : ' PM') : '';
    const fraction = p.fractionalSecond && p.fractionalSecond !== '000' ? '.' + p.fractionalSecond : '';
    const offset = p.timeZoneName === 'GMT' ? 'UTC+00:00' : p.timeZoneName.replace('GMT', 'UTC');
    return `${date} ${hour}:${p.minute}:${p.second}${fraction}${suffix} [${zone(options.timeZone || 'UTC')} ${offset}]`;
  }
  function inRange(row, options) {
    if (!options.from && !options.to) return options.includeUndated !== false || epoch(row.created) !== null;
    const key = day(row.created, options.timeZone || 'UTC');
    if (!key) return options.includeUndated !== false;
    return (!options.from || key >= options.from) && (!options.to || key <= options.to);
  }
  function compareTime(a, b, descending = false) {
    const first = epoch(a), second = epoch(b);
    if (first === null) return second === null ? 0 : 1;
    if (second === null) return -1;
    return descending ? second - first : first - second;
  }
  function compareRows(a, b, order = 'oldest') {
    if (a.kind === 'post' && b.kind !== 'post') return -1;
    if (b.kind === 'post' && a.kind !== 'post') return 1;
    return compareTime(a.created, b.created, order === 'newest') ||
      String(a.table).localeCompare(String(b.table)) || a.rowid - b.rowid;
  }
  function groupTime(group, descending) {
    const times = (group.viewRows || group.rows).map(row => epoch(row.created)).filter(value => value !== null);
    return times.length ? (descending ? Math.max(...times) : Math.min(...times)) : null;
  }
  function compareGroups(a, b, order = 'context') {
    let result = 0;
    if (order === 'newest' || order === 'oldest') result = compareTime(groupTime(a, order === 'newest'), groupTime(b, order === 'newest'), order === 'newest');
    else if (order === 'title') result = a.title.localeCompare(b.title);
    else if (order === 'title-desc') result = b.title.localeCompare(a.title);
    else if (order === 'count') result = (b.viewRows || b.rows).length - (a.viewRows || a.rows).length;
    else if (order === 'comments') result = (b.viewRows || b.rows).filter(row => row.kind === 'comment').length - (a.viewRows || a.rows).filter(row => row.kind === 'comment').length;
    else if (a.kind.endsWith('_history') || order === 'source') {
      result = a.rows[0].source.localeCompare(b.rows[0].source);
      if (!result) result = compareTime(a.rows[0].fields['List Position (zero-based)'], b.rows[0].fields['List Position (zero-based)']);
    } else result = b.comments - a.comments || a.title.localeCompare(b.title);
    return result || a.id.localeCompare(b.id);
  }
  function csvCell(value) {
    let text = value === null || value === undefined ? '' : String(value);
    // Protect spreadsheet consumers. Exact values remain in the raw JSON column/export.
    if (/^[\t\r\n]/.test(text) || /^\s*[=+\-@]/.test(text)) text = "'" + text;
    return '"' + text.replaceAll('"', '""') + '"';
  }
  function exportBundle(rows, metadata) {
    return {format: 'ileapp-reddit-reader-export-v1', ...metadata, count: rows.length,
      records: rows.map(row => ({...row, displayCreated: stamp(row.created, metadata.settings),
        createdUTC: epoch(row.created) === null ? '' : new Date(epoch(row.created) * 1000).toISOString()}))};
  }
  function csv(bundle) {
    const headings = ['Exported UTC','Export scope','Section','View settings JSON','Artifact','Export row','Kind',
      'Account','Source reference','Record ID','Post ID','Title','Community','Author','Text','Date meaning',
      'Created epoch seconds (UTC as exported)','Created UTC','Displayed date','Raw fields JSON','Relationships JSON'];
    const lines = [headings];
    for (const row of bundle.records) lines.push([bundle.exportedAtUTC,bundle.scope,bundle.section,
      JSON.stringify(bundle.settings),row.table,row.rowid,row.kind,row.account,row.source,row.id,row.postId,
      row.title,row.community,row.author,row.text,row.dateLabel,row.created,row.createdUTC,row.displayCreated,
      JSON.stringify(row.fields),JSON.stringify(row.links)]);
    return '\ufeff' + lines.map(line => line.map(csvCell).join(',')).join('\r\n') + '\r\n';
  }
  return {epoch, zone, parts, day, stamp, inRange, compareTime, compareRows, compareGroups, csvCell, exportBundle, csv};
})();
if (typeof module !== 'undefined' && module.exports) module.exports = ReaderControls;
