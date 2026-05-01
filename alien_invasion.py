import pygame
import random


class Ship:
    """A class to manage the player's ship."""

    def __init__(self, screen):
        self.screen = screen
        self.screen_rect = screen.get_rect()
        
        # Ship dimensions and position
        self.width = 60
        self.height = 40
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.midbottom = self.screen_rect.midbottom
        
        # Movement flags
        self.moving_right = False
        self.moving_left = False
        
        # Speed
        self.speed = 5
        
        # Colors: random bi-color
        self.color1 = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.color2 = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def update(self):
        """Update the ship's position based on movement flags."""
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.rect.x += self.speed
        if self.moving_left and self.rect.left > 0:
            self.rect.x -= self.speed

    def draw(self):
        """Draw the ship as a bi-color triangle."""
        # Points for the main triangle
        points1 = [
            (self.rect.centerx, self.rect.top),  # Top
            (self.rect.left, self.rect.bottom),  # Bottom left
            (self.rect.right, self.rect.bottom)  # Bottom right
        ]
        pygame.draw.polygon(self.screen, self.color1, points1)
        
        # Smaller triangle for bi-color effect
        points2 = [
            (self.rect.centerx, self.rect.top + 10),  # Top
            (self.rect.left + 15, self.rect.bottom - 10),  # Bottom left
            (self.rect.right - 15, self.rect.bottom - 10)  # Bottom right
        ]
        pygame.draw.polygon(self.screen, self.color2, points2)


class Bullet:
    """A class to manage bullets fired from the ship."""

    def __init__(self, screen, ship, charge=False):
        self.screen = screen
        self.charge = charge
        width = 8 if charge else 3
        height = 35 if charge else 15
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.midbottom = ship.rect.midtop
        self.color = (255, 200, 0) if charge else (255, 0, 0)
        self.speed = -12 if charge else -10  # Negative to move up
        self.power = 1.02 if charge else 1.0

    def update(self):
        """Move the bullet up the screen."""
        self.rect.y += self.speed

    def draw(self):
        """Draw the bullet."""
        pygame.draw.rect(self.screen, self.color, self.rect)


class AlienBullet:
    """A class to manage bullets fired from aliens."""

    def __init__(self, screen, alien, target_x=None, speed=5):
        self.screen = screen
        self.rect = pygame.Rect(0, 0, 3, 15)
        self.rect.midbottom = alien.rect.midbottom
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.color = (0, 255, 0)  # Green
        self.speed = speed  # Positive to move down

        # Aim roughly toward the player's x position at fire time
        if target_x is not None:
            aim_x = target_x + random.randint(-30, 30)
            delta_x = aim_x - self.rect.centerx
            self.dx = max(min(delta_x * 0.05, 2), -2)
        else:
            self.dx = 0.0

    def update(self):
        """Move the bullet down the screen."""
        self.x += self.dx
        self.y += self.speed
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self):
        """Draw the bullet."""
        pygame.draw.rect(self.screen, self.color, self.rect)


class Alien:
    """A class to manage alien invaders."""

    def __init__(self, x, y, health=1):
        # Size reduced by 15% for a tighter fleet formation
        self.rect = pygame.Rect(x, y, 34, 26)
        self.health = float(health)
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

    def draw(self, screen):
        """Draw the alien as a triangle."""
        points = [
            (self.rect.centerx, self.rect.top),  # Top
            (self.rect.left, self.rect.bottom),  # Bottom left
            (self.rect.right, self.rect.bottom)  # Bottom right
        ]
        pygame.draw.polygon(screen, self.color, points)


def run_game() -> None:
    """Run the main game loop for Alien Invasion."""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Alien Invasion")

    bg_color = (0, 0, 0)
    clock = pygame.time.Clock()
    stars = [
        (random.randint(0, 799), random.randint(0, 599))
        for _ in range(200)
    ]

    # Create ship
    ship = Ship(screen)
    
    # Bullets list
    bullets = []
    alien_bullets = []
    
    # Fire rate: 200ms cooldown
    fire_rate = 200  # milliseconds
    last_shot = 0
    charge_hold_time = 2000  # milliseconds required for a charged beam
    charge_start = None
    charging = False
    charge_effects = []

    # Score and difficulty
    score = 0
    level = 1
    base_alien_fire_chance = 0.00103
    base_alien_health = 1.0
    base_alien_speed = 1.0
    base_alien_drop = 20
    base_alien_bullet_speed = 5

    # Player health
    max_health = 100
    health = max_health

    # Create aliens
    alien_rows = 5
    alien_cols = 10
    alien_spacing_x = 60
    alien_spacing_y = 50

    def get_difficulty_multiplier(current_level):
        return 1.01 ** (current_level - 1)

    def create_aliens(current_level):
        aliens_list = []
        difficulty_multiplier = get_difficulty_multiplier(current_level)
        alien_health = base_alien_health * difficulty_multiplier
        for row in range(alien_rows):
            alien_row = []
            row_offset = (alien_spacing_x // 2) if row % 2 else 0
            for col in range(alien_cols):
                x = 50 + col * alien_spacing_x + row_offset
                y = 50 + row * alien_spacing_y
                alien_row.append(Alien(x, y, health=alien_health))
            aliens_list.append(alien_row)
        return aliens_list

    aliens = create_aliens(level)
    
    # Alien movement
    difficulty_multiplier = get_difficulty_multiplier(level)
    alien_speed = base_alien_speed * difficulty_multiplier
    alien_drop = base_alien_drop * difficulty_multiplier
    alien_direction = 1  # 1 for right, -1 for left

    # Game state
    game_active = True
    game_won = False

    running = True
    while running:
 
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    ship.moving_right = True
                elif event.key == pygame.K_LEFT:
                    ship.moving_left = True
                elif event.key == pygame.K_SPACE:
                    if current_time - last_shot > fire_rate:
                        charging = True
                        charge_start = current_time
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    ship.moving_right = False
                elif event.key == pygame.K_LEFT:
                    ship.moving_left = False
                elif event.key == pygame.K_SPACE:
                    if charging and current_time - last_shot > fire_rate:
                        charged = (current_time - charge_start) >= charge_hold_time
                        bullets.append(Bullet(screen, ship, charge=charged))
                        last_shot = current_time
                    charging = False
                    charge_start = None

        if game_active:
            # Update ship
            ship.update()
            
            # Update bullets
            for bullet in bullets[:]:
                bullet.update()
                if bullet.rect.bottom < 0:
                    bullets.remove(bullet)
            
            # Update alien bullets
            for bullet in alien_bullets[:]:
                bullet.update()
                if bullet.rect.top > screen.get_rect().bottom:
                    alien_bullets.remove(bullet)
                elif bullet.rect.colliderect(ship.rect):
                    health -= 25  # Alien bullet damage
                    alien_bullets.remove(bullet)
                    if health <= 0:
                        game_active = False
            
            # Update aliens
            move_aliens = False
            for row in aliens:
                for alien in row:
                    if alien:
                        alien.rect.x += alien_speed * alien_direction
                        if alien.rect.right >= screen.get_rect().right or alien.rect.left <= 0:
                            move_aliens = True
            
            if move_aliens:
                alien_direction *= -1
                for row in aliens:
                    for alien in row:
                        if alien:
                            alien.rect.y += alien_drop
            
            # Alien shooting: only the lowest alien in each column may fire
            difficulty_multiplier = get_difficulty_multiplier(level)
            alien_fire_chance = base_alien_fire_chance * difficulty_multiplier
            alien_bullet_speed = base_alien_bullet_speed * difficulty_multiplier
            for col_idx in range(alien_cols):
                shooter = None
                for row in reversed(aliens):
                    alien = row[col_idx]
                    if alien:
                        shooter = alien
                        break
                if shooter and random.random() < alien_fire_chance:
                    alien_bullets.append(AlienBullet(screen, shooter, ship.rect.centerx, speed=alien_bullet_speed))
            
            # Check collisions between bullets and aliens
            for bullet in bullets[:]:
                bullet_removed = False
                for row_idx, row in enumerate(aliens):
                    for col_idx, alien in enumerate(row):
                        if alien and bullet.rect.colliderect(alien.rect):
                            hit_x = alien.rect.centerx
                            hit_y = alien.rect.centery
                            alien.health -= bullet.power
                            if alien.health <= 0:
                                row[col_idx] = None
                                score += int(round(10 * (alien_rows - row_idx) * bullet.power))
                                # Add a brief hit flash for charged beam impacts
                                if bullet.charge:
                                    charge_effects.append({
                                        "x": hit_x,
                                        "y": hit_y,
                                        "start": current_time,
                                        "radius": 8,
                                    })
                                # Shift the row left to close gap
                                for i in range(col_idx, len(row) - 1):
                                    row[i] = row[i + 1]
                                    if row[i]:
                                        row[i].rect.x -= alien_spacing_x
                                    row[i + 1] = None
                            else:
                                if bullet.charge:
                                    bullet.y = float(alien.rect.top - bullet.rect.height)
                                    bullet.rect.y = int(bullet.y)
                            if not bullet.charge:
                                bullets.remove(bullet)
                                bullet_removed = True
                            break
                    if bullet_removed:
                        break
                # Charged beams persist and can hit additional aliens as they travel
            
            # Check for game over
            for row in aliens:
                for alien in row:
                    if alien and alien.rect.bottom >= screen.get_rect().bottom:
                        game_active = False
                        break
                if not game_active:
                    break
            
            # Check for level completion
            if all(not any(row) for row in aliens):
                level += 1
                bullets.clear()
                alien_bullets.clear()
                aliens = create_aliens(level)
                difficulty_multiplier = get_difficulty_multiplier(level)
                alien_speed = base_alien_speed * difficulty_multiplier
                alien_drop = base_alien_drop * difficulty_multiplier

        screen.fill(bg_color)

        # Draw stars
        for star in stars:
            color = (
                random.randint(150, 255),
                random.randint(150, 255),
                random.randint(150, 255),
            )
            screen.set_at(star, color)

        # Draw ship
        ship.draw()
        
        # Draw bullets
        for bullet in bullets:
            bullet.draw()
        
        # Draw alien bullets
        for bullet in alien_bullets:
            bullet.draw()
        
        # Draw aliens
        for row in aliens:
            for alien in row:
                if alien:
                    alien.draw(screen)

        # Draw score
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        level_text = font.render(f"Level: {level}", True, (255, 255, 255))
        screen.blit(level_text, (screen.get_rect().right - level_text.get_width() - 10, 10))

        # Draw charge progress bar
        bar_width = 200
        bar_height = 18
        bar_x = screen.get_rect().centerx - bar_width // 2
        bar_y = 60
        pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height))
        if charging and charge_start is not None:
            charge_elapsed = min(current_time - charge_start, charge_hold_time)
            filled = int((charge_elapsed / charge_hold_time) * bar_width)
            pygame.draw.rect(screen, (0, 170, 255), (bar_x, bar_y, filled, bar_height))
            status_text = "Beam Charged!" if charge_elapsed >= charge_hold_time else "Charging..."
            status_color = (0, 255, 255) if charge_elapsed >= charge_hold_time else (255, 255, 0)
        else:
            status_text = "Hold SPACE to charge beam"
            status_color = (180, 180, 180)
        charge_text = font.render(status_text, True, status_color)
        charge_rect = charge_text.get_rect(center=(screen.get_rect().centerx, bar_y + bar_height + 20))
        screen.blit(charge_text, charge_rect)
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

        # Draw charged-hit effects
        for effect in charge_effects[:]:
            elapsed = current_time - effect["start"]
            if elapsed > 300:
                charge_effects.remove(effect)
                continue
            alpha = max(0, 255 - int((elapsed / 300) * 255))
            radius = effect["radius"] + int((elapsed / 300) * 10)
            pygame.draw.circle(screen, (255, 220, 0), (effect["x"], effect["y"]), radius, 2)
        
        # Draw health bar
        bar_width = 200
        bar_height = 20
        pygame.draw.rect(screen, (255, 0, 0), (10, 40, bar_width, bar_height))  # Red background
        health_width = int((health / max_health) * bar_width)
        pygame.draw.rect(screen, (0, 255, 0), (10, 40, health_width, bar_height))  # Green fill
        health_text = font.render(f"HP: {health}", True, (255, 255, 255))
        screen.blit(health_text, (10, 65))

        # Display game over or win
        if not game_active:
            font = pygame.font.SysFont(None, 48)
            if game_won:
                win_text = font.render("You Win!", True, (0, 255, 0))
                score_final = font.render(f"Final Score: {score}", True, (255, 255, 255))
                win_rect = win_text.get_rect(center=(screen.get_rect().centerx, screen.get_rect().centery - 30))
                score_rect = score_final.get_rect(center=(screen.get_rect().centerx, screen.get_rect().centery + 30))
                screen.blit(win_text, win_rect)
                screen.blit(score_final, score_rect)
            else:
                over_text = font.render("Game Over", True, (255, 0, 0))
                score_final = font.render(f"Final Score: {score}", True, (255, 255, 255))
                over_rect = over_text.get_rect(center=(screen.get_rect().centerx, screen.get_rect().centery - 30))
                score_rect = score_final.get_rect(center=(screen.get_rect().centerx, screen.get_rect().centery + 30))
                screen.blit(over_text, over_rect)
                screen.blit(score_final, score_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    run_game()
