import tkinter as tk
from tkinter import ttk
import sounddevice as sd
from playsound import playsound
import numpy as np
import threading
import os
import time
import ctypes 

class MicMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Microphone Monitor")
        self.root.geometry("800x600")
        self.root.configure(bg="#2e2e2e")  

        self.font_header = ("Helvetica", 16, "bold")
        self.font_normal = ("Helvetica", 14)

        self.sidebar = tk.Frame(self.root, bg="#3c3c3c", padx=10, pady=20, bd=2, relief="groove")
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)
        self.sidebar.configure(highlightthickness=0, borderwidth=0)

        self.main_body = tk.Frame(self.root, bg="#1e1e1e", padx=20, pady=20, bd=2, relief="groove")
        self.main_body.pack(side="right", expand=True, fill="both", padx=10, pady=10)
        self.main_body.configure(highlightthickness=0, borderwidth=0)

        self.label = tk.Label(self.sidebar, text="Select Microphone:", font=self.font_header, bg="#3c3c3c", fg="white")
        self.label.pack(pady=5)

        self.mic_list = self.get_microphones()
        self.selected_mic = tk.StringVar()
        self.mic_dropdown = ttk.Combobox(self.sidebar, textvariable=self.selected_mic, font=self.font_normal)
        self.mic_dropdown['values'] = self.mic_list
        self.mic_dropdown.pack(pady=5)
        self.mic_dropdown.bind("<<ComboboxSelected>>", self.mic_selected)
        self.apply_dark_theme_to_combobox(self.mic_dropdown)

        self.volume_label = tk.Label(self.sidebar, text="Volume Level:", font=self.font_header, bg="#3c3c3c", fg="white")
        self.volume_label.pack(pady=5)

        self.volume_display = tk.Label(self.sidebar, text="0", font=self.font_normal, bg="#3c3c3c", fg="white")
        self.volume_display.pack(pady=5)

        self.volume_bar = ttk.Progressbar(self.sidebar, orient='horizontal', length=150, mode='determinate')
        self.volume_bar.pack(pady=5)

        self.delay_label = tk.Label(self.sidebar, text="Countdown (seconds):", font=self.font_header, bg="#3c3c3c", fg="white")
        self.delay_label.pack(pady=5)

        self.delay_slider = tk.Scale(self.sidebar, from_=1, to=60, orient='horizontal', font=self.font_normal, bg="#3c3c3c", fg="white", troughcolor="#555", highlightthickness=0, relief="flat")
        self.delay_slider.set(3)  # Default to 3 seconds
        self.delay_slider.pack(pady=5)

        self.trigger_label = tk.Label(self.sidebar, text="Volume Trigger:", font=self.font_header, bg="#3c3c3c", fg="white")
        self.trigger_label.pack(pady=5)

        self.trigger_slider = tk.Scale(self.sidebar, from_=0, to=100, orient='horizontal', font=self.font_normal, bg="#3c3c3c", fg="white", troughcolor="#555", highlightthickness=0, relief="flat")
        self.trigger_slider.set(10)  # Default to 10
        self.trigger_slider.pack(pady=5)

        self.key_press_var = tk.BooleanVar(value=True)  # Default is checked
        self.key_press_checkbox = tk.Checkbutton(self.sidebar, text="Activate Key Press", font=self.font_normal, variable=self.key_press_var, bg="#3c3c3c", fg="white", selectcolor="#2e2e2e")
        self.key_press_checkbox.pack(pady=10)

        self.counter_label = tk.Label(self.main_body, text="Countdown:", font=self.font_header, bg="#1e1e1e", fg="white")
        self.counter_label.pack(pady=50)

        self.counter_value = tk.Label(self.main_body, text="0", font=("Helvetica", 200, "bold"), bg="#1e1e1e", fg="white")  # Larger font size
        self.counter_value.pack(pady=20)

        self.stream = None
        self.monitoring = False
        self.counter_thread = None
        self.counter_running = False
        self.counter_seconds = 0

    def get_microphones(self):
        devices = sd.query_devices()
        mic_list = [dev['name'] for dev in devices if dev['max_input_channels'] > 0]
        return mic_list

    def mic_selected(self, event=None):
        mic_name = self.selected_mic.get()
        for idx, dev in enumerate(sd.query_devices()):
            if dev['name'] == mic_name:
                self.start_monitoring(idx)
                break

    def start_monitoring(self, device_index):
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()

        def audio_callback(indata, frames, time, status):
            volume_norm = np.linalg.norm(indata) * 10
            volume_trigger = self.trigger_slider.get()

            self.volume_display['text'] = f"{int(volume_norm)}"  # Display volume as digits
            self.volume_bar['value'] = min(volume_norm, 100)

            if volume_norm > volume_trigger:
                if not self.counter_running:
                    self.start_countdown()

        self.stream = sd.InputStream(callback=audio_callback, device=device_index, channels=1)
        self.stream.start()

    def start_countdown(self):
        if self.counter_thread is not None:
            self.counter_thread.join()
        self.counter_seconds = self.delay_slider.get()
        self.counter_running = True

        def countdown():
            while self.counter_seconds > 0:
                if self.counter_seconds == 1:
                    self.playsound('\\bebebeep.mp3')
                self.playsound('\\beep.mp3')
                time.sleep(1)
                self.counter_seconds -= 1
                self.counter_value['text'] = str(self.counter_seconds)
            self.counter_value['text'] = "😆"
            self.playsound('\\finished.mp3')
            self.counter_running = False
            if self.key_press_var.get():
                self.press_ctrl_p()

        self.counter_thread = threading.Thread(target=countdown, daemon=True)
        self.counter_thread.start()

    def playsound(self, path):
        current_dir = os.getcwd()
        playsound(current_dir+path)

    def press_ctrl_p(self):
        ctypes.windll.user32.keybd_event(0x11, 0, 0, 0)  # Press 'Ctrl'
        ctypes.windll.user32.keybd_event(0x50, 0, 0, 0)  # Press 'P'
        ctypes.windll.user32.keybd_event(0x50, 0, 2, 0)  # Release 'P'
        ctypes.windll.user32.keybd_event(0x11, 0, 2, 0)  # Release 'Ctrl'

    def stop(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
        self.counter_running = False

    def on_closing(self):
        self.stop()
        self.root.destroy()

    def apply_dark_theme_to_combobox(self, combobox):
        combobox.tk.eval("""
            ttk::style theme use clam
            ttk::style configure TCombobox -fieldbackground #2e2e2e -background #2e2e2e -foreground white
        """)

root = tk.Tk()
app = MicMonitorApp(root)

root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.mainloop()
