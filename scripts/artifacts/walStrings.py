__artifacts_v2__ = {
    "walStrings": {
        "name": "Database Journal Strings - Summary",
        "description": "Summarizes ASCII strings extracted from SQLite Write-Ahead Logs (WAL) and Journals.",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-04-30",
        "last_update_date": "2026-06-07",
        "requirements": "none",
        "category": "Database Metadata",
        "notes": "Generates text files with strings found in WAL/Journal files.",
        "paths": ('**/*-wal', '**/*-journal'),
        "output_types": "standard",
        "artifact_icon": "database",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 373 rows",
            "dexter_ios18": "iOS 18.3.2 | 909 rows",
            "felix_ios17": "iOS 17.6.1 | 502 rows",
            "fsfull002_ios17": "iOS 17.1 | 461 rows",
            "hc_ios18_7": "iOS 18.7.8 | 814 rows",
            "iphone11_ios17": "iOS 17.3 | 1012 rows",
            "iphone12_ios18": "iOS 18.7 | 654 rows",
            "iphone14plus_ios18": "iOS 18.0 | 490 rows",
            "otto_ios17": "iOS 17.5.1 | 813 rows",
            "abe_ios16": "iOS 16.5 | 862 rows",
            "felix23_ios16": "iOS 16.5 | 467 rows",
            "hickman_ios13": "iOS 13.3.1 | 381 rows",
            "hickman_ios14": "iOS 14.3 | 482 rows",
            "jess_ios15": "iOS 15.0.2 | 418 rows",
            "magnet_ios16": "iOS 16.1.1 | 478 rows",
        },
        "html_columns": ['Output File']
    },
    "walStringsDetails": {
        "name": "Database Journal Strings - Details",
        "description": "Provides searchable ASCII strings extracted from SQLite WAL and journal files.",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-04-30",
        "last_update_date": "2026-06-07",
        "requirements": "none",
        "category": "Database Metadata",
        "notes": "LAVA-only detailed string output.",
        "paths": ('**/*-wal', '**/*-journal'),
        "output_types": "lava_only",
        "artifact_icon": "database",
        "sample_data": {
            "ctf2020_ios12": "iOS 12.4 | 789973 rows",
            "dexter_ios18": "iOS 18.3.2 | 1161158 rows",
            "felix_ios17": "iOS 17.6.1 | 788273 rows",
            "fsfull002_ios17": "iOS 17.1 | 805831 rows",
            "hc_ios18_7": "iOS 18.7.8 | 1208783 rows",
            "iphone11_ios17": "iOS 17.3 | 1279032 rows",
            "iphone12_ios18": "iOS 18.7 | 565084 rows",
            "iphone14plus_ios18": "iOS 18.0 | 729482 rows",
            "otto_ios17": "iOS 17.5.1 | 1199161 rows",
            "abe_ios16": "iOS 16.5 | 1111184 rows",
            "felix23_ios16": "iOS 16.5 | 757035 rows",
            "hickman_ios13": "iOS 13.3.1 | 230298 rows",
            "hickman_ios14": "iOS 14.3 | 791401 rows",
            "jess_ios15": "iOS 15.0.2 | 161269 rows",
            "magnet_ios16": "iOS 16.1.1 | 246100 rows",
        }
    }
}

import os
import re
from pathlib import Path
from scripts.ilapfuncs import (
    artifact_processor,
    logfunc
    )

ASCII_STRINGS_RE = re.compile(rb'[\x20-\x7e]{4,}')
_extraction_cache = {}


def extract_strings(file_path):
    with open(file_path, 'rb') as file:
        data = file.read()

    strings = {}
    total_matches = 0

    for match in ASCII_STRINGS_RE.finditer(data):
        raw_value = match.group()
        value = raw_value.decode('ascii').strip()
        if len(value) < 4:
            continue

        total_matches += 1
        leading_spaces = len(raw_value) - len(raw_value.lstrip())
        offset = match.start() + leading_spaces

        if value in strings:
            strings[value]['count'] += 1
        else:
            strings[value] = {
                'offset': offset,
                'count': 1
            }

    return strings, total_matches


def process_journal_files(context):
    files_found = context.get_files_found()
    report_folder = context.get_report_folder()
    cache_key = (
        tuple(str(file_path) for file_path in files_found),
        str(report_folder)
    )
    if cache_key in _extraction_cache:
        return _extraction_cache[cache_key]

    summary_data = []
    summary_html_data = []
    detail_data = []
    source_path_ref = ''
    report_number = 1

    for file_found in files_found:
        file_found = str(file_found)
        source_path = context.get_relative_path(file_found)

        if not source_path_ref:
            source_path_ref = source_path

        try:
            if Path(file_found).stat().st_size == 0:
                continue
            strings, total_matches = extract_strings(file_found)
        except OSError as error:
            logfunc(f"Error reading {file_found}: {error}")
            continue

        if not strings:
            continue

        journal_name = os.path.basename(file_found)
        output_filename = f"{report_number}_{journal_name}.txt"
        output_path = os.path.join(report_folder, output_filename)

        try:
            with open(output_path, 'w', encoding='utf-8') as output_file:
                for value, string_info in strings.items():
                    output_file.write(
                        f"{string_info['offset']}\t"
                        f"{string_info['count']}\t{value}\n"
                    )
        except OSError as error:
            logfunc(f"Error writing report file {output_path}: {error}")
            continue

        relative_output_path = (
            f'{os.path.basename(report_folder)}/{output_filename}'
        )
        report_link = (
            f'<a href="{relative_output_path}" target="_blank" '
            f'style="color:blue">{journal_name}</a>'
        )
        summary_row = (
            relative_output_path,
            journal_name,
            total_matches,
            len(strings),
            source_path
        )
        summary_data.append(summary_row)
        summary_html_data.append((report_link, *summary_row[1:]))

        for value, string_info in strings.items():
            detail_data.append((
                value,
                len(value),
                string_info['offset'],
                string_info['count'],
                journal_name,
                source_path
            ))

        report_number += 1

    result = (
        summary_data,
        summary_html_data,
        detail_data,
        source_path_ref
    )
    _extraction_cache[cache_key] = result
    return result


@artifact_processor
def walStrings(context):
    data_list, html_data_list, _, source_path = process_journal_files(context)
    data_headers = (
        'Output File',
        'Filename',
        'Total Matches',
        'Unique Strings',
        'Source File'
    )

    if not data_list:
        logfunc("No strings found in WAL/Journal files.")
        return data_headers, [], source_path

    return data_headers, (data_list, html_data_list), source_path


@artifact_processor
def walStringsDetails(context):
    _, _, data_list, source_path = process_journal_files(context)
    data_headers = (
        'String',
        'Length',
        'First Byte Offset',
        'Occurrence Count',
        'Filename',
        'Source File'
    )

    return data_headers, data_list, source_path
