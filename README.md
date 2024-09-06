# Microphone Monitor App

This is a Python application that monitors your microphone input and displays the volume level in real-time. It also provides a countdown feature triggered by a specified volume level.

## Features

- **Microphone Selection:** Choose from available input devices on your system.
- **Volume Monitoring:** Displays the current volume level of the selected microphone.
- **Volume Trigger:** Set a volume threshold to trigger a countdown.
- **Countdown Timer:** Start a countdown when the volume exceeds the trigger. Plays beeps during the countdown and finishes with a sound notification.
- **Simulated Key Press:** Option to simulate pressing `Ctrl + P` after the countdown finishes.

## Requirements

- Python 3.x
- Tkinter (for the GUI)
- `sounddevice` (for microphone input)
- `playsound` (for audio playback)
- `numpy` (for volume calculation)
- `ctypes` (for simulating keypress)

Install the required dependencies using pip:

```bash
pip install sounddevice playsound numpy
```
