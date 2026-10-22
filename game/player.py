import pygame

SPEED = 4
GRAVITY = 0.55
JUMP_SPEED = -13
SPRING_SPEED = -19


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vel_y = 0
        self.on_ground = False
        self.color = (60, 160, 220)

    def update(self, keys, platforms, width, spring_platform_ids=None):
        if spring_platform_ids is None:
            spring_platform_ids = set()

        # Horizontal movement
        dx = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -SPEED

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = SPEED

        # Jump
        if (
            keys[pygame.K_SPACE]
            or keys[pygame.K_w]
            or keys[pygame.K_UP]
        ) and self.on_ground:
            self.vel_y = JUMP_SPEED
            self.on_ground = False

        # Remember the previous bottom before falling.
        previous_bottom = self.rect.bottom

        self.vel_y = min(self.vel_y + GRAVITY, 12)

        self.rect.x = max(
            0,
            min(width - self.rect.width, self.rect.x + dx),
        )

        self.rect.y += int(self.vel_y)
        self.on_ground = False

        # One-way platforms: land only while descending.
        if self.vel_y >= 0:
            for platform in platforms:
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

                    # Spring platforms launch the player higher.
                    if id(platform) in spring_platform_ids:
                        self.vel_y = SPRING_SPEED
                        self.on_ground = False
                    else:
                        self.vel_y = 0
                        self.on_ground = True

                    break

    def draw(self, screen, cam_y):
        dr = self.rect.move(0, -int(cam_y))

        pygame.draw.rect(
            screen,
            self.color,
            dr,
            border_radius=6,
        )

        pygame.draw.circle(
            screen,
            (255, 220, 180),
            (dr.centerx, dr.top + 8),
            7,
        )
