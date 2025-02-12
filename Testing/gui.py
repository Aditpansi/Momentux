import pygame
import cv2
import numpy as np

# Initialize pygame
pygame.init()

# Set screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# Set colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
GREEN = (0, 255, 0)
BLUE = (0, 191, 255)

# Set font
font = pygame.font.Font(None, 30)

# Initialize motors (replace with your motor control logic)
motors = {
    "X": {"state": False, "speed": "Low"},
    "Y": {"state": False, "speed": "Low"},
    "Yaw": {"state": False, "speed": "Low"},
    "Pitch": {"state": False, "speed": "Low"},
    "Z": {"state": False, "speed": "Low"}  # Initially, motor Z is off
}

selected_motor = "X"  # Initially select Motor X
speed = "Low"  # Initial speed

# Initialize popup message variables
popup_message = ""
popup_timer = 0

def toggle_motor(motor_name):
    global selected_motor, popup_message, popup_timer
    for name, motor in motors.items():
        if name != motor_name:
            motor["state"] = False
    motors[motor_name]["state"] = not motors[motor_name]["state"]
    selected_motor = motor_name
    if motors[motor_name]["state"]:
        popup_message = f"Starting motor {motor_name} with speed: {motors[motor_name]['speed']}"
        popup_timer = 120  # Display popup for 2 seconds (60 frames per second)
    else:
        popup_message = f"Stopping motor {motor_name}"
        popup_timer = 120

def toggle_speed():
    global speed, popup_message, popup_timer
    speed = "High" if speed == "Low" else "Low"
    popup_message = f"Speed changed to {speed} for {selected_motor}"
    popup_timer = 120

def is_mouse_over_button(pos, rect):
    return rect.left < pos[0] < rect.right and rect.top < pos[1] < rect.bottom

# Initialize camera captures
num_cameras = 4
captures = [cv2.VideoCapture(0) for i in range(num_cameras)]

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dynamic Motor Control with Cameras and Proximity Sensor")

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for motor_name, button_rects in button_positions.items():
                if "motor" in button_rects and is_mouse_over_button(mouse_pos, button_rects["motor"]):
                    toggle_motor(motor_name)
                elif "speed" in button_rects and is_mouse_over_button(mouse_pos, button_rects["speed"]):
                    toggle_speed()

    # Clear screen
    screen.fill(WHITE)

    # Calculate button sizes and positions dynamically based on the number of motors
    button_width = SCREEN_WIDTH // len(motors)
    button_height = 50
    button_margin = 20

    # Store button positions
    button_positions = {}

    # Draw motor buttons
    for i, motor_name in enumerate(motors.keys()):
        button_x = i * button_width
        button_y = 50
        motor_button_rect = pygame.Rect(button_x, button_y, button_width - button_margin, button_height)

        # Store button positions for later use
        button_positions[motor_name] = {"motor": motor_button_rect}

        # Draw motor button
        button_color = BLUE if motors[motor_name]["state"] else GRAY
        pygame.draw.rect(screen, button_color, motor_button_rect)
        pygame.draw.rect(screen, BLACK, motor_button_rect, width=2)
        motor_text = font.render(motor_name, True, WHITE)
        motor_text_rect = motor_text.get_rect(center=motor_button_rect.center)
        screen.blit(motor_text, motor_text_rect)

    # Draw speed button
    speed_button_width = 150
    speed_button_height = button_height
    speed_button_x = (SCREEN_WIDTH - speed_button_width) // 2
    speed_button_y = 50 + button_height + button_margin
    speed_button_rect = pygame.Rect(speed_button_x, speed_button_y, speed_button_width, speed_button_height)
    pygame.draw.rect(screen, GREEN, speed_button_rect)
    pygame.draw.rect(screen, BLACK, speed_button_rect, width=2)
    speed_text = font.render(f"Speed: {speed}", True, WHITE)
    speed_text_rect = speed_text.get_rect(center=speed_button_rect.center)
    screen.blit(speed_text, speed_text_rect)

    # Store button positions for later use
    button_positions["Speed"] = {"speed": speed_button_rect}

    # Display camera feeds
    camera_surface = pygame.Surface((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    camera_rect = camera_surface.get_rect(topleft=(0, 200))
    for capture in captures:
        ret, frame = capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)  # Rotate frame
            frame = pygame.surfarray.make_surface(frame)
            frame = pygame.transform.scale(frame, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4))
            camera_surface.blit(frame, (0, 0))
    screen.blit(camera_surface, camera_rect)

    

    # Display popup message
    if popup_timer > 0:
        popup_timer -= 1
        popup_surface = font.render(popup_message, True, BLACK)
        popup_rect = popup_surface.get_rect(topright=(SCREEN_WIDTH - 10, 10))
        screen.blit(popup_surface, popup_rect)

    # Update display
    pygame.display.flip()

# Cleanup
for capture in captures:
    capture.release()
pygame.quit()
