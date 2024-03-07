import pygame
import cv2
import numpy as np
import serial

# Initialize pygame
pygame.init()

# Set screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# Set colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Set font
font = pygame.font.Font(None, 36)

# Initialize motors (replace with your motor control logic)
num_motors = 6
motors = {f"Motor {i+1}": False for i in range(num_motors)}  # Initially, all motors are off

def toggle_motor(motor_name):
    motors[motor_name] = not motors[motor_name]
    if motors[motor_name]:
        start_motor(motor_name)
    else:
        stop_motor(motor_name)

def start_motor(motor_name):
    print(f"Starting motor {motor_name}")

def stop_motor(motor_name):
    print(f"Stopping motor {motor_name}")

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

    # Clear screen
    screen.fill(WHITE)

    # Draw motor buttons and check for button clicks
    button_width = SCREEN_WIDTH // num_motors
    for i, (motor_name, state) in enumerate(motors.items()):
        button_rect = pygame.Rect(i * button_width, 50, button_width, 50)
        pygame.draw.rect(screen, BLACK if state else WHITE, button_rect)
        text = font.render(motor_name, True, WHITE if state else BLACK)
        text_rect = text.get_rect(center=button_rect.center)
        screen.blit(text, text_rect)

        # Check button click
        if event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
            toggle_motor(motor_name)

    # Display camera feeds
    camera_surface = pygame.Surface((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    camera_rect = camera_surface.get_rect(topleft=(0, 100))
    for capture in captures:
        ret, frame = capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)  # Rotate frame
            frame = pygame.surfarray.make_surface(frame)
            frame = pygame.transform.scale(frame, (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4))
            camera_surface.blit(frame, (0, 0))
    screen.blit(camera_surface, camera_rect)

    # Read and display proximity sensor data (dummy data for now)
    proximity_data = "10"  # Dummy data for testing
    text = font.render(f"Proximity Sensor Distance: {100} cm", True, BLACK)
    screen.blit(text, (50, 650))

    # Update display
    pygame.display.flip()

# Cleanup
for capture in captures:
    capture.release()
pygame.quit()
