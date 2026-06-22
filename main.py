import pygame
import sys
import os

# --- CONFIGURATION ---
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 320
BG_COLOR = (10, 10, 15) 
FPS = 60

# --- UI CONFIG ---
COLOR_BG_BAR = (20, 20, 30)  # Deep void black

# Neon palette
COLOR_HUNGER = (180, 50, 255)    # Electric Purple
COLOR_HAPPY  = (50, 255, 150)    # Toxic Green
COLOR_ENERGY = (255, 50, 200)    # Hot Pink (or swap for cyan if you want)

# --- INITIALIZATION ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("StaticSprite Simulator // SIGNAL")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont('monospace', 12)

# --- ASSET LOADING ---
# Get the folder where this script lives
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_sprite(filename):
    filepath = os.path.join(SCRIPT_DIR, "assets", filename)
    try:
        return pygame.image.load(filepath).convert_alpha()
    except pygame.error:
        print(f"Warning: {filename} not found at {filepath}")
        return None

def draw_stat_bar(screen, x, y, width, height, value, color, label):
    # Background track
    pygame.draw.rect(screen, COLOR_BG_BAR, (x, y, width, height))
    # Fill
    fill_width = max(0, int((value / 100) * width))
    if fill_width > 0:
        pygame.draw.rect(screen, color, (x, y, fill_width, height))
    # Label
    text = FONT.render(f"{label}: {int(value)}", True, color)
    screen.blit(text, (x, y - 14))

# Dictionary of dictionaries for our animation frames
sprites = {
    "idle": {
        "base": load_sprite("signal_idle.png"),
        "blink": load_sprite("signal_idle_blink.png"),
        "move": load_sprite("signal_idle_move.png")
    },
    "happy": {
        "base": load_sprite("signal_happy.png"),
        "blink": load_sprite("signal_happy_blink.png"),
        "move": load_sprite("signal_happy_move.png")
    },
    "sad": {
        "base": load_sprite("signal_sad.png"),
        "blink": load_sprite("signal_sad_blink.png"),
        "move": load_sprite("signal_sad_move.png")
    },
    "angry": {
        "base": load_sprite("signal_angry.png"),
        "blink": load_sprite("signal_angry_blink.png"),
        "move": load_sprite("signal_angry_move.png")
    },
    "oof": {
        "base": load_sprite("signal_oof.png"),
        "move": load_sprite("signal_oof_move.png") # No blink for >.<
    },
    "sleeping": {
        "base": load_sprite("signal_sleeping.png"),
        "move": load_sprite("signal_sleeping_move.png")
    },
    "music": {
        "base": load_sprite("signal_music.png"),
        "move": load_sprite("signal_music_move.png")
    },
    "dead": {
        "base": load_sprite("signal_dead.png") # Dead things don't move or blink
    }
}

# --- STATE MACHINE ---
current_mood = "idle"
current_frame = "base"
frame_timer = 0

# Animation timings (in milliseconds)
TIME_BASE = 2000   # How long to hold the base pose
TIME_MOVE = 1500   # How long to hold the tentacle shift
TIME_BLINK = 750   # How fast the blink is
# --- STATS ENGINE ---
stats = {
    "hunger": 100,
    "happiness": 100,
    "energy": 100
}

STAT_DECAY_RATE = 0.002  # How fast stats drop per frame
STAT_DECAY_INTERVAL = 1000  # Decay every 1 second (in milliseconds)
stat_decay_timer = 0
mood_override_timer = 0
MOOD_OVERRIDE_DURATION = 5000

anim_sequence = ["base"]
anim_index = 0

# --- MAIN LOOP ---
running = True
while running:
    dt = clock.tick(FPS)
    
# 1. EVENT HANDLING (Keyboard controls for testing)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1: current_mood = "idle"
            if event.key == pygame.K_2: current_mood = "happy"
            if event.key == pygame.K_3: current_mood = "sad"
            if event.key == pygame.K_4: current_mood = "angry"
            if event.key == pygame.K_5: current_mood = "oof"
            if event.key == pygame.K_6: current_mood = "sleeping"
            if event.key == pygame.K_7: current_mood = "music"
            if event.key == pygame.K_8: current_mood = "dead"
            
            # Reset animation when mood changes
            current_frame = "base"
            frame_timer = 0
        
                # Touchscreen/Mouse interaction
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Petting restores stats
            stats["happiness"] = min(100, stats["happiness"] + 15)
            stats["energy"] = min(100, stats["energy"] + 20)  # More energy from petting
            stats["hunger"] = min(100, stats["hunger"] + 5)
            
            # If sleeping, clicking always wakes them up
            if current_mood == "sleeping":
                current_mood = "idle"
            # If dead, clicking doesn't work (they're dead)
            elif current_mood == "dead":
                pass
            else:
                # Otherwise cycle through moods
                mood_list = ["idle", "happy", "sad", "angry", "oof", "music"]
                current_idx = mood_list.index(current_mood)
                next_idx = (current_idx + 1) % len(mood_list)
                current_mood = mood_list[next_idx]
            
            # Give 5 seconds of manual control before stats override again
            mood_override_timer = MOOD_OVERRIDE_DURATION
            
            # Reset animation
            anim_index = 0
            frame_timer = 0

# 2. ANIMATION LOGIC
    frame_timer += dt
    mood_sprites = sprites.get(current_mood, sprites["idle"])

    # Build the animation sequence for this mood
    new_sequence = ["base"]
    if "move" in mood_sprites:
        new_sequence.append("move")
    if "blink" in mood_sprites:
        new_sequence.append("blink")

    # Reset sequence if mood changed
    if anim_sequence != new_sequence:
        anim_sequence = new_sequence
        anim_index = 0

    # Get current frame
    current_frame = anim_sequence[anim_index]

    # Determine timing
    if current_frame == "base":
        frame_duration = TIME_BASE
    elif current_frame == "move":
        frame_duration = TIME_MOVE
    elif current_frame == "blink":
        frame_duration = TIME_BLINK
    else:
        frame_duration = TIME_BASE

    # Advance frame
    if frame_timer >= frame_duration:
        frame_timer = 0
        anim_index = (anim_index + 1) % len(anim_sequence)
    
    # --- STATS DECAY ---
    stat_decay_timer += dt
    mood_override_timer = max(0, mood_override_timer - dt)  # Count down override timer
    
    if stat_decay_timer >= STAT_DECAY_INTERVAL:
        stat_decay_timer = 0
        stats["hunger"] = max(0, stats["hunger"] - STAT_DECAY_RATE * STAT_DECAY_INTERVAL)
        stats["happiness"] = max(0, stats["happiness"] - STAT_DECAY_RATE * STAT_DECAY_INTERVAL)
        stats["energy"] = max(0, stats["energy"] - STAT_DECAY_RATE * STAT_DECAY_INTERVAL)
        
        # Only auto-change mood if override timer is expired
        if mood_override_timer == 0:
            if stats["energy"] < 20:
                current_mood = "sleeping"
            elif stats["hunger"] < 30:
                current_mood = "sad"
            elif stats["happiness"] < 30:
                current_mood = "angry"
    
# 3. RENDERING
    screen.fill(BG_COLOR)
    
    # --- DRAW STATS UI ---
    bar_width = 60
    bar_height = 8
    start_x = 30
    start_y = 240
    spacing = 70

    # Calculate colors (flash red if a stat drops below 20)
    tick = pygame.time.get_ticks()
    flash = (tick // 300) % 2 == 0  # Toggles every 300ms

    c_hunger = (255, 0, 0) if stats["hunger"] < 20 and flash else COLOR_HUNGER
    c_happy  = (255, 0, 0) if stats["happiness"] < 20 and flash else COLOR_HAPPY
    c_energy = (255, 0, 0) if stats["energy"] < 20 and flash else COLOR_ENERGY

    draw_stat_bar(screen, start_x, start_y, bar_width, bar_height, stats["hunger"], c_hunger, "HNG")
    draw_stat_bar(screen, start_x + spacing, start_y, bar_width, bar_height, stats["happiness"], c_happy, "HAP")
    draw_stat_bar(screen, start_x + spacing * 2, start_y, bar_width, bar_height, stats["energy"], c_energy, "NRG")
    
    # Get the current image, fallback to base if missing
    active_sprite = mood_sprites.get(current_frame, mood_sprites.get("base"))
    
    if active_sprite:
        # Scale sprite if it's too big for the 240x320 screen
        # (Remove this if your sprites are already the right size)
        if active_sprite.get_width() > SCREEN_WIDTH:
            active_sprite = pygame.transform.scale(active_sprite, (SCREEN_WIDTH, SCREEN_HEIGHT))
            
        rect = active_sprite.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(active_sprite, rect)
    else:
        # Fallback purple box
        pygame.draw.rect(screen, (138, 43, 226), (SCREEN_WIDTH//2 - 20, SCREEN_HEIGHT//2 - 20, 40, 40))

    pygame.display.flip()

pygame.quit()
sys.exit()