import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900  # Increased height for the plant pool
LANE_COUNT = 5
LANE_HEIGHT = 100
CELL_WIDTH = 100  # Grid cell width
GRID_COLUMNS = SCREEN_WIDTH // CELL_WIDTH
PLANT_POOL_HEIGHT = 100  # Height of the plant pool menu

# Colors
WHITE = (255, 255, 255)
GREEN = (144, 238, 144)
DARK_GREEN = (34, 139, 34)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defense Game")

# Game Clock
clock = pygame.time.Clock()

# Load Sprites
plant_image = pygame.image.load("assets/plant.png")
plant_image = pygame.transform.scale(plant_image, (CELL_WIDTH - 10, LANE_HEIGHT - 10))

zombie_image = pygame.image.load("assets/zombie.png")
zombie_image = pygame.transform.scale(zombie_image, (CELL_WIDTH - 30, LANE_HEIGHT - 20))

bullet_image = pygame.image.load("assets/bullet.png")
bullet_image = pygame.transform.scale(bullet_image, (10, 10))

# Game objects
shooter_plants = [[None for _ in range(GRID_COLUMNS)] for _ in range(LANE_COUNT)]
zombies = []
bullets = []

# Drag-and-drop mechanics
dragging_plant = False
dragged_plant_pos = None


# Shooter Plant Class
class ShooterPlant:
    def __init__(self, lane, col):
        self.lane = lane
        self.col = col
        self.x = col * CELL_WIDTH
        self.y = lane * LANE_HEIGHT + 5
        self.bullets = 1
        self.max_bullets = 4
        self.reload_timer = 0
        self.first_bullet_reloaded = False  # Flag to track if first bullet has been reloaded

    def reload(self):
        # Reload bullets over time
        if self.bullets < self.max_bullets:
            self.reload_timer += 1
            if self.reload_timer >= 60:  # Reload one bullet per second
                self.bullets += 1
                self.reload_timer = 0

                # Set flag after the first bullet reloads
                if not self.first_bullet_reloaded :
                    self.first_bullet_reloaded = True

        # If the first bullet has been reloaded and the plant has 0 bullets, remove it
        if self.bullets < 0:
            shooter_plants[self.lane][self.col] = None  # Remove the plant from the grid

    def shoot(self):
        if self.bullets >= 0:
            self.bullets -= 1
            bullets.append(Bullet(self.x + CELL_WIDTH, self.y + LANE_HEIGHT // 2 - 5))
        if self.bullets < 0:
            shooter_plants[self.lane][self.col] = None  # Remove the plant from the grid

    def draw(self):
        screen.blit(plant_image, (self.x + 5, self.y))
        # Display bullet count
        font = pygame.font.Font(None, 24)
        text = font.render(f"{self.bullets}/{self.max_bullets}", True, BLACK)
        screen.blit(text, (self.x + 5, self.y + LANE_HEIGHT - 25))

    def place(self):
        # Reset flag when placed
        self.first_bullet_reloaded = False  # Ensure the flag is reset when the plant is placed




# Bullet Class
class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 10

    def move(self):
        self.x += self.speed

    def draw(self):
        screen.blit(bullet_image, (self.x, self.y))


# Zombie Class
class Zombie:
    def __init__(self, lane):
        self.lane = lane
        self.x = SCREEN_WIDTH
        self.y = lane * LANE_HEIGHT + 10
        self.health = 3
        self.speed = 1

    def move(self):
        self.x -= self.speed

    def draw(self):
        screen.blit(zombie_image, (self.x, self.y))


# Check for losing condition
def check_loss():
    for zombie in zombies:
        if zombie.x <= 0:
            return True
    return False


# Draw the grid
def draw_background():
    screen.fill(GREEN)  # Fill the entire screen with the game background color

    # Draw the grid lanes
    for i in range(LANE_COUNT):
        lane_color = DARK_GREEN if i % 2 == 0 else GREEN
        pygame.draw.rect(screen, lane_color, (0, i * LANE_HEIGHT, SCREEN_WIDTH, LANE_HEIGHT))
        pygame.draw.line(screen, BLACK, (0, i * LANE_HEIGHT), (SCREEN_WIDTH, i * LANE_HEIGHT), 2)
        for j in range(GRID_COLUMNS):
            pygame.draw.line(screen, BLACK, (j * CELL_WIDTH, 0), (j * CELL_WIDTH, LANE_HEIGHT * LANE_COUNT), 2)

    # Fill the plant pool area
    pygame.draw.rect(screen, WHITE, (0, LANE_COUNT * LANE_HEIGHT, SCREEN_WIDTH, PLANT_POOL_HEIGHT))




# Draw the plant pool
def draw_plant_pool():
    pool_y = LANE_COUNT * LANE_HEIGHT
    screen.fill(WHITE, rect=(0, pool_y, SCREEN_WIDTH, PLANT_POOL_HEIGHT))
    screen.blit(plant_image, (CELL_WIDTH // 2, pool_y + (PLANT_POOL_HEIGHT - LANE_HEIGHT) // 2))
    pygame.draw.rect(screen, BLACK, (CELL_WIDTH // 2, pool_y + (PLANT_POOL_HEIGHT - LANE_HEIGHT) // 2, CELL_WIDTH, LANE_HEIGHT), 2)
    return CELL_WIDTH // 2, pool_y + (PLANT_POOL_HEIGHT - LANE_HEIGHT) // 2, CELL_WIDTH, LANE_HEIGHT


# Spawn zombies randomly
def spawn_zombies():
    if random.randint(0, 100) < 2:  # 2% chance each frame to spawn a zombie
        lane = random.randint(0, LANE_COUNT - 1)
        zombies.append(Zombie(lane))


# Main game loop
def main():
    global dragging_plant, dragged_plant_pos

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Start dragging a plant
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                pool_x, pool_y, pool_w, pool_h = draw_plant_pool()
                if pool_x <= mx <= pool_x + pool_w and pool_y <= my <= pool_y + pool_h:
                    dragging_plant = True
                    dragged_plant_pos = (mx, my)

            # Drop the plant onto the grid
            # Drop the plant onto the grid
          # Drop the plant onto the grid
            if event.type == pygame.MOUSEBUTTONUP and dragging_plant:
                mx, my = pygame.mouse.get_pos()
                lane = my // LANE_HEIGHT
                col = mx // CELL_WIDTH
                if 0 <= lane < LANE_COUNT and 0 <= col < GRID_COLUMNS and not shooter_plants[lane][col]:
                    shooter_plants[lane][col] = ShooterPlant(lane, col)
                    shooter_plants[lane][col].place()  # Call the place method to reset reload state
                dragging_plant = False


            # Click to shoot plants
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                lane = my // LANE_HEIGHT
                col = mx // CELL_WIDTH
                if 0 <= lane < LANE_COUNT and 0 <= col < GRID_COLUMNS:
                    plant = shooter_plants[lane][col]
                    if plant:
                        plant.shoot()

        # Draw the game elements
        draw_background()

        # Draw plant pool
        pool_x, pool_y, pool_w, pool_h = draw_plant_pool()

        # Draw dragged plant
        if dragging_plant:
            mx, my = pygame.mouse.get_pos()
            screen.blit(plant_image, (mx - CELL_WIDTH // 2, my - LANE_HEIGHT // 2))

        # Update and draw shooter plants
        for lane in shooter_plants:
            for plant in lane:
                if plant:
                    plant.reload()
                    plant.draw()

        # Update and draw bullets
        for bullet in bullets[:]:
            bullet.move()
            bullet.draw()
            if bullet.x > SCREEN_WIDTH:
                bullets.remove(bullet)

        # Update and draw zombies
        for zombie in zombies[:]:
            zombie.move()
            zombie.draw()
            # Check for collisions with bullets
            for bullet in bullets[:]:
                if zombie.x < bullet.x < zombie.x + CELL_WIDTH - 30 and zombie.y < bullet.y < zombie.y + LANE_HEIGHT - 20:
                    zombie.health -= 1
                    bullets.remove(bullet)
                    if zombie.health <= 0:
                        zombies.remove(zombie)
                        break

        # Spawn new zombies
        spawn_zombies()

        # Check for losing condition
        if check_loss():
            font = pygame.font.Font(None, 72)
            text = font.render("You Lose!", True, RED)
            screen.blit(text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
            pygame.display.flip()
            pygame.time.delay(3000)
            pygame.quit()
            sys.exit()

        # Update the display
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
