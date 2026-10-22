import pygame
import random

PLATFORM_COLOR = (100, 80, 50)
LAVA_COLOR = (220, 60, 20)


def generate_platforms(width, base_y, count=30):
    platforms = [pygame.Rect(0, base_y, width, 20)]
    y = base_y - 110

    for _ in range(count):
        platform_width = random.randint(80, 200)
        x = random.randint(0, width - platform_width)
        platforms.append(pygame.Rect(x, y, platform_width, 16))
        y -= random.randint(80, 130)

    return platforms


def draw_lava(screen, lava_y, cam_y, width, height, frame):
    import math

    lava_screen_y = int(lava_y - cam_y)

    if lava_screen_y < height:
        points = [(0, lava_screen_y)]

        for x in range(0, width + 20, 20):
            wave_y = lava_screen_y + int(
                math.sin(x * 0.08 + frame * 0.1) * 8
            )
            points.append((x, wave_y))

        points.append((width, height))
        points.append((0, height))

        pygame.draw.polygon(screen, LAVA_COLOR, points)

        glow = pygame.Surface((width, 30), pygame.SRCALPHA)

        for i in range(15):
            pygame.draw.line(
                glow,
                (255, 100, 0, max(0, 60 - i * 4)),
                (0, i),
                (width, i),
                1,
            )

        screen.blit(glow, (0, lava_screen_y - 15))
