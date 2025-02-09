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
import pythoncom  # Import pythoncom to initialize COM for TTS
import sys

# Create the Tkinter window.
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

def send_input():
    """Called when the user clicks the Send button.
    This stores the complete entry text into input_value,
    clears the entry widget, and sets the event flag."""
    global input_value
    input_value = user_input_var.get()
    user_input_var.set("")  # Clear the entry box.
    input_event.set()         # Signal that input is ready.

# The Send button uses the above callback.
send_button = tk.Button(root, text="Send", command=send_input)
send_button.pack()

def get_input():
    """Waits until the Send button has been pressed and then returns the input."""
    input_event.wait()      # Block until the event is set.
    value = input_value    # Retrieve the stored input.
    input_event.clear()    # Reset the event for future input.
    return value

#############################################
# TTS and Animation Functions
#############################################

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

def goofy_tts(text, label, img1, img2, voice_index=0, lang="en", use_gtts=False):
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

#############################################
# Main Game Function
#############################################

def startGame():
    global label

    # Re-create the label to avoid duplication.
    if label:
        label.destroy()
    label = tk.Label(root, image=img1)
    label.pack()

    client_socket = socket.socket()
    port = 5555
    client_socket.connect(('127.0.0.1', port))

    # Receive and speak the login message.
    login_text = client_socket.recv(2048).decode()
    start_gui(login_text)


    name = get_input()  # Wait until the user presses Send.
    print(f"Name entered: {name}")
    client_socket.send(name.encode())
    time.sleep(1)

    # Load and display the user's win/lose record.
    with open("database.json", 'r') as file:
        data = json.load(file)

    # Game round 1: prompt for a word.
    prompt = client_socket.recv(2048).decode()
    start_gui(prompt)
    word = get_input()
    client_socket.send(word.encode())

    # Game round 2: two prompts before guessing.
    prompt1 = client_socket.recv(2048).decode()
    start_gui(prompt1)
    prompt2 = client_socket.recv(2048).decode()
    start_gui(prompt2)
    guess = get_input()
    client_socket.send(guess.encode())

    
    result = client_socket.recv(2048).decode()
    start_gui(result) 
    start_gui(f"{name} - wins: {data[name][0]} loses: {data[name][1]}")
    start_gui("do you want to play another game?")        
    client_socket.close()

    time.sleep(1)
    client_socket = socket.socket()
    client_socket.connect(('127.0.0.1', port))
    replay_prompt = client_socket.recv(2048).decode()


    response = get_input()
    client_socket.send(response.encode())
    with open("database.json", 'r') as file:
        data = json.load(file)

    
    if response.lower() == "yes":

        client_socket.close()
        time.sleep(1)
        startGame()  # Restart the game
    else:
        start_gui("thank you for playing")
        time.sleep(2)
        root.quit()
        sys.exit(0)

        

    # Refresh and show updated stats.
    
    client_socket.close()

    # Ask the user if they want to play again.


#############################################
# Start the Application
#############################################

if __name__ == "__main__":
    # Run the game logic in a separate thread.
    threading.Thread(target=startGame, daemon=True).start()
    # Start the Tkinter event loop (must run in main thread).
    root.mainloop()
