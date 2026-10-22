import pygame

SPEED = 4


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vel_y = 0
        self.on_ground = False
        self.color = (60, 160, 220)

    def update(self, keys, platforms, width):
        dx = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = SPEED

        if (
            keys[pygame.K_SPACE]
            or keys[pygame.K_w]
            or keys[pygame.K_UP]
        ) and self.on_ground:
            self.vel_y = -13
            self.on_ground = False

        previous_bottom = self.rect.bottom

        self.vel_y = min(self.vel_y + 0.55, 12)

        self.rect.x = max(
            0,
            min(width - self.rect.width, self.rect.x + dx)
        )

        self.rect.y += int(self.vel_y)
        self.on_ground = False

        if self.vel_y > 0:
            for platform in platforms:
                if not platform:
                    continue

                horizontal_overlap = (
                    self.rect.right > platform.left
                    and self.rect.left < platform.right
                )

                crossed_top = (
                    previous_bottom <= platform.top
                    and self.rect.bottom >= platform.top
                )

                if horizontal_overlap and crossed_top:
                    self.rect.bottom = platform.top
                    self.vel_y = 0
                    self.on_ground = True

                    break

    def draw(self, screen, cam_y):
        dr = self.rect.move(0, -int(cam_y))
        pygame.draw.rect(
            screen, self.color, dr, border_radius=6
        )
        pygame.draw.circle(
            screen,
            (255, 220, 180),
            (dr.centerx, dr.top + 8),
            7
        )
