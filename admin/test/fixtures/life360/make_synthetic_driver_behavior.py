#!/usr/bin/env python3
"""Fabricate Life360 diagnostic logs; no subject data is copied from an extraction."""
import argparse
from pathlib import Path
import zipfile


def build_logs(root):
    """Create independent fabricated records, including a warning before a later alert."""
    directory = Path(root) / 'MainApplication' / 'Logs'
    directory.mkdir(parents=True, exist_ok=True)
    prefix = 'Life360[100:200] I | '
    records = [
        '2026-01-15T12:28:00.000+0530 ' + prefix + '[DriverBehavior | ArityAdapter] - startAccelerometerUpdates',
        '2026-01-15T12:29:00.010+0530 ' + prefix + '[DriverBehavior | DvBArity] - SDK warning: {\n'
        '    message = "Accelerometer anomaly detected - collision capability will be deactivated for the trip.";\n}',
        '2026-01-15T12:29:00.011+0530 ' + prefix + '[Metrics] - accelerometer-anomaly-detected',
        '2026-01-15T12:30:30.100+0530 ' + prefix + '[DriverBehavior | DvBArity] - Collision detected!',
        '2026-01-15T12:30:30.120+0530 ' + prefix + '[DriverBehavior | DvBArity] - '
        'Confidence: 0.8125 | startTimestamp: 2026-01-15 07:00:00 +0000 | '
        'endTimestamp: 2026-01-15 07:00:30 +0000 | location: 0.5, -150.5',
        '2026-01-15T12:30:30.625+0530 ' + prefix + '[DriverBehavior] - Crash detected: '
        'TripID: synthetic-trip-a EventID: 00000000-0000-0000-0000-00000000d101 '
        'Timestamp: 2026-01-15 07:00:30 +0000 Event Type: crash Location: <0.5, -150.5> '
        'Accuracy: 45.0 UnmappedSetting: keep-me Speed: 11.176',
        '2026-01-15T12:30:30.640+0530 ' + prefix + '[DriverBehavior] - '
        'High confidence collision detected. Deactivate recording for this trip!',
        '2026-01-15T12:30:30.990+0530 ' + prefix + '[DriverBehavior | DvBArity] - '
        'Data exchange type: collision payload size: 128 bytes',
        '2026-01-15T12:31:00.000+0530 ' + prefix + '[DriverBehavior] - '
        'Collision diagnostic variant: syntheticQuality=unknown',
        '2026-01-15T12:31:01.000+0530 ' + prefix + '[Unrelated] - Crash detected: unrelated component',
    ]
    main_log = directory / 'com.life360.safetymap synthetic.log'
    main_log.write_text('\n'.join(records) + '\n', encoding='utf-8')
    sidecar = directory / 'com.life360.safetymap.sidecar synthetic.log'
    sidecar.write_text(
        '2026-01-15 07:02:00.250+0000 Sidecar[300:400] I | [DriverBehavior] - Crash detected: '
        'TripID: synthetic-trip-b EventID: 00000000-0000-0000-0000-00000000d102 '
        'Timestamp: 2026-01-15 07:02:00.125 +0000 Event Type: crash Location: <-0.5, -151.5> '
        'Accuracy: 0 Speed: 0\n', encoding='utf-8')
    return [main_log, sidecar]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--containers', type=int, default=1)
    arguments = parser.parse_args()
    for number in range(arguments.containers):
        build_logs(arguments.output / 'private/var/mobile/Containers/Shared/AppGroup' /
                   f'00000000-0000-0000-0000-{0xD000 + number:012x}')
    archive = arguments.output.with_suffix('.zip')
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as output:
        for path in sorted(arguments.output.rglob('*')):
            if path.is_file():
                member = zipfile.ZipInfo(path.relative_to(arguments.output).as_posix(),
                                         date_time=(2026, 1, 15, 12, 0, 0))
                member.compress_type = zipfile.ZIP_DEFLATED
                output.writestr(member, path.read_bytes())
    print(archive)


if __name__ == '__main__':
    main()
