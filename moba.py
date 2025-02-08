import pygame
import time
import threading
import tkinter as tk
from tkinter import simpledialog
import keyboard  # For global hotkey support
import os
import sys

def resource_path(relative_path):
    """Get the absolute path to a resource, compatible with PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller extracts resources to a temporary directory
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Initialize PyGame mixer for audio
pygame.mixer.init()

# Load sounds
click_sound = pygame.mixer.Sound(resource_path('click.wav'))
small_camp_sound = pygame.mixer.Sound(resource_path('small_camp_spawn.wav'))
medium_camp_sound = pygame.mixer.Sound(resource_path('medium_camp_spawn.wav'))
hard_camp_sound = pygame.mixer.Sound(resource_path('hard_camp_spawn.wav'))
buff_1min_sound = pygame.mixer.Sound(resource_path('buff_1min.wav'))
buff_30sec_sound = pygame.mixer.Sound(resource_path('buff_30sec.wav'))
buff_10sec_sound = pygame.mixer.Sound(resource_path('buff_10sec.wav'))
buff_spawn_sound = pygame.mixer.Sound(resource_path('buff_spawn.wav'))
wave_sound = pygame.mixer.Sound(resource_path('wave.wav'))

# Timing configuration
start_time = None
pause_time = None
is_paused = False
next_event_idx = 0

# Tkinter GUI
root = tk.Tk()
root.title("MOBA Timer Alerts")
root.geometry("900x600")  # Adjusted window size for better layout

# Display hotkeys info
hotkeys_label = tk.Label(root, text="Hotkeys: Alt + P (Pause/Resume), Alt + R (Reset), Close Button to exit", font=("Arial", 12))
hotkeys_label.grid(row=0, column=0, columnspan=2, pady=5)

# Current time and next events display
time_label = tk.Label(root, text="Time: --:--", font=("Arial", 16))
time_label.grid(row=1, column=0, columnspan=2, pady=10)

events_label = tk.Label(root, text="Upcoming Events:", font=("Arial", 14))
events_label.grid(row=2, column=0, sticky="w")

events_text = tk.Text(root, font=("Arial", 12), height=10, width=40, state="disabled")
events_text.grid(row=3, column=0, padx=10)

# Full events list display (excluding map checks)
full_events_label = tk.Label(root, text="Full Event List (No Map Checks):", font=("Arial", 14))
full_events_label.grid(row=2, column=1, sticky="w")

full_events_text = tk.Text(root, font=("Arial", 12), height=20, width=40, state="disabled")
full_events_text.grid(row=3, column=1, padx=10)

# Buttons layout
button_frame = tk.Frame(root)
button_frame.grid(row=4, column=0, columnspan=2, pady=10)

start_button = tk.Button(button_frame, text="Start Timer", width=15, command=lambda: start_timer())
start_button.grid(row=0, column=0, padx=5)

pause_button = tk.Button(button_frame, text="Pause/Resume", width=15, command=lambda: toggle_pause())
pause_button.grid(row=0, column=1, padx=5)

reset_button = tk.Button(button_frame, text="Reset Timer", width=15, command=lambda: reset_timer())
reset_button.grid(row=0, column=2, padx=5)

sync_button = tk.Button(button_frame, text="Sync Timer", width=15, command=lambda: sync_timer_popup())
sync_button.grid(row=0, column=3, padx=5)

close_button = tk.Button(button_frame, text="Close", width=15, command=lambda: close_app())
close_button.grid(row=0, column=4, padx=5)

def play_sound(sound):
    sound.play()

def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

def toggle_pause():
    """Pauses or resumes the timer."""
    global is_paused, start_time, pause_time

    if not is_paused:
        # Pause: store the current time to freeze the display
        is_paused = True
        pause_time = time.time() - start_time  # Store the current timer value in seconds
        print("\nPaused")
    else:
        # Resume: calculate new start_time based on the paused time
        is_paused = False
        start_time = time.time() - pause_time  # Resume from the synced time value
        pause_time = None
        print("\nResumed")
        
def reset_timer():
    """Resets the timer to zero."""
    global start_time, next_event_idx, is_paused, pause_time
    is_paused = False
    pause_time = None
    start_time = time.time()
    next_event_idx = 0
    print("\nTimer reset to 00:00")

def sync_timer_popup():
    """Prompts the user to sync the timer through a popup."""
    new_time_str = simpledialog.askstring("Sync Timer", "Enter new time (mm:ss):")
    if new_time_str:
        adjust_time(new_time_str)

def adjust_time(new_time_str):
    """Adjusts the timer to sync with the in-game time and skip past events."""
    global start_time, pause_time, next_event_idx

    try:
        # Parse input time (e.g., "05:30")
        mins, secs = map(int, new_time_str.split(":"))
        new_time_in_seconds = mins * 60 + secs

        if is_paused:
            # Update pause_time to reflect the synced time
            pause_time = new_time_in_seconds
        else:
            # Adjust start_time for running mode
            current_time = time.time()
            start_time = current_time - new_time_in_seconds

        # Skip past events
        for i, (event_time, _, _) in enumerate(events):
            if event_time > new_time_in_seconds:
                next_event_idx = i
                break

        print(f"Timer synced to {format_time(new_time_in_seconds)} (Paused: {is_paused})")
        update_display()

    except ValueError:
        print("\nInvalid time format. Use mm:ss (e.g., 05:30).")

def update_display():
    """Updates the GUI display with the current time and upcoming events."""
    if not start_time and not pause_time:
        root.after(100, update_display)
        return

    # Calculate the time to display
    if is_paused:
        # Use pause_time directly while paused
        current_time = pause_time
    else:
        # Calculate time difference while running
        current_time = time.time() - start_time

    # Display the time with appropriate label
    time_label.config(text=f"Time: {format_time(current_time)}" + (" [PAUSED]" if is_paused else ""))

    # Update upcoming events list
    events_text.config(state="normal")
    events_text.delete("1.0", tk.END)
    for i in range(next_event_idx, min(next_event_idx + 3, len(events))):
        event_time, _, event_desc = events[i]
        events_text.insert(tk.END, f"{format_time(event_time)} - {event_desc}\n")
    events_text.config(state="disabled")

    # Schedule the next update
    root.after(100, update_display)

def load_full_event_list():
    """Loads the full list of events, excluding map checks, into the right-side text box."""
    full_events_text.config(state="normal")
    full_events_text.delete("1.0", tk.END)
    for event_time, _, event_desc in events:
        if "Map Check" not in event_desc:  # Exclude map checks
            full_events_text.insert(tk.END, f"{format_time(event_time)} - {event_desc}\n")
    full_events_text.config(state="disabled")

def start_timer():
    """Starts the timer and event handling."""
    global start_time, next_event_idx
    start_time = time.time()
    next_event_idx = 0
    print("Timer started")

    keyboard.add_hotkey('alt+p', toggle_pause)
    keyboard.add_hotkey('alt+r', reset_timer)

    update_display()
    threading.Thread(target=handle_events, daemon=True).start()

def handle_events():
    """Handles playing sounds for events."""
    global next_event_idx
    while next_event_idx < len(events):
        if is_paused:
            time.sleep(0.1)
            continue

        current_time = time.time() - start_time
        event_time, sound, _ = events[next_event_idx]
        if current_time >= event_time:
            play_sound(sound)
            next_event_idx += 1

        time.sleep(0.1)

def close_app():
    """Cleanly exits the application."""
    root.destroy()
    print("Application closed.")
    exit()

# Initialize event list
events = [
    *[(i * 10, click_sound, 'Map Check') for i in range(1, 600)],
    *[(i * 25, wave_sound, 'Wave') for i in range(1, ((10 * 60 - 35) // 25))],
    (110, small_camp_sound, 'Small Camp Spawn'),
    (290, medium_camp_sound, 'Medium Camp Spawn'),
    (470, hard_camp_sound, 'Hard Camp Spawn'),
    *[(9 * 60 + n * 5 * 60 - 10, buff_1min_sound, f'Buff {10 + n * 5} min - 1 min alert') for n in range(0, 10)],
    *[(9 * 60 + 30 + n * 5 * 60 - 10, buff_30sec_sound, f'Buff {10 + n * 5} min - 30 sec alert') for n in range(0, 10)],
    *[(9 * 60 + 50 + n * 5 * 60 - 10, buff_10sec_sound, f'Buff {10 + n * 5} min - 10 sec alert') for n in range(0, 10)],
    *[(10 * 60 + n * 5 * 60 - 10, buff_spawn_sound, f'Buff {10 + n * 5} min Spawn') for n in range(0, 10)],
]
events.sort(key=lambda x: x[0])

load_full_event_list()

root.mainloop()
