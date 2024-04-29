import serial
import pygame
import cv2
import numpy as np
import time
from fuctiontest import *
from datetime import datetime

pygame.init() # initializing pygame
pygame.joystick.init()   # initializing joystick 

# Set screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h

img = pygame.image.load('/Users/aditpansi/Downloads/Antena Platform.png')
# Set image as icon 
pygame.display.set_icon(img) 

# Set colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
GREEN = (0, 255, 0)
BLUE = (0, 191, 255)
RED = (255, 0 , 0)
data = ''
selected_motor = None  # Initially select Motor is NONE
speed = "Low"  # Initial speed
command = 'n'
last_command_sent = 'n'
previous_data = ''

# Initialize popup message variables
popup_message = ""
popup_timer = 0

# Before the loop
dark_mode = False
button_default_text = "Light"
button_alternate_text = "Dark"

# Define colors for both modes
light_colors = {"background": WHITE, "text": BLACK, "bar": GRAY, "button": WHITE}
dark_colors = {"background": BLACK, "text": WHITE, "bar": (50, 50, 50), "button": (100, 100, 100)}

button_width = 90
button_height = 24.3
button_corner_radius = 10
toggle_button_rect = pygame.Rect(SCREEN_WIDTH - button_width - 50, 4.3, button_width, button_height)

# Set font
font = pygame.font.Font(None, 30)

num_cameras = 4
captures = [cv2.VideoCapture(i) for i in range(num_cameras)]
'''captures = [
    cv2.VideoCapture(0),  # Index 0 for laptop's built-in webcam
    cv2.VideoCapture(1),  # Index 1 for first external webcam
    cv2.VideoCapture(2),  # Index 2 for second external webcam
]'''

# Initialize motors 
motors = {
    "X": {"state": False, "speed": "Low"},
    "Y": {"state": False, "speed": "Low"},
    "Z": {"state": False, "speed": "Low"},  
    "Yaw": {"state": False, "speed": "Low"},
    "Pitch": {"state": False, "speed": "Low"}
    
}
# Define camera screen regions
camera_screen_rects = [
    pygame.Rect(0, 200, SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4),
    pygame.Rect(SCREEN_WIDTH // 4, 200, SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4),
    pygame.Rect(0, 400, SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4),
    pygame.Rect(SCREEN_WIDTH // 4, 400, SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4)
]

selected_motor_label = "Motor X" 
motor_y_label_text = "Motor Y"
motor_z_label_text = "Motor Z"
motor_button_pressed = False

running = True
speed_button_enabled = False  # Initialize speed button as disabled


#-------------------------------------Rounded Button -------------------------------------------------------

def draw_rounded_button(surface, color, rect, corner_radius):
    """
    Draws buttons with rounded corners on a pygame surface.
    
    :param surface: The pygame surface to draw on.
    :param color: The color of the button (R, G, B).
    :param rect: A pygame.Rect object defining the button's position and size.
    :param corner_radius: The radius of the rounded corners.
    """
    if corner_radius < 0:
        raise ValueError("Corner radius should be >= 0")

    if corner_radius == 0:
        pygame.draw.rect(surface, color, rect)
        return

    if corner_radius > rect.width / 2 or corner_radius > rect.height / 2:
        raise ValueError("Corner radius is too large")

    # Center and corner circles
    pygame.draw.circle(surface, color, (rect.left + corner_radius, rect.top + corner_radius), corner_radius)
    pygame.draw.circle(surface, color, (rect.right - corner_radius - 1, rect.top + corner_radius), corner_radius)
    pygame.draw.circle(surface, color, (rect.left + corner_radius, rect.bottom - corner_radius - 1), corner_radius)
    pygame.draw.circle(surface, color, (rect.right - corner_radius - 1, rect.bottom - corner_radius - 1), corner_radius)
    
    # Rectangle to fill the space between circles
    pygame.draw.rect(surface, color, (rect.left, rect.top + corner_radius, rect.width, rect.height - 2 * corner_radius))
    pygame.draw.rect(surface, color, (rect.left + corner_radius, rect.top, rect.width - 2 * corner_radius, rect.height))


# Create screen
screen_info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = screen_info.current_w, screen_info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Elevator Platform")

#-------------------------------------Aurdino -------------------------------------------------------

# arduino_port = find_arduino_port() # identifies the arduino port 
# print("arduinio port is :", arduino_port)
# ser = serial.Serial(arduino_port , 9600, timeout=1)
# time.sleep(2)

# def send_to_arduino(last_command_sent, chr):
#     ser.write(chr.encode())
#     if last_command_sent != chr:
#         print("sent command :",chr, " to arduino.")
#         last_command_sent = chr
#     return last_command_sent

# def read_from_arduino(prev_data):
#     if ser.inWaiting() > 0:
#         new_data = ser.readline().decode('utf-8').rstrip()
#         if new_data != prev_data:  # Check if new data is different from previous data
#             prev_data = new_data
#             print(prev_data)
#             return prev_data

    #-------------------------------------Joystick code 1-------------------------------------------------------

# joystick_count = pygame.joystick.get_count()
# if joystick_count == 0:
#     print("No joystick detected.")
#     pygame.quit()
    
# # Initialize the first joystick
# joystick = pygame.joystick.Joystick(0)
# joystick.init()
# joy_input = 'n'

while running:
    screen.fill(light_colors["background"] if not dark_mode else dark_colors["background"])
    pygame.event.pump()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if cross_button_rect.collidepoint(event.pos):
                    running = False  # Terminate the program when cross button is clicked
            mouse_pos = pygame.mouse.get_pos()
            pygame.event.pump()

            if toggle_button_rect.collidepoint(mouse_pos):
                dark_mode = not dark_mode

            # Check if mouse click occurred within the button area
            if button_x < mouse_pos[0] < button_x + button_width and button_y < mouse_pos[1] < button_y + button_height:
                # Turn off every motor
                for motor_name in motors:
                    motors[motor_name]["state"] = False
                print("All motors turned off.")
                # Update the display to reflect the changes
                pygame.display.flip()
            
            for motor_name, button_rects in button_positions.items():
                if "motor" in button_rects and is_mouse_over_button(mouse_pos, button_rects["motor"]):
                   selected_motor, popup_message, popup_timer, speed_button_enabled, speed = toggle_motor(motor_name, motors, button_rects, speed)
                   #if motor_name in ['X', 'Y', 'Z']:
                        #selected_motor_label = f"Selected motor: {motor_name}"
                   
                if "speed" in button_rects and is_mouse_over_button(mouse_pos, button_rects["speed"]):
                    speed, command, popup_message, popup_timer = toggle_speed(selected_motor, speed, button_rects, mouse_pos, speed_button_enabled)

                if selected_motor in ['Yaw', 'Pitch']:
                    speed_button_enabled = False

    #-------------------------------------Joystick code 2-------------------------------------------------------

    # if event.type == pygame.JOYAXISMOTION:
    #     x_axis = joystick.get_axis(1)  
    #     y_axis = joystick.get_axis(0)
    #     yaw_axis = joystick.get_axis(2)
    #     previous_data = read_from_arduino( previous_data)
        
    #     if selected_motor == 'X': 
    #         joy_input = joystick_input(x_axis)
    #     elif selected_motor == 'Y':
    #         joy_input = joystick_input(y_axis)
    #     elif selected_motor == 'Yaw':
    #         joy_input = joystick_input(yaw_axis)
    #     elif selected_motor == 'Pitch':
    #         joy_input = joystick_input(x_axis)
    #     elif selected_motor == 'Z' :
    #         joy_input = joystick_input(y_axis)
    #     last_command_sent = send_to_arduino(last_command_sent,joy_input)
        # Clear screen
    # Clear screen
    #screen.fill(WHITE)

    #------------------------------------Menu Bar----------------------------------------------

    # Draw grey bar on top
    top_bar_height = 30
    pygame.draw.rect(screen, GRAY, (0, 0, SCREEN_WIDTH, top_bar_height))

    # Display current date and time
    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%Y-%m-%d")
    date_text = font.render(f"Date: {current_date}", True, WHITE)
    time_text = font.render(f"Time: {current_time}", True, WHITE)
    date_text_rect = date_text.get_rect(topleft=(10, 10))
    time_text_rect = time_text.get_rect(left=date_text_rect.right + 20, top=date_text_rect.top)
    screen.blit(date_text, date_text_rect)
    screen.blit(time_text, time_text_rect)

    # Draw cross button
    cross_button_size = 20
    cross_button_rect = pygame.Rect(SCREEN_WIDTH - cross_button_size - 5, 5, cross_button_size, cross_button_size)
    #pygame.draw.rect(screen, RED, cross_button_rect)
    pygame.draw.line(screen, RED, cross_button_rect.topleft, cross_button_rect.bottomright, 4)
    pygame.draw.line(screen, RED, cross_button_rect.bottomleft, cross_button_rect.topright, 4)

    # Draw the toggle button (rounded rectangle)
    pygame.draw.rect(screen, light_colors["button"] if not dark_mode else dark_colors["button"], toggle_button_rect, border_radius=button_corner_radius)
    
    # Determine text to display based on dark_mode
    button_text = font.render(button_alternate_text if dark_mode else button_default_text, True, light_colors["text"] if not dark_mode else dark_colors["text"])
    
    button_text_rect = button_text.get_rect(center=toggle_button_rect.center)
    screen.blit(button_text, button_text_rect)

    
    #------------------------------------- Button-------------------------------------------------------

    # Calculate button sizes and positions dynamically based on the number of motors
    button_width = SCREEN_WIDTH // len(motors)
    button_height = 50
    button_margin = 20

    # Store button positions
    button_positions = {}

    #-------------------------------------Motor Button-------------------------------------------------------

    # Draw motor buttons
    button_offset = 10  # Adjust this offset as needed
    for i, motor_name in enumerate(motors.keys()):
        button_x = i * button_width + button_offset  # Add offset to x-coordinate
        button_y = 50
        motor_button_rect = pygame.Rect(button_x, button_y, button_width - button_margin, button_height)

    # Store button positions for later use
        button_positions[motor_name] = {"motor": motor_button_rect}

    # Determine button color based on motor state
        button_color = BLUE if motors[motor_name]["state"] else GRAY
    
    # Draw motor button with rounded corners
        draw_rounded_button(screen, button_color, motor_button_rect, 10)  # Assuming a corner radius of 10

    # Draw motor name text
        motor_text = font.render(motor_name, True, WHITE)
        motor_text_rect = motor_text.get_rect(center=motor_button_rect.center)
        screen.blit(motor_text, motor_text_rect)

    #-------------------------------------Speed Button-------------------------------------------------------

   # Draw speed button
        speed_button_width = 150
        speed_button_height = button_height
        speed_button_x = (SCREEN_WIDTH - speed_button_width) // 2
        speed_button_y = 50 + button_height + button_margin
        speed_button_rect = pygame.Rect(speed_button_x, speed_button_y, speed_button_width, speed_button_height)

    # Draw speed button with rounded corners
    draw_rounded_button(screen, GREEN, speed_button_rect, 10)  # Assuming a corner radius of 10

    # Optional: Draw a border around the button
    # This could involve drawing a slightly larger button in black first, and then the actual button on top
    # For simplicity, this example does not implement a border. You might adjust the function or use a workaround as suggested

    # Draw speed text
    speed_text = font.render(f"Speed: {speed}", True, WHITE)
    speed_text_rect = speed_text.get_rect(center=speed_button_rect.center)
    screen.blit(speed_text, speed_text_rect)

    # Store button positions for later use
    button_positions["Speed"] = {"speed": speed_button_rect}

    #------------------------------------Pop-up message------------------------------------------

    # Check for popup message and display if timer is active
    if popup_timer > 0:
        popup_timer -= 1  # Decrement the timer on each loop
        # Define popup message dimensions and position
        popup_width = 340
        popup_height = 40
        popup_x = (SCREEN_WIDTH - popup_width - 10)  # Center horizontally
        popup_y = (SCREEN_HEIGHT - 100 - popup_height) // 5   # Adjust vertical position as needed

        # Create popup rectangle
        popup_bg_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

        # Draw the popup background rectangle
        pygame.draw.rect(screen, GRAY, popup_bg_rect)

        # Render the popup message text
        popup_text = font.render(popup_message, True, WHITE)

        # Center the text within the popup rectangle
        popup_text_rect = popup_text.get_rect(center=popup_bg_rect.center)

        # Draw the text onto the screen at the specified position
        screen.blit(popup_text, popup_text_rect)            

    #------------------------------Camera code 2 -----------------------------------------------------------

   # Display camera feeds
    center_x = (SCREEN_WIDTH - 2 * SCREEN_WIDTH // 4) // 2
    center_y = (SCREEN_HEIGHT - 2 * SCREEN_HEIGHT // 4) // 2

    # Adjust this variable to move the camera screen(s) to the left
    shift_left_fraction = 0.2  # Adjust this value as needed
    # Calculate shift_left based on screen width
    shift_left = int(SCREEN_WIDTH * shift_left_fraction)

    for i, camera_rect in enumerate(camera_screen_rects):
        camera_surface = pygame.Surface((camera_rect.width, camera_rect.height))
        camera_surface.fill(BLACK)

        # Adjust the position to shift to the left by subtracting `shift_left`
        camera_rect.topleft = (center_x + (i % 2) * SCREEN_WIDTH // 4 - shift_left, center_y + (i // 2) * SCREEN_HEIGHT // 4)
        #camera_rect.topleft = (center_x + (i % 2) * SCREEN_WIDTH // 4, center_y + (i // 2) * SCREEN_HEIGHT // 4)
       # Draw smaller camera screen
        capture = captures[i]
        ret, frame = capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)  # Rotate frame
            frame = pygame.surfarray.make_surface(frame)
            frame = pygame.transform.scale(frame, (camera_rect.width, camera_rect.height))
            camera_surface.blit(frame, (0, 0))

        # Display camera name at the top
        font_size = 20
        camera_name = f"Cam {i + 1}"
        camera_name_text = font.render(camera_name, True, BLACK)
        camera_name_rect = camera_name_text.get_rect(topleft=(5, 5))  # Adjust position as needed
        camera_surface.blit(camera_name_text, camera_name_rect)
        screen.blit(camera_surface, camera_rect)

        #-------------------------------------------Stop button--------------------------------

    button_width = 165
    button_height = 50
    button_color = (255, 0, 0)  # Red
    button_text = "STOP"
    button_font = pygame.font.Font(None, 30)
    button_text_color = (255, 255, 255)  # White

    # Calculate button position dynamically based on screen dimensions
    button_x = (SCREEN_WIDTH - button_width) // 2
    button_y = SCREEN_HEIGHT - 170  # Positioned 100 pixels from the bottom

    # Create button rectangle
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

    # Specify the radius for the rounded corners
    corner_radius = 10  # Adjust based on the desired roundness

    # Draw the button with rounded corners
    pygame.draw.rect(screen, button_color, button_rect, border_radius=corner_radius)

    # Create and position the button text
    button_text_surface = button_font.render(button_text, True, button_text_color)
    button_text_rect = button_text_surface.get_rect(center=button_rect.center)

    # Blit the text onto the screen at the button's position
    screen.blit(button_text_surface, button_text_rect)

    # -----------------------------------Draw other elements first---------------------------------------------
        
    # After displaying camera feeds in your main loop
    # Define blank screen dimensions
    blank_screen_width = SCREEN_WIDTH // 3.5
    blank_screen_height = camera_screen_rects[0].height * 2  # Match the height with the first camera screen height

    # Define its position (right side of the last camera feed)
    # Assuming camera_screen_rects[-1] is the last camera screen's position
    last_camera_rect = camera_screen_rects[-1]
    blank_screen_x = last_camera_rect.right + 20  # 20 pixels to the right of the last camera screen
    blank_screen_y = camera_screen_rects[0].top  # Aligned to the top of the first camera screen

    # Calculate the fraction of the screen width to adjust the blank screen position
    blank_screen_fraction = 0.1  # Adjust this value as needed

    # Move the blank screen further to the right
    blank_screen_x += int(SCREEN_WIDTH * blank_screen_fraction)  # Adjust this value as needed to move it more to the right

    # Create a Rect for the blank screen
    blank_screen_rect = pygame.Rect(blank_screen_x, blank_screen_y, blank_screen_width, blank_screen_height)

    # Define the corner radius for the blank screen
    corner_radius = 20

    # Draw white background on the top of the blank screen
    top_background_rect = pygame.Rect(blank_screen_x, blank_screen_y, blank_screen_width, 50)  # Adjust height as needed
    pygame.draw.rect(screen, WHITE, top_background_rect)

    # Fill the blank screen with a darker shade to give it depth
    depth_color = (230, 230, 230)  # Slightly darker shade of gray
    pygame.draw.rect(screen, depth_color, blank_screen_rect)

    # Draw the blank screen with rounded corners
    pygame.draw.rect(screen, WHITE, blank_screen_rect)
    pygame.draw.rect(screen, (200, 200, 200), blank_screen_rect, border_radius=corner_radius)

    # Create a slightly lighter shade for the top and left edges to simulate light reflection
    light_color = (255, 255, 255)  # Lighter shade of gray
    pygame.draw.line(screen, light_color, blank_screen_rect.topleft, blank_screen_rect.topright, width=2)
    pygame.draw.line(screen, light_color, blank_screen_rect.topleft, blank_screen_rect.bottomleft, width=2)

    #------------------------------------------Motor X ---------------------------

    # Calculate label position (top center)
    label_x = blank_screen_rect.centerx
    label_y = blank_screen_rect.top + 70  # Adjust vertical position as needed

    # Calculate label background rectangle size and position
    label_background_width = 200
    label_background_height = 30
    label_background_x = label_x - label_background_width // 2  # Center horizontally
    label_background_y = label_y
    label_background_rect = pygame.Rect(label_background_x, label_background_y, label_background_width, label_background_height)

    # Draw a white background with rounded corners for the label
    pygame.draw.rect(screen, WHITE, label_background_rect, border_radius=corner_radius)  # Rounded corners

    # Render selected motor label inside the blank screen box
    selected_motor_label_text = font.render(selected_motor_label, True, BLACK)  # Render the label text
    label_text_rect = selected_motor_label_text.get_rect(center=label_background_rect.center)  # Position the label at the center of the white background
    screen.blit(selected_motor_label_text, label_text_rect)  # Blit

    # Define square dimensions
    square_size = 30
    square_padding = 50  # Padding between squares

    # Calculate the position for the first square
    first_square_x = blank_screen_rect.centerx - square_size - square_padding // 2
    first_square_y = label_background_rect.bottom + 20  # Adjust vertical position as needed
    first_square_rect = pygame.Rect(first_square_x, first_square_y, square_size, square_size)

    # Calculate the position for the second square
    second_square_x = blank_screen_rect.centerx + square_padding // 2
    second_square_y = first_square_y
    second_square_rect = pygame.Rect(second_square_x, second_square_y, square_size, square_size)

    # Draw the first square
    pygame.draw.rect(screen, BLACK, first_square_rect)
    # Draw the second square
    pygame.draw.rect(screen, BLACK, second_square_rect)

     # Define the label text for the Left side
    front_label_text = "Front"

    # Render the label text for the Left side
    front_label_rendered = font.render(front_label_text, True, BLACK)

    # Calculate the position of the label relative to the squares for the Left side
    front_label_x = first_square_rect.left - 70  # Adjust this value as needed
    front_label_y = first_square_rect.centery - front_label_rendered.get_height() // 2

    # Blit the label for the Left side onto the screen
    screen.blit(front_label_rendered, (front_label_x, front_label_y))

    # Define the label text for the Right side
    back_label_text = "Back"

    # Render the label text for the Right side
    back_label_rendered = font.render(back_label_text, True, BLACK)

    # Calculate the position of the label relative to the squares for the Right side
    back_label_x = second_square_rect.right + 20  # Adjust this value as needed
    back_label_y = second_square_rect.centery - back_label_rendered.get_height() // 2

    # Blit the label for the Right side onto the screen
    screen.blit(back_label_rendered, (back_label_x, back_label_y))
    # Draw lines to give 3D effect
    # Lines for the first square
    pygame.draw.line(screen, GRAY, first_square_rect.topleft, first_square_rect.topright, width=2)
    pygame.draw.line(screen, GRAY, first_square_rect.topleft, first_square_rect.bottomleft, width=2)
    pygame.draw.line(screen, WHITE, first_square_rect.topright, (first_square_rect.right, first_square_rect.top - 5), width=2)
    pygame.draw.line(screen, WHITE, first_square_rect.bottomleft, (first_square_rect.left - 5, first_square_rect.bottom), width=2)

    # Lines for the second square
    pygame.draw.line(screen, GRAY, second_square_rect.topleft, second_square_rect.topright, width=2)
    pygame.draw.line(screen, GRAY, second_square_rect.topleft, second_square_rect.bottomleft, width=2)
    pygame.draw.line(screen, WHITE, second_square_rect.topright, (second_square_rect.right, second_square_rect.top - 5), width=2)
    pygame.draw.line(screen, WHITE, second_square_rect.bottomleft, (second_square_rect.left - 5, second_square_rect.bottom), width=2)
    #--------------------------Motor Y---------------------------

    # Render the label text for motor Y
    motor_y_label_rendered = font.render(motor_y_label_text, True, BLACK)

    # Calculate the position of the label relative to the cubes for motor Y
    motor_y_label_x = (first_square_rect.left + second_square_rect.right) // 2  # Center horizontally between the cubes
    motor_y_label_y = second_square_rect.bottom + 40  # Adjust this value as needed to position below the cubes

    # Blit the label for motor Y onto the screen
    screen.blit(motor_y_label_rendered, (motor_y_label_x - motor_y_label_rendered.get_width() // 2, motor_y_label_y))

    # Calculate label background rectangle size and position for motor Y
    motor_y_label_background_width = 200  # Adjust width as needed
    motor_y_label_background_height = 30  # Adjust height as needed
    motor_y_label_background_x = motor_y_label_x - motor_y_label_background_width // 2  # Center horizontally
    motor_y_label_background_y = motor_y_label_y  # Adjust vertical position as needed
    motor_y_label_background_rect = pygame.Rect(motor_y_label_background_x, motor_y_label_background_y, motor_y_label_background_width, motor_y_label_background_height)

    # Draw a white background with rounded corners for the motor Y label
    pygame.draw.rect(screen, WHITE, motor_y_label_background_rect, border_radius=corner_radius)  # Rounded corners

    # Render motor Y label text inside the background box
    motor_y_label_text_rendered = font.render(motor_y_label_text, True, BLACK)  # Render the label text
    motor_y_label_text_rect = motor_y_label_text_rendered.get_rect(center=motor_y_label_background_rect.center)  # Position the label at the center of the white background
    screen.blit(motor_y_label_text_rendered, motor_y_label_text_rect)  # Blit

   # Define cube dimensions
    # Define square dimensions
    square_size = 30
    square_padding = 50  # Padding between squares

    # Calculate the position for the third square (below Motor Y)
    third_square_x = blank_screen_rect.centerx - square_size - square_padding // 2
    third_square_y = motor_y_label_background_rect.bottom + 20  # Adjust vertical position as needed
    third_square_rect = pygame.Rect(third_square_x, third_square_y, square_size, square_size)

    # Calculate the position for the fourth square
    fourth_square_x = blank_screen_rect.centerx + square_padding // 2
    fourth_square_y = third_square_y
    fourth_square_rect = pygame.Rect(fourth_square_x, fourth_square_y, square_size, square_size)

    # Draw the third square
    pygame.draw.rect(screen, BLACK, third_square_rect)
    # Draw the fourth square
    pygame.draw.rect(screen, BLACK, fourth_square_rect)

    # Define the label text for the Left side
    left_label_text = "Left"

    # Render the label text for the Left side
    left_label_rendered = font.render(left_label_text, True, BLACK)

    # Calculate the position of the label relative to the squares for the Left side
    left_label_x = third_square_rect.left - 70  # Adjust this value as needed
    left_label_y = third_square_rect.centery - left_label_rendered.get_height() // 2

    # Blit the label for the Left side onto the screen
    screen.blit(left_label_rendered, (left_label_x, left_label_y))

    # Define the label text for the Right side
    right_label_text = "Right"

    # Render the label text for the Right side
    right_label_rendered = font.render(right_label_text, True, BLACK)

    # Calculate the position of the label relative to the squares for the Right side
    right_label_x = fourth_square_rect.right + 20  # Adjust this value as needed
    right_label_y = fourth_square_rect.centery - right_label_rendered.get_height() // 2

    # Blit the label for the Right side onto the screen
    screen.blit(right_label_rendered, (right_label_x, right_label_y))

    # Draw lines to give 3D effect
    # Lines for the third square
    pygame.draw.line(screen, GRAY, third_square_rect.topleft, third_square_rect.topright, width=2)
    pygame.draw.line(screen, GRAY, third_square_rect.topleft, third_square_rect.bottomleft, width=2)
    pygame.draw.line(screen, WHITE, third_square_rect.topright, (third_square_rect.right, third_square_rect.top - 5), width=2)
    pygame.draw.line(screen, WHITE, third_square_rect.bottomleft, (third_square_rect.left - 5, third_square_rect.bottom), width=2)

    # Lines for the fourth square
    pygame.draw.line(screen, GRAY, fourth_square_rect.topleft, fourth_square_rect.topright, width=2)
    pygame.draw.line(screen, GRAY, fourth_square_rect.topleft, fourth_square_rect.bottomleft, width=2)
    pygame.draw.line(screen, WHITE, fourth_square_rect.topright, (fourth_square_rect.right, fourth_square_rect.top - 5), width=2)
    pygame.draw.line(screen, WHITE, fourth_square_rect.bottomleft, (fourth_square_rect.left - 5, fourth_square_rect.bottom), width=2)

    #--------------------------Motor Z-------------------------------

   # Render the label text for Motor Z
    motor_z_label_rendered = font.render(motor_z_label_text, True, BLACK)

    # Calculate the position of the label relative to the cubes for Motor Z
    motor_z_label_x = (third_square_rect.left + fourth_square_rect.right) // 2  # Center horizontally between the cubes of Motor Y
    motor_z_label_y = fourth_square_rect.bottom + 40  # Adjust this value as needed to position below the cubes

    # Blit the label for Motor Z onto the screen
    screen.blit(motor_z_label_rendered, (motor_z_label_x - motor_z_label_rendered.get_width() // 2, motor_z_label_y))

    # Calculate label background rectangle size and position for Motor Z
    motor_z_label_background_width = 200  # Adjust width as needed
    motor_z_label_background_height = 30  # Adjust height as needed
    motor_z_label_background_x = motor_z_label_x - motor_z_label_background_width // 2  # Center horizontally
    motor_z_label_background_y = motor_z_label_y  # Adjust vertical position as needed
    motor_z_label_background_rect = pygame.Rect(motor_z_label_background_x, motor_z_label_background_y, motor_z_label_background_width, motor_z_label_background_height)

    # Draw a white background with rounded corners for the Motor Z label
    pygame.draw.rect(screen, WHITE, motor_z_label_background_rect, border_radius=corner_radius)  # Rounded corners

    # Render Motor Z label text inside the background box
    motor_z_label_text_rendered = font.render(motor_z_label_text, True, BLACK)  # Render the label text
    motor_z_label_text_rect = motor_z_label_text_rendered.get_rect(center=motor_z_label_background_rect.center)  # Position the label at the center of the white background
    screen.blit(motor_z_label_text_rendered, motor_z_label_text_rect)  # Blit

    # Define square dimensions
    square_size = 30
    square_padding = 50  # Padding between squares

    # Calculate the position for the fifth square (below Motor Z)
    fifth_square_x = blank_screen_rect.centerx - square_size - square_padding // 2
    fifth_square_y = motor_z_label_background_rect.bottom + 20  # Adjust vertical position as needed
    fifth_square_rect = pygame.Rect(fifth_square_x, fifth_square_y, square_size, square_size)

    # Calculate the position for the sixth square
    sixth_square_x = blank_screen_rect.centerx + square_padding // 2
    sixth_square_y = fifth_square_y
    sixth_square_rect = pygame.Rect(sixth_square_x, sixth_square_y, square_size, square_size)

    # Draw the fifth square
    pygame.draw.rect(screen, BLACK, fifth_square_rect)
    # Draw the sixth square
    pygame.draw.rect(screen, BLACK, sixth_square_rect)

    # Define the label text for the Top side
    top_label_text = "Top"

    # Render the label text for the top side
    top_label_rendered = font.render(top_label_text, True, BLACK)

    # Calculate the position of the label relative to the squares for the top side
    top_label_x = fifth_square_rect.left - 70  # Adjust this value as needed
    top_label_y = fifth_square_rect.centery - top_label_rendered.get_height() // 2

    # Blit the label for the top side onto the screen
    screen.blit(top_label_rendered, (top_label_x, top_label_y))

    # Define the label text for the Down side
    down_label_text = "Down"

    # Render the label text for the down side
    down_label_rendered = font.render(down_label_text, True, BLACK)

    # Calculate the position of the label relative to the squares for the Down side
    down_label_x = sixth_square_rect.right + 20  # Adjust this value as needed
    down_label_y = sixth_square_rect.centery - down_label_rendered.get_height() // 2

    # Blit the label for the Down side onto the screen
    screen.blit(down_label_rendered, (down_label_x, down_label_y))

    # Draw lines to give 3D effect for the fifth square
    pygame.draw.line(screen, GRAY, fifth_square_rect.topleft, fifth_square_rect.topright, width=2)
    pygame.draw.line(screen, GRAY, fifth_square_rect.topleft, fifth_square_rect.bottomleft, width=2)
    pygame.draw.line(screen, WHITE, fifth_square_rect.topright, (fifth_square_rect.right, fifth_square_rect.top - 5), width=2)
    pygame.draw.line(screen, WHITE, fifth_square_rect.bottomleft, (fifth_square_rect.left - 5, fifth_square_rect.bottom), width=2)

    # Draw lines to give 3D effect for the sixth square
    pygame.draw.line(screen, GRAY, sixth_square_rect.topleft, sixth_square_rect.topright, width=2)
    pygame.draw.line(screen, GRAY, sixth_square_rect.topleft, sixth_square_rect.bottomleft, width=2)
    pygame.draw.line(screen, WHITE, sixth_square_rect.topright, (sixth_square_rect.right, sixth_square_rect.top - 5), width=2)
    pygame.draw.line(screen, WHITE, sixth_square_rect.bottomleft, (sixth_square_rect.left - 5, sixth_square_rect.bottom), width=2)

    #------------Turning green after pressing motor x button--------------
    # Check if Motor X is selected
    if selected_motor == 'X':
        # Draw the first cube in green
        pygame.draw.rect(screen, GREEN, first_square_rect)
        # Draw the second cube in green
        pygame.draw.rect(screen, GREEN, second_square_rect)
    
    # Draw the cubes in their default color (black) if Motor X is not selected
    else:
        # Draw the first cube in black
        pygame.draw.rect(screen, BLACK, first_square_rect)
        # Draw the second cube in black
        pygame.draw.rect(screen, BLACK, second_square_rect)

# Update display
    #------------Turning green after pressing motor Y button--------------
    # Check if Motor X is selected
    if selected_motor == 'Y':
        # Draw the third cube in green
        pygame.draw.rect(screen, GREEN, third_square_rect)
        # Draw the fourth cube in green
        pygame.draw.rect(screen, GREEN, fourth_square_rect)
    
    # Draw the cubes in their default color (black) if Motor X is not selected
    else:
        # Draw the third cube in black
        pygame.draw.rect(screen, BLACK, third_square_rect)
        # Draw the fourth cube in black
        pygame.draw.rect(screen, BLACK, fourth_square_rect)

# Update display
#------------Turning green after pressing motor Z button--------------
    # Check if Motor X is selected
    if selected_motor == 'Z':
        pygame.draw.rect(screen, GREEN, fifth_square_rect)
        pygame.draw.rect(screen, GREEN, sixth_square_rect)
    else:   
        pygame.draw.rect(screen, BLACK, fifth_square_rect)
        pygame.draw.rect(screen, BLACK, sixth_square_rect)

    # Update display
    pygame.display.flip()

      # Cleanup
for capture in captures:
    capture.release()
pygame.quit()