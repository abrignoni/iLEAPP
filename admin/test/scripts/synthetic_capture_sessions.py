#!/usr/bin/env python3
"""Build a SYNTHETIC Unified Log export for the camera and microphone capture artifacts.

The output has the shape of ``log show --style json``: a JSON list of records with
``timestamp``, ``processImagePath``, ``processID``, ``subsystem``, ``category``,
``eventMessage`` and ``traceID`` (iLEAPP's logarchive artifact accepts any ``logarchive*.json``).

Every process, app id and PID is invented (``com.example.*``, ``Fake*``, PIDs 3101 and up) and every
timestamp is fixed, so the output is reproducible and carries nothing from a real device. The message
shapes follow lines read on iOS 26.6 and iOS 27.0 logs; the shapes the real logs did not contain are
marked ``INVENTED SHAPE`` below, and they exist to exercise a branch, not to describe a device.

    python synthetic_capture_sessions.py [output.json]

``build_lines()`` labels each line 'listed' (appears in the capture sessions artifact), 'held' (collected into
logarchive_artifacts but not listed), 'power' (streaming artifact), 'indicator' (recording indicator artifact) or
'never' (must not be collected); ``lines_of(kind)`` gives the Row Numbers the import assigns to them.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone

_ZONE = timezone(timedelta(hours=-5))
_BASE = datetime(2026, 3, 14, 10, 0, 0, tzinfo=_ZONE)

FIXTURE_NAME = 'logarchive_synthetic_capture.json'

DAEMON = '/usr/libexec/cameracaptured'
CAMERA_SUBSYSTEM = 'com.apple.cameracapture'
SPRINGBOARD = '/System/Library/CoreServices/SpringBoard.app/SpringBoard'
FAKE_CAM = '/private/var/containers/Bundle/Application/FAKE0000-0000-0000-0000-000000000001/FakeCam.app/FakeCam'

STATE_27 = ('ClientStartedSession:{started} Cam/Audio:{cam}/{aud} bg:{bg} prewarming:0 micStolen:{mic} '
            'multitasking:0 pip:0 cameraStolen:{cams} pressured:0 interruptions:0 runtimeError:0 '
            'stopRequired:0 shouldRun:{started} interruptionError:0 sessionStatus:{status}')


def _tag(address, pid, app='com.example.fakecam'):
    return f'<{address}[{pid}][{app}]>' if app else f'<{address}[{pid}]>'


def _state(started, cam, aud, bg, mic, cams, status, suffix=''):
    text = STATE_27.format(started=started, cam=cam, aud=aud, bg=bg, mic=mic, cams=cams, status=status)
    return f'{text} {suffix}'.rstrip()


def _session(function, tag, text):
    return f'<<<< FigCaptureSession >>>> {function}: {tag} {text}'.rstrip()


def build_lines():
    """(seconds after the base time, process path, pid, subsystem, category, message, tag) in file order.

    The last element names the branch each line exercises: 'listed' lines appear in the artifact
    named in ``EXPECTED``; 'held' lines are collected into logarchive_artifacts but not listed;
    'never' lines are not collected at all.
    """
    cam = _tag('0x7f0a11c000', 3101)
    prewarm = _tag('0x7f0a11d000', 3102, 'com.example.fakeprewarm')
    video = _tag('0x7f0a11e000', 3103, 'com.example.fakevideo')
    noapp = _tag('0x7f0a11f000', 3105, None)
    lines = []

    def add(sec, message, kind, process=DAEMON, pid=118, subsystem=CAMERA_SUBSYSTEM, category=''):
        lines.append((sec, process, pid, subsystem, category, message, kind))

    # iOS 27 form. A client creates a session, starts it, runs it in the background, loses the
    # camera and the microphone, then stops it.
    add(0.100, '<<<< FigCaptureSession >>>> FigCaptureSessionCreate: Creating session for PID 3101', 'listed')
    add(0.101, _session('FigCaptureSessionCreate', cam, 'New session created.'), 'listed')
    add(0.102, _session('captureSession_SetConfiguration', cam, _state(0, 0, 0, 0, 0, 0, 'Idle', 'Update:0')), 'held')
    add(5.000, _session('captureSession_updateSessionStateWithApplicationAndLayoutState', cam,
                        _state(0, 0, 0, 1, 0, 0, 'Idle', 'Update:0')), 'held')
    add(10.000, _session('captureSession_StartRunning', cam, 'Called'), 'listed')
    add(10.001, _session('captureSession_StartRunning', cam,
                         _state(1, 1, 0, 0, 0, 0, 'Idle', 'ClientStartRunning')), 'listed')
    add(10.002, _session('captureSession_transitionToSessionStatus', cam, 'Idle -> Starting Running'), 'listed')
    add(10.290, _session('captureSession_transitionToSessionStatus', cam, 'Starting Running -> Running'), 'listed')
    add(10.291, _session('captureSession_transitionToSessionStatus', cam, 'Starting took 289.6ms'), 'held')
    add(20.000, _session('captureSession_updateSessionStateWithApplicationAndLayoutState', cam,
                         _state(1, 1, 0, 1, 0, 0, 'Running', 'Update:1')), 'listed')
    add(25.000, _session('captureSession_updateSessionStateWithApplicationAndLayoutState', cam,
                         _state(0, 1, 0, 0, 0, 1, 'Idle', 'Update:1')), 'listed')
    # INVENTED SHAPE: no sample held an audio flag or a mic-stolen flag at 1; the flags sit where the
    # real format puts them.
    add(30.000, _session('captureSession_updateSessionStateWithApplicationAndLayoutState', cam,
                         _state(1, 0, 1, 0, 1, 0, 'Running', 'Update:1')), 'listed')
    add(40.000, _session('captureSession_StopRunning', cam, 'Called'), 'listed')
    add(40.001, _session('captureSession_StopRunning', cam,
                         _state(1, 1, 0, 0, 0, 0, 'Running', 'ClientStopRunning')), 'listed')
    add(40.002, _session('captureSession_transitionToSessionStatus', cam, 'Running -> Stopping Running'), 'listed')
    add(40.050, _session('captureSession_transitionToSessionStatus', cam, 'Stopping Running -> Idle'), 'listed')
    add(40.060, _session('captureSession_didStopRunning', cam, 'Stopped running, tearing down graph'), 'listed')
    add(40.061, _session('captureSession_didStopRunning', cam, 'disabling memory pool'), 'held')
    add(60.000, _session('FigCaptureSessionDetachFromClient_block_invoke', cam,
                         'detaching from client with session 7F0A11C000'), 'listed')

    # A session that is created and configured but never started.
    add(100.000, '<<<< FigCaptureSession >>>> FigCaptureSessionCreate: Creating session for PID 3102', 'listed')
    add(100.001, _session('FigCaptureSessionCreate', prewarm, 'New session created.'), 'listed')
    add(100.002, _session('captureSession_SetConfiguration', prewarm, _state(0, 1, 0, 0, 0, 0, 'Idle', 'Update:0')), 'held')

    # A tag with no app id between the second pair of brackets.
    add(110.000, _session('FigCaptureSessionCreate', noapp, 'New session created.'), 'listed')

    # iOS 26.6 form: captureSession_updateRunningCondition, no sessionStatus or runtimeError.
    add(200.000, '<<<< FigCaptureSession >>>> FigCaptureSessionCreate: Creating session for PID 3103', 'listed')
    add(200.001, _session('FigCaptureSessionCreate', video, 'New session created.'), 'listed')
    add(200.002, _session('captureSession_updateRunningCondition', video,
                          'ClientStartedSession:0 Cam/Audio:1/0 bg:0 prewarming:0 micStolen:0 multitasking:0 '
                          'pip:0 cameraStolen:0 pressured:0 interruptions:0 active:0 shouldRun:0 (start:0 stop:0)'),
        'held')
    add(210.000, _session('captureSession_StartRunning', video, 'Called'), 'listed')
    add(210.001, _session('captureSession_updateRunningCondition', video,
                          'ClientStartedSession:1 Cam/Audio:1/0 bg:0 prewarming:0 micStolen:0 multitasking:0 '
                          'pip:0 cameraStolen:0 pressured:0 interruptions:0 active:0 shouldRun:1 (start:1 stop:0)'),
        'listed')
    # The lowercase spelling matches the case-insensitive marker and carries no state fields.
    add(210.002, _session('captureSession_updateSessionRunningCondition_block_invoke', video,
                          'Handle clientRequested start:1 stop:0, clientStartedSession:1, shouldRun:1, '
                          'shouldStop:0 sessionStatus:Idle, interruptionError:0, runtimeError:0 cancelled:0 -> Start'),
        'listed')

    # Client-side calls, written by the client process itself.
    add(300.000, '<<<< AVCaptureSession >>>> -[AVCaptureSession startRunning]: (73CCD281A0) (pthread:16DBEB000)',
        'listed', process=FAKE_CAM, pid=3104)
    add(310.000, '<<<< AVCaptureSession >>>> -[AVCaptureSession stopRunning]: (73CCD281A0) (pthread:16DBEB000)',
        'listed', process=FAKE_CAM, pid=3104)

    # Camera daemon lines that are neither session lifecycle nor power log: torch, device vendor, thermal.
    add(400.000, '<<<< FigFlashlightLocal >>>> -[FigFlashlightLocal _postNotification:withValue:]_block_invoke: '
                 '<0x7f0a200000[118][com.apple.springboard]> Posting notification FlashlightLevel with payload {\n'
                 '    FlashlightValue = 1;\n}', 'never')
    add(401.000, '<<<< FigFlashlightLocal >>>> -[FigFlashlightLocal initWithClientType:clientAuditToken:'
                 'clientApplicationID:]: <0x7f0a200000[118][com.apple.springboard]> Created flashlight '
                 '(0x7f0a200010), clientType: AVCaptureDevice Torch.', 'never')
    add(402.000, '<<<< BWFigCaptureDevice >>>> -[BWFigCaptureDevice _setProperty:value:requireSupported:]: '
                 '<0x7f0a210000 FigCaptureDeviceRef(0x7f0a210010), 1, Default>: set ClientIsActive to 1', 'never')
    add(403.000, '<<<< FigCaptureThermalMonitor >>>> -[FigCaptureThermalMonitor _thermalNotification:]: '
                 'Thermal level now 0 (vs. threshold 3)', 'never')
    add(404.000, '<<<< FigCapturePowerLog >>>> cpls_logCameraStreamingPowerEvents: Event 9: {\n'
                 '    CameraType = 1;\n    Streaming = 0;\n    Timestamp = "2026-03-14 10:06:44 +0000";\n}', 'never')

    # Decoys: the same text under another subsystem is not the camera daemon.
    add(500.000, _session('captureSession_StartRunning', cam, _state(1, 1, 0, 0, 0, 0, 'Idle', 'ClientStartRunning')),
        'never', subsystem='com.example.notcamera')
    add(501.000, '<<<< AVCaptureSession >>>> -[AVCaptureSession startRunning]: (73CCD28290) (pthread:16DB5F000)',
        'never', process=FAKE_CAM, pid=3104, subsystem='com.example.notcamera')
    add(502.000, 'FigCaptureLogCameraStreamingPowerEvent: PID: 3101, applicationID: <private>, deviceType: 2, '
                 'streaming: 1, portType: PortTypeBack', 'never', subsystem='com.example.notcamera')

    # Power log lines. Application id redacted, application id in the clear, and a line that matches the
    # marker but not the field pattern.
    add(600.000, '<<<< FigCapturePowerLog >>>> FigCaptureLogCameraStreamingPowerEvent: PID: 3101, '
                 'applicationID: <private>, deviceType: 20, streaming: 1, portType: PortTypeFrontInfrared', 'power')
    add(600.900, '<<<< FigCapturePowerLog >>>> FigCaptureLogCameraStreamingPowerEvent: PID: 3101, '
                 'applicationID: <private>, deviceType: 20, streaming: 0, portType: PortTypeFrontInfrared', 'power')
    # INVENTED SHAPE: the samples held applicationID: <private> only.
    add(610.000, '<<<< FigCapturePowerLog >>>> FigCaptureLogCameraStreamingPowerEvent: PID: 3103, '
                 'applicationID: com.example.fakevideo, deviceType: 2, streaming: 1, portType: PortTypeBack', 'power')
    # INVENTED SHAPE: a later release that reorders the fields would land here.
    add(620.000, '<<<< FigCapturePowerLog >>>> FigCaptureLogCameraStreamingPowerEvent: unrecognised layout', 'power')

    # SpringBoard recording indicator lines.
    for sec, text, kind in (
            (700.000, '[Recording Indicator] Active camera/microphone activity changed:\n{(\n)}', 'indicator'),
            # INVENTED SHAPE: the samples held an empty set only.
            (700.500, '[Recording Indicator] Active camera/microphone activity changed:\n{(\n    Camera\n)}',
             'indicator'),
            (701.000, '[Recording Indicator] creating secure indicator layer for view-dot with Camera', 'indicator'),
            (702.000, '[Recording Indicator] updating live rendering assertion... hasSecureIndicator: YES, '
                      'isActive: NO, windowScene: <private>', 'indicator'),
            (703.000, '[Recording Indicator] Changed high level layer opacity to 0.5 for backlightLuminance '
                      'update 0.5 from: 1.0', 'never'),
            (704.000, '[Recording Indicator] Should force high level layer off... forceOff: NO', 'never')):
        add(sec, text, kind, process=SPRINGBOARD, pid=60, subsystem='com.apple.SpringBoard', category='StatusBarish')
    add(705.000, '[Recording Indicator] Active camera/microphone activity changed:\n{(\n)}', 'never',
        process=SPRINGBOARD, pid=60, subsystem='com.example.notspringboard', category='StatusBarish')
    return lines


def _stamp(seconds):
    return (_BASE + timedelta(seconds=seconds)).strftime('%Y-%m-%d %H:%M:%S.%f%z')


def build_records():
    """The JSON list in file order. traceID is a fixed, invented number per line."""
    records = []
    for index, (sec, process, pid, subsystem, category, message, _kind) in enumerate(build_lines()):
        records.append({
            'traceID': 1000 + index,
            'eventMessage': message,
            'eventType': 'logEvent',
            'source': None,
            'formatString': '%{public}s',
            'activityIdentifier': 0,
            'subsystem': subsystem,
            'category': category,
            'threadID': 4000 + index,
            'senderImageUUID': '00000000-0000-0000-0000-000000000000',
            'senderImagePath': process,
            'machTimestamp': 1000000 + index,
            'messageType': 'Default',
            'processImageUUID': '00000000-0000-0000-0000-000000000001',
            'processUniqueID': pid,
            'processID': pid,
            'processImagePath': process,
            'timestamp': _stamp(sec),
            'timezoneName': '',
            'creatorActivityID': 0,
            'parentActivityIdentifier': 0,
        })
    return records


def to_bytes(records=None):
    return (json.dumps(build_records() if records is None else records, indent=1) + '\n').encode('utf-8')


def lines_of(kind):
    """1-based file positions (the Row Number the import assigns) of the lines of one kind."""
    return [index for index, line in enumerate(build_lines(), start=1) if line[6] == kind]


if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else FIXTURE_NAME
    with open(target, 'wb') as handle:
        handle.write(to_bytes())
    print(f'wrote {target}: {len(build_lines())} records')
