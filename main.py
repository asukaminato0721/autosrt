#!/usr/bin/env python
import subprocess
from configparser import ConfigParser
from pathlib import Path
import PySimpleGUI as sg

DIR = Path(__file__).parent.absolute()

# Read and write config file
config = ConfigParser()
config.read(DIR / "config.ini")


# Check if ffmpeg is installed
def check_ffmpeg():
    try:
        subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, check=True, text=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


ffmpeg_is_installed = check_ffmpeg()

# Define the layout of the GUI
layout = [
    [
        sg.Text(
            "ffmpeg detected"
            if ffmpeg_is_installed
            else "Select or fill in ffmpeg path"
        )
    ],
    [sg.Text("Select or fill in whisper cpp path")],
    [
        sg.Input(
            key="_WHISPER_",
            enable_events=True,
            visible=True,
            default_text=config.get("DEFAULT", "_WHISPER_", fallback=""),
        ),
        sg.FileBrowse(),
    ],
    [sg.Text("Select or fill in whisper model path")],
    [
        sg.Input(
            key="_MODEL_",
            enable_events=True,
            visible=True,
            default_text=config.get("DEFAULT", "_MODEL_", fallback=""),
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
    [
        sg.Text("srt language:"),
        sg.Combo(
            ["ja", "zh", "en"],
            key="_LANGUAGE_",
            default_value=config.get("DEFAULT", "_LANGUAGE_", fallback="ja"),
            enable_events=True,
        ),
    ],
    [sg.Button("Run Task")],
]
# add the layout to choose ffmpeg if not installed
if not ffmpeg_is_installed:
    layout.insert(
        1,
        [
            sg.Input(
                key="_FFMPEG_",
                enable_events=True,
                visible=True,
                default_text=config.get("DEFAULT", "_FFMPEG_", fallback=""),
            ),
            sg.FileBrowse(),
        ],
    )

# Create the GUI window
window = sg.Window("Autosrt", layout)

# Start the event loop
while True:
    event, values = window.read()

    # If the user closes the window or clicks the "Exit" button, exit the event loop
    if event == sg.WINDOW_CLOSED:
        break
    # If select a file then write config
    if event in ("_FFMPEG_", "_WHISPER_", "_MODEL_", "_LANGUAGE_"):
        config["DEFAULT"][event] = values[event]
        config.write(Path(DIR / "config.ini").open("w"))
    if event == "Run Task":
        file_path: str = values["_FILEBROWSER_"]
        whisper = values["_WHISPER_"]
        model = values["_MODEL_"]
        ffmpeg = "ffmpeg" if ffmpeg_is_installed else values["_FFMPEG_"]
        thread_count = values[0]
        language = values["_LANGUAGE_"]
        filewav = f"{file_path}.wav"

        subprocess.Popen(
            (
                [
                    ffmpeg,
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
                    file_path,
                ]
            )
        )

# Close the window and exit the program
window.close()
