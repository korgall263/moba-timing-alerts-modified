import pygame
import time

# Initialize PyGame mixer
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

def play_sound(sound):
    sound.play()

def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

def main():
    global start_time
    input("Press Enter to start the alerts...")
    start_time = time.time()
    
    # Schedule
    events = [
        # Map check reminders every 10 seconds
        *[(i * 10, click_sound, 'Map Check') for i in range(1, 600)],

        # Wave spawns every 25 seconds starting at 35s until the first buff at 10:00
        *[(i * 25, wave_sound, 'Wave') for i in range(1, ((10 * 60 - 35) // 25))],

        # Camp spawns (adjusted for 10s game timer offset)
        (110, small_camp_sound, 'Small Camp Spawn'),  # Small camp at 2:00
        (290, medium_camp_sound, 'Medium Camp Spawn'), # Medium camp at 5:00
        (470, hard_camp_sound, 'Hard Camp Spawn'),   # Hard camp at 8:00

        # Buff alerts (starting at 10:00, adjusted for 10s offset, then every 5 min)
        *[(9 * 60 + n * 5 * 60 - 10, buff_1min_sound, f'Buff {10 + n*5} min - 1 min alert') for n in range(0, 10)],     # 1 min before each buff
        *[(9 * 60 + 20 + n * 5 * 60 - 10, buff_30sec_sound, f'Buff {10 + n*5} min - 30 sec alert') for n in range(0, 10)], # 30 sec before each buff
        *[(9 * 60 + 50 + n * 5 * 60 -10, buff_10sec_sound, f'Buff {10 + n*5} min - 10 sec alert') for n in range(0, 10)], # 10 sec before each buff
        *[(10 * 60 + n * 5 * 60 - 10, buff_spawn_sound, f'Buff {10 + n*5} min Spawn') for n in range(0, 10)],     # Buff at 10:00, 15:00, etc.
    ]

    # Sort events by time
    events.sort(key=lambda x: x[0])

    # Print event schedule for debugging
    print("Scheduled Events:")
    for event_time, _, description in events:
        print(f"{format_time(event_time)} - {description}")

    next_event_idx = 0
    while next_event_idx < len(events):
        current_time = time.time() - start_time
        event_time, sound, _ = events[next_event_idx]

        if current_time >= event_time:
            play_sound(sound)
            next_event_idx += 1
        
        time.sleep(0.1)  # Small delay to prevent high CPU usage

if __name__ == "__main__":
    main()

