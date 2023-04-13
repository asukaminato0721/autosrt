#!/usr/bin/env python
import platform
import subprocess
from pathlib import Path

import PySimpleGUI as sg

if platform.system() == "Windows":
    ffmpeg_executable = "ffmpeg.exe"
else:
    ffmpeg_executable = "ffmpeg"


# Check if ffmpeg is installed
def check_ffmpeg():
    try:
        subprocess.run(
            [ffmpeg_executable, "-version"], capture_output=True, check=True, text=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


ffmpeg_is_installed = check_ffmpeg()

DIR = Path(__file__).parent.absolute()

# Define the layout of the GUI
layout = [
    [sg.Text("ffmpeg detected" if ffmpeg_is_installed else "please install ffmpeg")],
    [sg.Text("Select or fill in whisper cpp path")],
    [
        sg.Input(
            key="_WHISPER_",
            enable_events=True,
            visible=True,
            default_text="/usr/bin/whisper.cpp",
        ),
        sg.FileBrowse(),
    ],
    [sg.Text("Select or fill in whisper model path")],
    [
        sg.Input(
            key="_MODEL_",
            enable_events=True,
            visible=True,
            default_text="/usr/share/whisper.cpp-model-large/large.bin",
        ),
        sg.FileBrowse(),
    ],
    [sg.Text("Select or fill in Video or Audio File:")],
    [
        sg.Input(key="_FILEBROWSER_", enable_events=True, visible=True),
        sg.FileBrowse(),
    ],
    [
        sg.Text("Thread Count:"),
        sg.Spin(values=list(range(1, 13)), initial_value=8),
    ],
    [sg.Text("srt language:"), sg.Combo(["ja", "zh", "en"], default_value="ja")],
    [sg.Button("Run Task", disabled=not ffmpeg_is_installed)],
]

# Create the GUI window
window = sg.Window("Autosrt", layout)

# Start the event loop
while True:
    event, values = window.read()

    # If the user closes the window or clicks the "Exit" button, exit the event loop
    if event == sg.WINDOW_CLOSED:
        break
    if event == "Run Task":
        file_path: str = values["_FILEBROWSER_"]
        whisper = values["_WHISPER_"]
        model = values["_MODEL_"]
        thread_count = values[0]
        language = values[1]
        filewav = f"{file_path}.wav"  # remove space to fix path

        subprocess.Popen(
            (
                [
                    ffmpeg_executable,
                    "-i",
                    file_path,
                    "-ar",
                    "16000",
                    "-ac",
                    "1",
                    "-c:a",
                    "pcm_s16le",
                    filewav,
                    "-y",
                ]
            )
        ).wait()
        subprocess.Popen(
            (
                [
                    whisper,
                    "--model",
                    model,
                    "-f",
                    filewav,
                    "-l",
                    language,
                    "-t",
                    str(thread_count),
                    "-osrt",
                    "-of",
                    f"{file_path}.srt",
                ]
            )
        )

# Close the window and exit the program
window.close()
