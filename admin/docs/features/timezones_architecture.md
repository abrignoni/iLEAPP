# Architectural Decision Record: Timezone Handling in Project

## Status
Proposed

## Context
Our project deals with timestamp data from various sources, including SQL databases and plist files. We need a consistent approach to handle timezones across different components of our system, including LAVA, TSV, and KML outputs. The current implementation varies across modules, leading to inconsistencies and potential errors in timestamp processing.

For ongoing discussion and updates related to this ADR, please refer to [Issue #850: Timezone Handling](https://github.com/abrignoni/iLEAPP/issues/850).

Key issues:
1. Some modules produce timestamps without timezone information.
2. The `lava_insert_sqlite_data` function expects timestamps in ISO format with timezone.
3. Different output formats (LAVA, TSV, KML) have different timezone requirements.
4. The `timezone_offset` parameter is currently only supported in iLEAPP.
5. The need to maintain compatibility with TSV and KML outputs, which benefit from timezone adjustments.
6. Consideration of features in comparable commercial tools, which often include timezone adjustment capabilities.

## Decision
We propose the following approach for handling timezones:

1. All modules should provide timestamps in one of two formats:
   a. Unix timestamps (assumed to be in UTC)
   b. ISO 8601 format with timezone specified (e.g., "2021-12-12 12:54:37+00:00")

2. Maintain the `timezone_offset` parameter as an input to iLEAPP:
   - This parameter will continue to be used for adjusting timezones in TSV and KML outputs.
   - It provides consistency with features found in comparable commercial tools.
   - For LAVA output, all timestamps will be converted to UTC, with timezone adjustments handled by LAVA's display features.

3. Update timestamp conversion functions to handle null or empty values gracefully.

4. For LAVA, all timestamps should be converted to UTC, with timezone adjustments handled by LAVA's display features.

## Consequences
Positive:
- Consistent timestamp handling across all modules
- Improved compatibility with LAVA's requirements
- Maintained support for timezone adjustments in TSV and KML outputs
- Maintained feature parity with commercial tools regarding timezone adjustments in direct outputs (TSV, KML)
- Flexibility for users to adjust timezones in non-LAVA outputs without requiring changes to the source data

Negative:
- Requires updates to existing modules to ensure compliance with new standards
- May introduce temporary inconsistencies during the transition period

Risks:
- Potential for data misinterpretation if timezone information is not correctly propagated through the system

## Implementation
1. Update `ilapfuncs.py` to include robust timestamp conversion functions that:
   - Convert Unix timestamps to ISO 8601 format with UTC timezone
   - Add timezone information to ISO format timestamps if missing
   - Handle null or empty timestamp values gracefully

2. Modify the `lava_insert_sqlite_data` function to accept both Unix timestamps and ISO 8601 format timestamps.

3. Update all modules to use the new timestamp conversion functions when processing data.

4. Ensure the `timezone_offset` parameter in iLEAPP is properly documented and its usage is clear for developers:
   - It should be applied to timestamp adjustments for TSV and KML outputs.
   - It should be ignored for LAVA output preparation, as LAVA handles timezone display internally.

5. Update the documentation for users to clarify how the `timezone_offset` parameter affects different output types.

## Notes
- Further discussion may be needed to determine if LAVA should completely replace other report types in the future.
- Consider creating a comprehensive test suite to verify correct timezone handling across all modules and output formats.
- Regular code reviews should include checks for proper timestamp formatting to ensure ongoing compliance with this decision.
- The decision to maintain the `timezone_offset` parameter balances the needs of different output formats and user expectations based on comparable tools in the industry.
