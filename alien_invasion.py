import pygame
import random


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

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(bg_color)

        for star in stars:
            color = (
                random.randint(150, 255),
                random.randint(150, 255),
                random.randint(150, 255),
            )
            screen.set_at(star, color)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    run_game()
