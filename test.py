import pygame
import math

# Initialize Pygame
pygame.init()

# Set the window size
window_size = (640, 480)

# Create the window
screen = pygame.display.set_mode(window_size)

# Load the player sprite and get its rect
player_image = pygame.image.load("./assets/PNG/playerShip1_blue.png").convert_alpha()
og_player_image = pygame.image.load("./assets/PNG/playerShip1_blue.png").convert_alpha()
player_rect = player_image.get_rect()

# Set the player's starting position
player_rect.center = (320, 240)

# Set the player's speed (in pixels per frame)
player_speed = 5

# Run the game loop
running = True
while running:
    # Check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get the mouse position
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Calculate the angle between the player and the mouse
    rel_x, rel_y = mouse_x - player_rect.centerx, mouse_y - player_rect.centery
    angle = math.atan2(rel_y, rel_x)
    angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)


    # Rotate the player image
    player_image = pygame.transform.rotate(og_player_image, int(angle)-90)
    player_rect = player_image.get_rect(center=player_rect.center)

    # Clear the screen
    screen.fill((255, 255, 255))

    # Draw the player
    screen.blit(player_image, player_rect)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
