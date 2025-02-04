import pyttsx3

# Initialize TTS engine
engine = pyttsx3.init()

# Set properties
voices = engine.getProperty('voices')
# Select female voice if available
for voice in voices:
    if 'zira' in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break

# Increase speech rate slightly
rate = engine.getProperty('rate')
engine.setProperty('rate', rate + 30)

# Alerts to generate
alerts = {
    'small_camp_spawn': "Small camps.",
    'medium_camp_spawn': "Medium camps.",
    'hard_camp_spawn': "Hard camps.",
    'buff_1min': "Buff in one minute.",
    'buff_30sec': "Buff in thirty seconds.",
    'buff_10sec': "Buff in ten seconds.",
    'buff_spawn': "Buff.",
    'wave': "Wave."
}

# Generate and save TTS files
for filename, text in alerts.items():
    engine.save_to_file(text, f'{filename}.wav')

engine.runAndWait()
print("TTS alerts generated successfully!")
