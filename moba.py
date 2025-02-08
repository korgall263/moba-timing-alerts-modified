import pygame
import time
import threading
import tkinter as tk
import keyboard  # For global hotkey support

# Initialize PyGame mixer for audio
pygame.mixer.init()

# Load sounds
click_sound = pygame.mixer.Sound('click.wav')
small_camp_sound = pygame.mixer.Sound('small_camp_spawn.wav')
medium_camp_sound = pygame.mixer.Sound('medium_camp_spawn.wav')
hard_camp_sound = pygame.mixer.Sound('hard_camp_spawn.wav')
buff_1min_sound = pygame.mixer.Sound('buff_1min.wav')
buff_30sec_sound = pygame.mixer.Sound('buff_30sec.wav')
buff_10sec_sound = pygame.mixer.Sound('buff_10sec.wav')
buff_spawn_sound = pygame.mixer.Sound('buff_spawn.wav')
wave_sound = pygame.mixer.Sound('wave.wav')

# Timing configuration
start_time = None
is_paused = False
next_event_idx = 0  # Track current event

# Tkinter GUI
root = tk.Tk()
root.title("MOBA Timer Alerts")
root.geometry("800x400")

# Current time and next events display
time_label = tk.Label(root, text="Time: --:--", font=("Arial", 16))
time_label.grid(row=0, column=0, columnspan=2, pady=10)

events_label = tk.Label(root, text="Upcoming Events:", font=("Arial", 14))
events_label.grid(row=1, column=0, sticky="w")

events_text = tk.Text(root, font=("Arial", 12), height=10, width=40, state="disabled")
events_text.grid(row=2, column=0, padx=10)

# Full events list display (excluding map checks)
full_events_label = tk.Label(root, text="Full Event List (No Map Checks):", font=("Arial", 14))
full_events_label.grid(row=1, column=1, sticky="w")

full_events_text = tk.Text(root, font=("Arial", 12), height=20, width=40, state="disabled")
full_events_text.grid(row=2, column=1, padx=10)

def play_sound(sound):
    sound.play()

def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

def toggle_pause():
    global is_paused
    is_paused = not is_paused
    print("\nPaused" if is_paused else "\nResumed")

def adjust_time(new_time_str):
    """Adjusts the timer to sync with the in-game time and skip past events."""
    global start_time, next_event_idx
    try:
        mins, secs = map(int, new_time_str.split(":"))
        new_time_in_seconds = mins * 60 + secs
        current_time = time.time()
        start_time = current_time - new_time_in_seconds

        # Skip past events
        for i, (event_time, _, _) in enumerate(events):
            if event_time > new_time_in_seconds:
                next_event_idx = i
                break

        print(f"\nTimer adjusted to {format_time(new_time_in_seconds)}")
    except ValueError:
        print("\nInvalid time format. Use mm:ss (e.g., 05:30).")

def update_display():
    """Updates the GUI display with the current time and upcoming events."""
    if not start_time:
        return

    current_time = time.time() - start_time

    # Update time label
    time_label.config(text=f"Time: {format_time(current_time)}" + (" [PAUSED]" if is_paused else ""))

    # Update upcoming events list
    events_text.config(state="normal")
    events_text.delete("1.0", tk.END)
    for i in range(next_event_idx, min(next_event_idx + 3, len(events))):
        event_time, _, event_desc = events[i]
        events_text.insert(tk.END, f"{format_time(event_time)} - {event_desc}\n")
    events_text.config(state="disabled")

    # Schedule next update
    root.after(100, update_display)

def load_full_event_list():
    """Loads the full list of events, excluding map checks, into the right-side text box."""
    full_events_text.config(state="normal")
    full_events_text.delete("1.0", tk.END)
    for event_time, _, event_desc in events:
        if "Map Check" not in event_desc:  # Exclude map checks
            full_events_text.insert(tk.END, f"{format_time(event_time)} - {event_desc}\n")
    full_events_text.config(state="disabled")

def listen_for_input():
    """Continuously listens for manual input commands."""
    while True:
        user_input = input("\nEnter 'sync mm:ss' to adjust the timer: ").strip().lower()
        if user_input.startswith('sync '):
            _, new_time_str = user_input.split(' ', 1)
            adjust_time(new_time_str)

def main():
    global start_time, next_event_idx
    input("Press Enter to start the alerts...")
    start_time = time.time()

    # Register a global hotkey for pause/resume (Alt + P)
    keyboard.add_hotkey('alt+p', toggle_pause)

    # Start a separate thread to listen for manual input commands
    threading.Thread(target=listen_for_input, daemon=True).start()

    # Schedule
    global events
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

    # Load the full event list (excluding map checks)
    load_full_event_list()

    # Start updating the display
    update_display()

    # Main loop to handle events
    while next_event_idx < len(events):
        if is_paused:
            time.sleep(0.1)
            continue

        current_time = time.time() - start_time

        # Check if the current event should trigger
        event_time, sound, _ = events[next_event_idx]
        if current_time >= event_time:
            play_sound(sound)
            next_event_idx += 1

        time.sleep(0.1)

if __name__ == "__main__":
    threading.Thread(target=main, daemon=True).start()
    root.mainloop()
