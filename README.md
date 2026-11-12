# pseudo-event-blink

Turning normal camera frames into event camera style output (ON/OFF events).
ON events (pixel got brighter) show as red, OFF events (pixel got darker) show as blue.

There are two ways of making events in here:
- Log: compares the log of the brightness, threshold is 0.2 (about a 22% change)
- Subtraction: compares the raw brightness, threshold is in grey levels (30 by default)

## Setup

Needs Python with opencv and numpy:

    pip install opencv-python numpy

The Pi runner also needs picamera2, which comes with Raspberry Pi OS.

## Event_Conversion

The converters. Each file has one class called PseudoEventCamera with a
step() function that takes a greyscale frame and returns the ON and OFF events.

- conversion_log_1.py - basic log version (default threshold 0.2)
- conversion_log_2.py - lookup-table log version (default threshold 0.2)
- conversion_log_3.py - 2D lookup log version (default threshold 0.2)
- conversion_subtraction_1.py - basic subtraction version (default threshold 30)
- conversion_subtraction_2.py - 8-bit subtraction version (default threshold 30)

These files don't open a camera on their own, they're imported by the runners
and the comparison. Since every class has the same name, swapping method is
just changing the import:

    from Event_Conversion.conversion_log_1 import PseudoEventCamera
    from Event_Conversion.conversion_subtraction_1 import PseudoEventCamera

To use more than one in the same file, rename them on import:

    from Event_Conversion.conversion_log_2 import PseudoEventCamera as PseudoEventCamera2

## Runners

Runs a converter live on a camera. Both use conversion_log_1 by default,
change the import at the top to use a different method.

To change the threshold, edit THRESHOLD at the top of the file.
Leave it as None to use the converter's default.

### webcam_runner.py

Runs on a laptop webcam.

To use: run the file. Two windows open, the normal webcam and the events.
Press q (with one of the windows clicked) to stop.

When it stops it prints the threshold, resolution, number of frames,
average time per frame and average conversion time.

If you have more than one camera, change the 0 in cv2.VideoCapture(0).

### picamera_runner.py

Runs on the Raspberry Pi with the Pi camera.

To use: run the file on the Pi (needs the Pi desktop or a screen, since it
opens a window). Press q in the Events window or Ctrl+C in the terminal to stop.
It prints the fps every second or so while running.

Settings at the top of the file:
- THRESHOLD - event threshold (None for default)
- FRAMERATE - camera fps (30 by default)
- FRAMEWIDTH, FRAMEHEIGHT - resolution (640x480 by default)
- SHOW_UNPROCESSED - set to True to also show the normal camera feed

Exposure and white balance are locked so the camera doesn't change brightness
on its own (that would cause fake events).

## Comparison

- mp4_comparison.py - times every conversion method on the same video
- mp4_comparison_summary.py - averages the results for each method

To use: save a video as "EventComparisonFile.mp4" in the "Comparison"
directory, then run mp4_comparison.py from PyCharm.
It runs 5 times for each method, prints "done" when finished, and saves the
timings to mp4_results.csv. mp4_results.csv gets wiped and rewritten every run.

Then run mp4_comparison_summary.py to print the average total time per frame,
average conversion time and theoretical fps for each method.

Close mp4_results.csv in Excel before running or it won't be able to write to it.
