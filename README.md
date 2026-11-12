# pseudo-event-blink

Turning normal camera frames into event camera style output (ON/OFF events).
ON events (pixel got brighter) show as red, OFF events (pixel got darker) show as blue.

There are two ways of making events in here:
- Log: compares the log of the brightness, threshold is 0.2 (about a 22% change)
- Subtraction (NoLog): compares the raw brightness, threshold is in grey levels (30 by default)

## Setup

Needs Python with opencv and numpy:

    pip install opencv-python numpy

The Picamera files also need picamera2, which comes with Raspberry Pi OS.

## Webcam_Event_Conversion

Runs on a laptop webcam.

- webcam_to_event_Log.py - basic log version
- webcam_to_event_Log2.py - lookup-table log version
- webcam_to_event_Log3.py - 2D lookup log version
- webcam_to_event_NoLog.py - basic subtraction version
- webcam_to_event_NoLog2.py - 8-bit subtraction version

To use: run the file. Two windows open, the normal webcam and the events.
Press q (with one of the windows clicked) to stop.

When it stops it prints the threshold, resolution, number of frames,
average time per frame and average conversion time.

To change the threshold, edit THRESHOLD at the top of the file.
If you have more than one camera, change the 0 in cv2.VideoCapture(0).

The classes in these files can be imported into other files without
starting the webcam. 
These are used to test and compare different event-generation algorithms 
before they are added to the Raspberry Pi implementations:

    from Webcam_Event_Conversion.webcam_to_event_Log import PseudoEventCamera
    from Webcam_Event_Conversion.webcam_to_event_Log2 import PseudoEventCamera2
    from Webcam_Event_Conversion.webcam_to_event_Log3 import PseudoEventCamera3
    from Webcam_Event_Conversion.webcam_to_event_NoLog import PseudoEventCameraNL
    from Webcam_Event_Conversion.webcam_to_event_NoLog2 import PseudoEventCameraNL2

## Webcam_Comparison

- comparison.py - times the currently designed methods on the same video

To use: save a video as "EventComparisonFile.mp4" in the "Webcam_Comparison" directory, then run it.
It runs 5 times for each method, prints "done" when finished, and saves the
timings to results.csv. results.csv gets wiped and rewritten every run.

Close results.csv in Excel before running or it won't be able to write to it.

It imports from Webcam_Event_Conversion, so run it from PyCharm or from the
project folder:

    python -m Webcam_Comparison.comparison

## Picamera_Event_Conversion

Runs on the Raspberry Pi with the Pi camera.

- picamera_conversion.py - log version
- picamera_subtraction_conversion.py - subtraction version

To use: run the file on the Pi (needs the Pi desktop or a screen, since it
opens a window). Press q in the Events window or Ctrl+C in the terminal to stop.
It prints the fps every second or so while running.

Settings at the top of the file:
- THRESHOLD - event threshold
- FRAMERATE - camera fps (30 by default)
- FRAMEWIDTH, FRAMEHEIGHT - resolution (640x480 by default)
- SHOW_UNPROCESSED - set to True to also show the normal camera feed

Exposure and white balance are locked so the camera doesn't change brightness
on its own (that would cause fake events).
