import pygame
import sys
import os

# --- CONFIGURATION ---
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 320
BG_COLOR = (10, 10, 15) 
FPS = 60

# --- INITIALIZATION ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("StaticSprite Simulator // SIGNAL")
clock = pygame.time.Clock()

# --- ASSET LOADING ---
# Get the folder where this script lives
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_sprite(filename):
    # Build the full path: script_folder/filename
    filepath = os.path.join(SCRIPT_DIR, "assets", filename)    try:
        return pygame.image.load(filepath).convert_alpha()
    except pygame.error:
        print(f"Warning: {filename} not found at {filepath}")
        return None

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
mood_list = ["idle", "happy", "sad", "angry", "oof", "sleeping", "music", "dead"]
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
            
                # Touchscreen/Mouse interaction
        if event.type == pygame.MOUSEBUTTONDOWN:
            current_idx = mood_list.index(current_mood)
            next_idx = (current_idx + 1) % len(mood_list)
            current_mood = mood_list[next_idx]
            
            # Reset animation so the new mood starts fresh
            anim_index = 0
            frame_timer = 0
            
            # Reset animation when mood changes
            current_frame = "base"
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
    # 3. RENDERING
    screen.fill(BG_COLOR)
    
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