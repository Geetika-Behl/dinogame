import pygame
import sys
import random

# === Game Configuration ===
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
GROUND_Y = 400
FPS = 60

# === Initialization ===
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Dino Game")
game_font = pygame.font.Font("assets/PressStart2P-Regular.ttf", 24)

# === Load Assets ===
def load_scaled_image(path, size):
    return pygame.transform.scale(pygame.image.load(path), size)

# === Classes ===
class Dino(pygame.sprite.Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__()
        self.running_frames = [
            load_scaled_image("assets/Dino1.png", (50, 70)),
            load_scaled_image("assets/Dino2.png", (50, 70))
        ]
        self.ducking_frames = [
            load_scaled_image("assets/DinoDucking1.png", (70, 40)),
            load_scaled_image("assets/DinoDucking2.png", (70, 40))
        ]
        self.is_ducking = False
        self.frames = self.running_frames
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(midbottom=(x_pos, y_pos))
        self.original_bottom = y_pos
        self.gravity = 0
        self.jump_force = -30
        self.gravity_increment = 2.0
        self.animation_timer = 0
        self.animation_interval = 100
        self.collision_rect = self.rect.inflate(-20, -20)

    def jump(self):
        if self.rect.bottom >= self.original_bottom:
            self.gravity = self.jump_force
            jump_sfx.play()

    def duck(self):
        if not self.is_ducking:
            self.is_ducking = True
            self.frames = self.ducking_frames
            bottom = self.rect.bottom
            self.image = self.frames[0]
            self.rect = self.image.get_rect(midbottom=(self.rect.centerx, bottom))

    def unduck(self):
        if self.is_ducking:
            self.is_ducking = False
            self.frames = self.running_frames
            bottom = self.rect.bottom
            self.image = self.frames[0]
            self.rect = self.image.get_rect(midbottom=(self.rect.centerx, bottom))

    def apply_gravity(self):
        self.gravity += self.gravity_increment
        self.rect.y += self.gravity
        if self.rect.bottom >= self.original_bottom:
            self.rect.bottom = self.original_bottom
            self.gravity = 0

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.animation_timer > self.animation_interval:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            self.animation_timer = now

    def update(self):
        self.apply_gravity()
        self.animate()
        self.collision_rect = self.rect.inflate(-20, -20)

class Cactus(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        cactus_type = random.randint(1, 6)
        self.image = load_scaled_image(f"assets/cacti/cactus{cactus_type}.png", (60, 80))
        self.rect = self.image.get_rect(midbottom=(WINDOW_WIDTH, GROUND_Y))

    def update(self):
        self.rect.x -= game_speed
        if self.rect.right < 0:
            self.kill()

class Ptero(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frames = [
            load_scaled_image("assets/Ptero1.png", (80, 52)),
            load_scaled_image("assets/Ptero2.png", (80, 52))
        ]
        self.image = self.frames[0]
        self.rect = self.image.get_rect(midbottom=(WINDOW_WIDTH + 100, random.choice([280, 350])))
        self.index = 0

    def update(self):
        self.index = (self.index + 0.1) % 2
        self.image = self.frames[int(self.index)]
        self.rect.x -= game_speed
        if self.rect.right < 0:
            self.kill()

class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_scaled_image("assets/cloud.png", (200, 80))
        self.rect = self.image.get_rect(midbottom=(WINDOW_WIDTH + 100, random.randint(50, 300)))

    def update(self):
        self.rect.x -= 1
        if self.rect.right < 0:
            self.kill()

# === Sound Effects ===
death_sfx = pygame.mixer.Sound("assets/sfx/lose.mp3")
points_sfx = pygame.mixer.Sound("assets/sfx/100points.mp3")
jump_sfx = pygame.mixer.Sound("assets/sfx/jump.mp3")

# === Game Elements ===
ground = load_scaled_image("assets/ground.png", (WINDOW_WIDTH, 20))
ground_x = 0
dino = Dino(100, GROUND_Y)
dino_group = pygame.sprite.GroupSingle(dino)
obstacle_group = pygame.sprite.Group()
cloud_group = pygame.sprite.Group()

# === Game Variables ===
game_speed = 10
score = 0
game_over = False
obstacle_timer = 0
obstacle_cooldown = 800

# === Events ===
CLOUD_EVENT = pygame.USEREVENT
pygame.time.set_timer(CLOUD_EVENT, 3000)

# === Game Loop ===
while True:
    screen.fill("white")

    # Input Handling
    keys = pygame.key.get_pressed()
    if keys[pygame.K_DOWN]:
        dino.duck()
    else:
        dino.unduck()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == CLOUD_EVENT:
            cloud_group.add(Cloud())
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_UP):
                if game_over:
                    game_over = False
                    score = 0
                    game_speed = 5
                    obstacle_group.empty()
                    cloud_group.empty()
                dino.jump()

    if not game_over:
        score += 0.1
        if int(score) % 100 == 0 and int(score) > 0:
            points_sfx.play()

        game_speed += 0.0025

        if pygame.time.get_ticks() - obstacle_timer >= obstacle_cooldown:
            obstacle_group.add(Cactus() if random.random() < 0.7 else Ptero())
            obstacle_timer = pygame.time.get_ticks()

        dino_group.update()
        obstacle_group.update()
        cloud_group.update()

        if any(dino.collision_rect.colliderect(ob.rect) for ob in obstacle_group):
            death_sfx.play()
            game_over = True

        if not game_over:
            ground_x = 0 if ground_x <= -WINDOW_WIDTH else ground_x - game_speed

    # Drawing
    cloud_group.draw(screen)
    screen.blit(ground, (ground_x, GROUND_Y))
    screen.blit(ground, (ground_x + WINDOW_WIDTH, GROUND_Y))
    dino_group.draw(screen)
    obstacle_group.draw(screen)
    score_text = game_font.render(str(int(score)), True, "black")
    screen.blit(score_text, (1150, 10))

    if game_over:
        game_over_text = game_font.render("Game Over!", True, "black")
        screen.blit(game_over_text, game_over_text.get_rect(center=(WINDOW_WIDTH / 2, 300)))
        final_score_text = game_font.render(f"Score: {int(score)}", True, "black")
        screen.blit(final_score_text, final_score_text.get_rect(center=(WINDOW_WIDTH / 2, 350)))

    pygame.display.update()
    clock.tick(FPS)
