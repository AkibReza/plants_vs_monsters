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
pygame.display.set_caption("Plants Vs Monsters")

# Game Clock
clock = pygame.time.Clock()

# Load Sprites
plant_image = pygame.image.load("assets/plant.png")
plant_image = pygame.transform.scale(plant_image, (CELL_WIDTH - 10, LANE_HEIGHT - 10))

freezing_plant_image = pygame.image.load("assets/freezing_plant.png")
freezing_plant_image = pygame.transform.scale(freezing_plant_image, (CELL_WIDTH - 10, LANE_HEIGHT - 10))

repeater_image = pygame.image.load("assets/repeater.png")
repeater_image = pygame.transform.scale(repeater_image, (CELL_WIDTH - 10, LANE_HEIGHT - 10))

zombie_image = pygame.image.load("assets/zombie.png")
zombie_image = pygame.transform.scale(zombie_image, (CELL_WIDTH - 30, LANE_HEIGHT - 20))

zombie_2_image = pygame.image.load("assets/zombie_2.png")
zombie_2_image = pygame.transform.scale(zombie_2_image, (CELL_WIDTH - 30, LANE_HEIGHT - 20))

zombie_3_image = pygame.image.load("assets/zombie_3.png")
zombie_3_image = pygame.transform.scale(zombie_3_image, (CELL_WIDTH - 30, LANE_HEIGHT - 20))

freezed_zombie_image = pygame.image.load("assets/freezed_zombie.png")
freezed_zombie_image = pygame.transform.scale(freezed_zombie_image, (CELL_WIDTH - 30, LANE_HEIGHT - 20))

bullet_image = pygame.image.load("assets/bullet.png")
bullet_image = pygame.transform.scale(bullet_image, (50, 50))

ice_bullet_image = pygame.image.load("assets/ice_bullet.png")
ice_bullet_image = pygame.transform.scale(ice_bullet_image, (50, 50))

repeater_bullet_image = pygame.image.load("assets/repeater_bullet.png")
repeater_bullet_image = pygame.transform.scale(repeater_bullet_image, (50, 50))

wallnut_image = pygame.image.load("assets/wallnut.png")
wallnut_image = pygame.transform.scale(wallnut_image, (CELL_WIDTH - 10, LANE_HEIGHT - 10))

cherry_bomb_image = pygame.image.load("assets/cherry_bomb.png")
cherry_bomb_image = pygame.transform.scale(cherry_bomb_image, (CELL_WIDTH - 10, LANE_HEIGHT - 10))

shovel_image = pygame.image.load("assets/shovel.png")
shovel_image = pygame.transform.scale(shovel_image, (CELL_WIDTH - 10, LANE_HEIGHT - 10))


# Game objects
shooter_plants = [[None for _ in range(GRID_COLUMNS)] for _ in range(LANE_COUNT)]
zombies = []
bullets = []
coins = 100

# Drag-and-drop mechanics
dragging_plant = False
dragged_plant_pos = None
plant_type_dragged = None

plant_costs = {
    "normal_plant": 10,
    "freezing_plant": 30,
    "repeater": 30,
    "wallnut": 25,
    "cherry_bomb": 50,
}


# Shooter Plant Class
class ShooterPlant:
    def __init__(self, lane, col,health=5):
        self.lane = lane
        self.col = col
        self.x = col * CELL_WIDTH
        self.y = lane * LANE_HEIGHT + 5
        self.shoot_timer = 0
        self.health = health

    def auto_shoot(self):
        self.shoot_timer += 1
        if self.shoot_timer >= 90:  # Shoot every 1.5 seconds
            for zombie in zombies:
                if zombie.lane == self.lane:
                    bullets.append(Bullet(self.x + CELL_WIDTH, self.y + LANE_HEIGHT // 2 - 5))
                    self.shoot_timer = 0
                    break
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            shooter_plants[self.lane][self.col] = None

    def draw(self):
        screen.blit(plant_image, (self.x + 5, self.y))


# Freezing Plant Class
class FreezingPlant(ShooterPlant):
    def auto_shoot(self):
        self.shoot_timer += 1
        if self.shoot_timer >= 120:  # Shoot every 2 seconds
            for zombie in zombies:
                if zombie.lane == self.lane:
                    bullets.append(IceBullet(self.x + CELL_WIDTH, self.y + LANE_HEIGHT // 2 - 5))
                    self.shoot_timer = 0
                    break

    def draw(self):
        screen.blit(freezing_plant_image, (self.x + 5, self.y))


# Repeater Class
class Repeater(ShooterPlant):
    def auto_shoot(self):
        self.shoot_timer += 1
        if self.shoot_timer >= 60:  # Shoot every 1 second
            for zombie in zombies:
                if zombie.lane == self.lane:
                    # Shoots two bullets in quick succession
                    bullets.append(SmallBullet(self.x + CELL_WIDTH, self.y + LANE_HEIGHT // 2 - 5))
                    bullets.append(SmallBullet(self.x + CELL_WIDTH + 20, self.y + LANE_HEIGHT // 2 - 5))
                    self.shoot_timer = 0
                    break

    def draw(self):
        screen.blit(repeater_image, (self.x + 5, self.y))

# Wallnut Plant Class
class Wallnut(ShooterPlant):
    def __init__(self, lane, col):
        super().__init__(lane, col, health=100
        )  # High health value
        self.x = col * CELL_WIDTH
        self.y = lane * LANE_HEIGHT + 5

    def auto_shoot(self):
        # Wallnut doesn't shoot, so this method does nothing
        pass

    def draw(self):
        # Use a specific sprite for the Wallnut
        screen.blit(wallnut_image, (self.x + 5, self.y))

# CherryBomb Plant Class
class CherryBomb(ShooterPlant):
    def __init__(self, lane, col):
        super().__init__(lane, col, health=1)  # Minimal health as it explodes quickly
        self.explode_timer = 60  # Explodes after 1 second (60 frames at 60 FPS)

    def auto_shoot(self):
        # Countdown to explosion
        self.explode_timer -= 1
        if self.explode_timer <= 0:
            self.explode()  # Trigger the explosion

    def explode(self):
        # Remove all zombies in a 1-grid radius
        for zombie in zombies[:]:
            zombie_col = int(zombie.x // CELL_WIDTH)
            zombie_lane = zombie.lane

            # Check if the zombie is within 1-grid range (including diagonals)
            if abs(zombie_col - self.col) <= 1 and abs(zombie_lane - self.lane) <= 1:
                zombies.remove(zombie)

        # Remove the CherryBomb plant after explosion
        shooter_plants[self.lane][self.col] = None

    def draw(self):
        # Use a specific sprite for the CherryBomb
        screen.blit(cherry_bomb_image, (self.x + 5, self.y))


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


# Ice Bullet Class
class IceBullet(Bullet):
    def draw(self):
        screen.blit(ice_bullet_image, (self.x, self.y))


# Small Bullet Class
class SmallBullet(Bullet):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.damage = 2  # Twice the damage of normal bullets

    def draw(self):
        screen.blit(repeater_bullet_image, (self.x, self.y))



speed_multiplier = 1.0

# Zombie Class
class Zombie:
    def __init__(self, lane):
        self.lane = lane
        self.x = SCREEN_WIDTH
        self.y = lane * LANE_HEIGHT + 10
        self.health = 5
        self.base_speed = 1  # Even slower base speed
        self.speed = self.base_speed * speed_multiplier
        self.frozen = False
        self.frozen_timer = 0
        self.eating_plant = None
        self.reward = 10  # Default reward

    def move(self):
        if self.eating_plant:  # Stop moving if eating a plant
            self.eating_plant.take_damage(0.1)  # Slowly damage the plant
            if self.eating_plant.health <= 0:  # Once the plant is destroyed
                self.eating_plant = None  # Stop eating
        elif not self.frozen:  # If not frozen or eating, continue moving
            self.x -= self.speed * speed_multiplier  # Apply speed multiplier
        else:  # Handle frozen timer
            self.frozen_timer += 1
            if self.frozen_timer >= 300:  # 5 seconds freeze (60 FPS * 5)
                self.frozen = False
                self.frozen_timer = 0

    def detect_plant(self):
    # Check for plants in front of the zombie
        col = int(self.x // CELL_WIDTH)  # Ensure column index is an integer
        if 0 <= col < GRID_COLUMNS:
            plant = shooter_plants[self.lane][col]
            if plant:  # If there's a plant in the zombie's lane and column
                self.eating_plant = plant  # Start eating this plant

    def draw(self):
        if self.frozen:
            screen.blit(freezed_zombie_image, (self.x, self.y))
        else:
            screen.blit(zombie_image, (self.x, self.y))


# Zombie Type 2 Class
class Zombie2(Zombie):
    def __init__(self, lane):
        super().__init__(lane)
        self.health = 10  # Increased health
        self.base_speed = 1  # Even slower base speed
        self.speed = self.base_speed * speed_multiplier
        self.reward = 20  # Higher reward


    def draw(self):
        if self.frozen:
            screen.blit(freezed_zombie_image, (self.x, self.y))
        else:
            screen.blit(zombie_2_image, (self.x, self.y))


# Zombie Type 3 Class
class Zombie3(Zombie):
    def __init__(self, lane):
        super().__init__(lane)
        self.health = 15  # Increased health
        self.base_speed = 1  # Even slower base speed
        self.speed = self.base_speed * speed_multiplier
        self.reward = 30  # Highest reward

    def draw(self):
        if self.frozen:
            screen.blit(freezed_zombie_image, (self.x, self.y))
        else:
            screen.blit(zombie_3_image, (self.x, self.y))


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

    font = pygame.font.Font(None, 24)  # Font for the cost text
    plant_positions = {}

    # Normal plant
    x, y = CELL_WIDTH // 2, pool_y + (PLANT_POOL_HEIGHT - LANE_HEIGHT) // 2
    screen.blit(plant_image, (x, y))
    pygame.draw.rect(screen, BLACK, (x, y, CELL_WIDTH, LANE_HEIGHT), 2)
    cost_text = font.render(f"{plant_costs['normal_plant']}", True, BLACK)
    screen.blit(cost_text, (x + 5, y + LANE_HEIGHT - 20))
    plant_positions["normal_plant"] = (x, y, CELL_WIDTH, LANE_HEIGHT)

    # Freezing plant
    x, y = 3 * CELL_WIDTH // 2, pool_y + (PLANT_POOL_HEIGHT - LANE_HEIGHT) // 2
    screen.blit(freezing_plant_image, (x, y))
    pygame.draw.rect(screen, BLACK, (x, y, CELL_WIDTH, LANE_HEIGHT), 2)
    cost_text = font.render(f"{plant_costs['freezing_plant']}", True, BLACK)
    screen.blit(cost_text, (x + 5, y + LANE_HEIGHT - 20))
    plant_positions["freezing_plant"] = (x, y, CELL_WIDTH, LANE_HEIGHT)

    # Repeater
    x, y = 5 * CELL_WIDTH // 2, pool_y + (PLANT_POOL_HEIGHT - LANE_HEIGHT) // 2
    screen.blit(repeater_image, (x, y))
    pygame.draw.rect(screen, BLACK, (x, y, CELL_WIDTH, LANE_HEIGHT), 2)
    cost_text = font.render(f"{plant_costs['repeater']}", True, BLACK)
    screen.blit(cost_text, (x + 5, y + LANE_HEIGHT - 20))
    plant_positions["repeater"] = (x, y, CELL_WIDTH, LANE_HEIGHT)

    # Wallnut
    x, y = 7 * CELL_WIDTH // 2, pool_y + (PLANT_POOL_HEIGHT - LANE_HEIGHT) // 2
    screen.blit(wallnut_image, (x, y))
    pygame.draw.rect(screen, BLACK, (x, y, CELL_WIDTH, LANE_HEIGHT), 2)
    cost_text = font.render(f"{plant_costs['wallnut']}", True, BLACK)
    screen.blit(cost_text, (x + 5, y + LANE_HEIGHT - 20))
    plant_positions["wallnut"] = (x, y, CELL_WIDTH, LANE_HEIGHT)

    # Cherry Bomb
    x, y = 9 * CELL_WIDTH // 2, pool_y + (PLANT_POOL_HEIGHT - LANE_HEIGHT) // 2
    screen.blit(cherry_bomb_image, (x, y))
    pygame.draw.rect(screen, BLACK, (x, y, CELL_WIDTH, LANE_HEIGHT), 2)
    cost_text = font.render(f"{plant_costs['cherry_bomb']}", True, BLACK)
    screen.blit(cost_text, (x + 5, y + LANE_HEIGHT - 20))
    plant_positions["cherry_bomb"] = (x, y, CELL_WIDTH, LANE_HEIGHT)

    # Shovel (no cost required)
    x, y = 11 * CELL_WIDTH // 2, pool_y + (PLANT_POOL_HEIGHT - LANE_HEIGHT) // 2
    screen.blit(shovel_image, (x, y))
    pygame.draw.rect(screen, BLACK, (x, y, CELL_WIDTH, LANE_HEIGHT), 2)
    plant_positions["shovel"] = (x, y, CELL_WIDTH, LANE_HEIGHT)

    return plant_positions


# Waves Configuration
waves = [
    {"Zombie": 10, "Zombie2": 10, "Zombie3": 5},  # Wave 1
    {"Zombie": 10, "Zombie2": 0, "Zombie3": 90},  # Wave 2
    {"Zombie": 20, "Zombie2": 50, "Zombie3": 50},  # Wave 3
    # Add more waves here as needed
]
current_wave = 0
wave_zombies_remaining = sum(waves[current_wave].values())

spawn_timer = 0
SPAWN_INTERVAL = 30  # Spawn a zombie every 1 second (60 FPS)

# Spawn zombies based on wave configuration
def spawn_zombies():
    global wave_zombies_remaining, current_wave, spawn_timer,speed_multiplier
    spawn_timer += 1
    if spawn_timer >= SPAWN_INTERVAL and wave_zombies_remaining > 0:
        zombie_type = random.choices(
            ["Zombie", "Zombie2", "Zombie3"],
            weights=[
                waves[current_wave].get("Zombie", 0),
                waves[current_wave].get("Zombie2", 0),
                waves[current_wave].get("Zombie3", 0),
            ],
            k=1,
        )[0]
        if waves[current_wave][zombie_type] > 0:
            lane = random.randint(0, LANE_COUNT - 1)
            if zombie_type == "Zombie":
                zombies.append(Zombie(lane))
            elif zombie_type == "Zombie2":
                zombies.append(Zombie2(lane))
            elif zombie_type == "Zombie3":
                zombies.append(Zombie3(lane))
            waves[current_wave][zombie_type] -= 1
            wave_zombies_remaining -= 1
            spawn_timer = 0  # Reset timer after spawning

# Update zombie speeds when transitioning waves
def update_zombie_speeds():
    for zombie in zombies:
        zombie.speed = zombie.base_speed * speed_multiplier


# Check wave completion and transition

def check_wave_completion():
    global current_wave, wave_zombies_remaining, speed_multiplier
    if wave_zombies_remaining == 0 and not zombies:
        current_wave += 1
        if current_wave < len(waves):
            wave_zombies_remaining = sum(waves[current_wave].values())
            speed_multiplier += 0.2  # Increase zombie speed by 20% per wave
            update_zombie_speeds()
        else:
            print("You Win!")
            pygame.quit()
            sys.exit()

# Draw wave and zombie information
def draw_wave_info():
    font = pygame.font.Font(None, 36)
    wave_text = font.render(f"Wave: {current_wave + 1}", True, BLACK)
    zombies_text = font.render(f"Zombies Left: {len(zombies) + wave_zombies_remaining}", True, BLACK)
    coins_text = font.render(f"Coins: {coins}", True, BLACK)  # Display coins
    speed_text = font.render(f"Speed Multiplier: {speed_multiplier:.1f}x", True, BLACK)  # Display multiplier
    screen.blit(wave_text, (10, SCREEN_HEIGHT - 80))
    screen.blit(zombies_text, (200, SCREEN_HEIGHT - 80))
    screen.blit(coins_text, (500, SCREEN_HEIGHT - 80))
    screen.blit(speed_text, (700, SCREEN_HEIGHT - 80))


# Main game loop
def main():
    global dragging_plant, dragged_plant_pos, plant_type_dragged, coins

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Start dragging a plant or tool
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                plant_pool_positions = draw_plant_pool()

                # Check which plant/tool is being dragged
                for plant_type, (x, y, w, h) in plant_pool_positions.items():
                    if x <= mx <= x + w and y <= my <= y + h:
                        dragging_plant = True
                        dragged_plant_pos = (mx, my)
                        plant_type_dragged = plant_type

            # Drop the plant/tool onto the grid
            if event.type == pygame.MOUSEBUTTONUP and dragging_plant:
                mx, my = pygame.mouse.get_pos()
                lane = my // LANE_HEIGHT
                col = mx // CELL_WIDTH

                if plant_type_dragged == "shovel":
                    # Remove plant if shovel is used
                    if 0 <= lane < LANE_COUNT and 0 <= col < GRID_COLUMNS and shooter_plants[lane][col]:
                        shooter_plants[lane][col] = None
                elif plant_type_dragged in plant_costs:  # Ensure it's a plant, not a shovel
                    if coins >= plant_costs[plant_type_dragged]:  # Check if player has enough coins
                        if 0 <= lane < LANE_COUNT and 0 <= col < GRID_COLUMNS and not shooter_plants[lane][col]:
                            if plant_type_dragged == "normal_plant":
                                shooter_plants[lane][col] = ShooterPlant(lane, col)
                            elif plant_type_dragged == "freezing_plant":
                                shooter_plants[lane][col] = FreezingPlant(lane, col)
                            elif plant_type_dragged == "repeater":
                                shooter_plants[lane][col] = Repeater(lane, col)
                            elif plant_type_dragged == "wallnut":
                                shooter_plants[lane][col] = Wallnut(lane, col)
                            elif plant_type_dragged == "cherry_bomb":
                                shooter_plants[lane][col] = CherryBomb(lane, col)

                            # Deduct coins
                            coins -= plant_costs[plant_type_dragged]
                    else:
                        font = pygame.font.Font(None, 36)
                        warning_text = font.render("Not enough coins!", True, RED)
                        screen.blit(warning_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 50))

                # Reset dragging state
                dragging_plant = False
                plant_type_dragged = None

        # Draw the game elements
        draw_background()

        # Draw plant pool
        draw_plant_pool()

        # Draw wave, zombie, and coin information
        draw_wave_info()

        # Draw the dragged plant/tool following the mouse cursor
        if dragging_plant:
            mx, my = pygame.mouse.get_pos()
            if plant_type_dragged == "normal_plant":
                screen.blit(plant_image, (mx - CELL_WIDTH // 2, my - LANE_HEIGHT // 2))
            elif plant_type_dragged == "freezing_plant":
                screen.blit(freezing_plant_image, (mx - CELL_WIDTH // 2, my - LANE_HEIGHT // 2))
            elif plant_type_dragged == "repeater":
                screen.blit(repeater_image, (mx - CELL_WIDTH // 2, my - LANE_HEIGHT // 2))
            elif plant_type_dragged == "wallnut":
                screen.blit(wallnut_image, (mx - CELL_WIDTH // 2, my - LANE_HEIGHT // 2))
            elif plant_type_dragged == "cherry_bomb":
                screen.blit(cherry_bomb_image, (mx - CELL_WIDTH // 2, my - LANE_HEIGHT // 2))
            elif plant_type_dragged == "shovel":
                screen.blit(shovel_image, (mx - CELL_WIDTH // 2, my - LANE_HEIGHT // 2))

        # Update and draw shooter plants
        for lane in shooter_plants:
            for plant in lane:
                if plant:
                    plant.auto_shoot()
                    plant.draw()

        # Update and draw bullets
        for bullet in bullets[:]:
            bullet.move()
            bullet.draw()
            if bullet.x > SCREEN_WIDTH:
                bullets.remove(bullet)

        # Update and draw zombies
        for zombie in zombies[:]:
            zombie.detect_plant()  # Check if there's a plant in front
            zombie.move()          # Move or eat plant
            zombie.draw()

            # Check for collisions with bullets
            for bullet in bullets[:]:
                if zombie.x < bullet.x < zombie.x + CELL_WIDTH - 30 and zombie.y < bullet.y < zombie.y + LANE_HEIGHT - 20:
                    if isinstance(bullet, IceBullet):
                        zombie.frozen = True
                        zombie.frozen_timer = 0
                    else:
                        zombie.health -= getattr(bullet, 'damage', 1)  # Default damage is 1
                    bullets.remove(bullet)
                    if zombie.health <= 0:
                        coins += zombie.reward  # Add coins based on zombie reward
                        zombies.remove(zombie)
                        break

        # Spawn new zombies
        spawn_zombies()

        # Check for wave completion
        check_wave_completion()

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
