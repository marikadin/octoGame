import json
import socket
import time
import pyttsx3
from gtts import gTTS
import io
import pygame
import threading
import tkinter as tk
from PIL import Image, ImageTk
import pythoncom
import asyncio  # Import asyncio to handle the event loop
from googletrans import Translator

root = tk.Tk()
root.title("TTS Animation")

# Load and keep images in memory.
img1 = ImageTk.PhotoImage(Image.open("octo.png"))  # Replace with your actual image path.
img2 = ImageTk.PhotoImage(Image.open("open_mouth.png"))
label = tk.Label(root, image=img1)
label.pack()

# Create an entry widget for user input.
user_input_var = tk.StringVar()
text_box = tk.Entry(root, textvariable=user_input_var, width=40)
text_box.pack()

# We’ll use a threading.Event to signal that input is ready.
input_event = threading.Event()
# Global variable to hold the input string.
input_value = ""

def pyttsx3_tts(text, voice_index, speaking):
    """Function for TTS using pyttsx3"""
    pythoncom.CoInitialize()  # Initialize COM in the new thread
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    if 0 <= voice_index < len(voices):
        engine.setProperty('voice', voices[voice_index].id)
    engine.setProperty('rate', 250)
    engine.say(text)
    engine.runAndWait()
    speaking[0] = False  # Stop the animation

def gtts_tts(text, lang, speaking):
    """Function for TTS using gTTS"""
    tts = gTTS(text=text, lang=lang)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    pygame.mixer.init()
    pygame.mixer.music.load(fp, 'mp3')
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    speaking[0] = False  # Stop the animation

def animate_images(label, img1, img2, speaking):
    """While speaking, alternate between two images for a talking animation."""
    while speaking[0]:
        label.config(image=img1)
        label.update()
        time.sleep(0.35)
        label.config(image=img2)
        label.update()
        time.sleep(0.35)
    # Reset to the default image when done.
    label.config(image=img1)

def goofy_tts(text, label=label, img1=img1, img2=img2, voice_index=0, lang="en", use_gtts=False):
    """Start animation and TTS in separate threads."""
    speaking = [True]
    threading.Thread(target=animate_images, args=(label, img1, img2, speaking), daemon=True).start()
    if use_gtts:
        threading.Thread(target=gtts_tts, args=(text, lang, speaking), daemon=True).start()
    else:
        threading.Thread(target=pyttsx3_tts, args=(text, voice_index, speaking), daemon=True).start()

def speak(label, img1, img2, text):
    """Convenience wrapper to start the TTS and image animation."""
    goofy_tts(text, label, img1, img2, voice_index=0)

def start_gui(text):
    """Update the GUI with TTS. (Does not call mainloop.)"""
    speak(label, img1, img2, text)

async def translate_and_speak():
    word = input("Enter a word in English: ")
    target_language = input("Enter the target language code (e.g., 'es' for Spanish, 'fr' for French): ")
    # Initialize the translator
    translator = Translator()

    # Translate the word into the target language asynchronously
    translation = await translator.translate(word, dest=target_language)
    translated_word = translation.text

    print(f"Original: {word}")
    goofy_tts(translated_word, lang=target_language)


    # Convert the translated word to speech
    tts = gTTS(translated_word, lang=target_language)

    # Initialize Pygame mixer for sound playback
    pygame.mixer.init()

    # Save speech to a byte stream (in-memory) instead of a file
    with io.BytesIO() as byte_stream:
        tts.write_to_fp(byte_stream)
        byte_stream.seek(0)  # Reset the pointer to the start
        pygame.mixer.music.load(byte_stream, "mp3")
        pygame.mixer.music.play()

        # Wait for the sound to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)  # Wait until the sound has finished

# Input word and target language

# Function to run the async task in the main thread
def run_async_function():
    asyncio.run(translate_and_speak())

# Run the asynchronous function
if __name__ == "__main__":
    threading.Thread(target=run_async_function, daemon=True).start()
    # Start the Tkinter event loop (must run in main thread).
    root.mainloop()
