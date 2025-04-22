import pygame
import sys
import requests
from io import BytesIO
import random

# Initialize pygame
pygame.init()

# Set up screen
WIDTH, HEIGHT = 800, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dino Game")

# Clock
clock = pygame.time.Clock()
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Load images from web
def load_image_from_url(url):
    response = requests.get(url)
    return pygame.image.load(BytesIO(response.content)).convert_alpha()

# Dino and cactus images
dino_url = 'https://i.pinimg.com/736x/d7/cf/d7/d7cfd7fa57e2bbc4353d6d0c3b279597.jpg'
cactus_url = 'https://media.gettyimages.com/id/1349703132/vector/cactus-sketch-illustration.jpg?s=612x612&w=gi&k=20&c=nwymXUxE8YYxVLrIuX3-Wd4Kq1Edv6gbahgha-TOuKM='

dino_img = load_image_from_url(dino_url)
cactus_img = load_image_from_url(cactus_url)

# Resize
dino_img = pygame.transform.scale(dino_img, (60, 60))
cactus_img = pygame.transform.scale(cactus_img, (40, 70))

# Dino settings
dino_x = 50
dino_y = HEIGHT - 100
dino_jump = False
jump_velocity = 0

# Cactus pattern settings
cactus_groups = []
cactus_speed = 7

# Score
score = 0

def create_cactus_group():
    # Randomize the number of cacti in the group (1, 2, or 3)
    num_cacti = random.choice([1, 2, 3])
    group = []
    x_start = WIDTH + random.randint(0, 200)
    previous_cactus_x = x_start  # To control spacing between cacti

    # Randomize spacing between cacti in the group
    for i in range(num_cacti):
        # Adjust x based on the previous cactus' position and random spacing
        cactus_x = previous_cactus_x + random.randint(80, 200)
        cactus_y = HEIGHT - 90
        group.append(pygame.Rect(cactus_x, cactus_y, cactus_img.get_width(), cactus_img.get_height()))
        previous_cactus_x = cactus_x  # Update the previous cactus' position

    return group

# Add the first cactus group
cactus_groups.append(create_cactus_group())

# Font for score
font = pygame.font.SysFont('Arial', 30)

# Main game loop
running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Jump on key press
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not dino_jump:
                dino_jump = True
                jump_velocity = -15

    # Dino jump mechanics
    if dino_jump:
        dino_y += jump_velocity
        jump_velocity += 1
        if dino_y >= HEIGHT - 100:
            dino_y = HEIGHT - 100
            dino_jump = False

    # Move and draw cactus groups
    for group in cactus_groups:
        for cactus in group:
            cactus.x -= cactus_speed
            screen.blit(cactus_img, (cactus.x, cactus.y))

    # Add new cactus group when the last group moves off screen
    if cactus_groups[-1][0].x < WIDTH - random.randint(200, 400):
        cactus_groups.append(create_cactus_group())

    # Remove cactus group off screen
    if cactus_groups[0][-1].x < -50:
        cactus_groups.pop(0)
        score += 1  # Increment score when a group is removed

    # Collision detection
    dino_rect = pygame.Rect(dino_x, dino_y, 60, 60)
    for group in cactus_groups:
        for cactus in group:
            if dino_rect.colliderect(cactus):
                # Display final score when game ends
                print(f"Game Over! Final Score: {score}")
                pygame.time.wait(1000)
                running = False

    # Draw dino
    screen.blit(dino_img, (dino_x, dino_y))

    # Display the score
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
sys.exit()
