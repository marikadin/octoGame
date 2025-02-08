import speech_recognition as sr

# Initialize recognizer
recognizer = sr.Recognizer()

# Use the default microphone as the audio source
with sr.Microphone() as source:
    print("Say something within 5 seconds...")
    # Adjust for ambient noise
    recognizer.adjust_for_ambient_noise(source)
    try:
        # Listen for 5 seconds and save the audio to 'audio' variable
        audio = recognizer.listen(source, timeout=5)
        
        # Recognize speech using Google's speech recognition
        print("You said: " + recognizer.recognize_google(audio))
    
    except sr.WaitTimeoutError:
        print("Listening timed out, no speech detected.")
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
