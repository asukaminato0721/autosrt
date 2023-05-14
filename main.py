#!/usr/bin/env python
import subprocess
from configparser import ConfigParser
from pathlib import Path
from typing import List

import PySimpleGUI as sg

DIR = Path(__file__).parent.absolute()

# Read and write config file
config = ConfigParser()
config.read(DIR / "config.ini")

LANG = {
    v: k
    for k, v in {
        "en": "english",
        "zh": "chinese",
        "de": "german",
        "es": "spanish",
        "ru": "russian",
        "ko": "korean",
        "fr": "french",
        "ja": "japanese",
        "pt": "portuguese",
        "tr": "turkish",
        "pl": "polish",
        "ca": "catalan",
        "nl": "dutch",
        "ar": "arabic",
        "sv": "swedish",
        "it": "italian",
        "id": "indonesian",
        "hi": "hindi",
        "fi": "finnish",
        "vi": "vietnamese",
        "iw": "hebrew",
        "uk": "ukrainian",
        "el": "greek",
        "ms": "malay",
        "cs": "czech",
        "ro": "romanian",
        "da": "danish",
        "hu": "hungarian",
        "ta": "tamil",
        "no": "norwegian",
        "th": "thai",
        "ur": "urdu",
        "hr": "croatian",
        "bg": "bulgarian",
        "lt": "lithuanian",
        "la": "latin",
        "mi": "maori",
        "ml": "malayalam",
        "cy": "welsh",
        "sk": "slovak",
        "te": "telugu",
        "fa": "persian",
        "lv": "latvian",
        "bn": "bengali",
        "sr": "serbian",
        "az": "azerbaijani",
        "sl": "slovenian",
        "kn": "kannada",
        "et": "estonian",
        "mk": "macedonian",
        "br": "breton",
        "eu": "basque",
        "is": "icelandic",
        "hy": "armenian",
        "ne": "nepali",
        "mn": "mongolian",
        "bs": "bosnian",
        "kk": "kazakh",
        "sq": "albanian",
        "sw": "swahili",
        "gl": "galician",
        "mr": "marathi",
        "pa": "punjabi",
        "si": "sinhala",
        "km": "khmer",
        "sn": "shona",
        "yo": "yoruba",
        "so": "somali",
        "af": "afrikaans",
        "oc": "occitan",
        "ka": "georgian",
        "be": "belarusian",
        "tg": "tajik",
        "sd": "sindhi",
        "gu": "gujarati",
        "am": "amharic",
        "yi": "yiddish",
        "lo": "lao",
        "uz": "uzbek",
        "fo": "faroese",
        "ht": "haitian creole",
        "ps": "pashto",
        "tk": "turkmen",
        "nn": "nynorsk",
        "mt": "maltese",
        "sa": "sanskrit",
        "lb": "luxembourgish",
        "my": "myanmar",
        "bo": "tibetan",
        "tl": "tagalog",
        "mg": "malagasy",
        "as": "assamese",
        "tt": "tatar",
        "haw": "hawaiian",
        "ln": "lingala",
        "ha": "hausa",
        "ba": "bashkir",
        "jw": "javanese",
        "su": "sundanese",
    }.items()
}


def check_ffmpeg():
    try:
        subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, check=True, text=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
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
        sg.FileBrowse(file_types=(("Model", "*.bin"),)),
    ],
    [sg.Text("Select or fill in Video or Audio File:")],
    [
        sg.Input(key="_FILEBROWSER_", enable_events=True, visible=True),
        sg.FilesBrowse(),
    ],
    [
        sg.Text("Thread Count:"),
        sg.Spin(values=list(range(1, 13)), initial_value=8),
    ],
    [
        sg.Text("srt language:"),
        sg.Combo(
            values=list(LANG.keys()),
            key="_LANGUAGE_",
            default_value=config.get("DEFAULT", "_LANGUAGE_", fallback="japanese"),
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
        file_paths: List[str] = values["_FILEBROWSER_"].split(";")
        whisper = values["_WHISPER_"]
        model = values["_MODEL_"]
        ffmpeg = "ffmpeg" if ffmpeg_is_installed else values["_FFMPEG_"]
        thread_count = values[0]
        language = LANG[values["_LANGUAGE_"]]
        for file_path in file_paths:
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
