import math
import random
import pygame

from game.player import Player
from game.world import generate_platforms, draw_lava, PLATFORM_COLOR

WIDTH, HEIGHT = 500, 640
FPS = 60
BG = (20, 15, 30)
GROUND_Y = HEIGHT + 200


class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Lava Escape")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 24, bold=True)
        self.big_font = pygame.font.SysFont("monospace", 42, bold=True)
        self.reset()

    def reset(self):
        self.platforms = generate_platforms(WIDTH, GROUND_Y)
        self.player = Player(WIDTH // 2 - 16, GROUND_Y - 50)
        self.cam_y = 0
        self.lava_y = GROUND_Y + 60
        self.lava_rise = 0.4
        self.surge_timer = 0
        self.surge_duration = 180
        self.surge_interval = 600
        self.surge_active = False
        self.score = 0
        self.game_over = False
        self.won = False
        self.top_y = self.platforms[-1].y
        self.frame = 0
        self.crumble_timers = {}

        candidates = self.platforms[1:]
        springs = random.sample(candidates, min(4, len(candidates)))
        self.spring_platform_ids = {id(p) for p in springs}

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
        return True

    def update(self):
        if self.game_over or self.won:
            return

        keys = pygame.key.get_pressed()
        self.player.update(
            keys, self.platforms, WIDTH, self.spring_platform_ids
        )

        if self.player.on_ground:
            for platform in self.platforms:
                if (
                    self.player.rect.bottom == platform.top
                    and self.player.rect.right > platform.left
                    and self.player.rect.left < platform.right
                ):
                    platform_id = id(platform)

                    if (
                        platform.top != GROUND_Y
                        and platform_id not in self.spring_platform_ids
                        and platform_id not in self.crumble_timers
                        and random.random() < 0.25
                    ):
                        self.crumble_timers[platform_id] = 0
                    break

        for platform in self.platforms[1:]:
            platform_id = id(platform)
            if platform_id in self.crumble_timers:
                self.crumble_timers[platform_id] += 1
                if self.crumble_timers[platform_id] >= 45:
                    self.platforms.remove(platform)
                    del self.crumble_timers[platform_id]
                    break

        target = self.player.rect.centery - HEIGHT // 2
        if target < self.cam_y:
            self.cam_y = target

                # Trigger a lava surge periodically.
        self.surge_timer += 1

        if self.surge_timer >= self.surge_interval:
            self.surge_timer = 0
            self.surge_active = True

        if self.surge_active:
            self.lava_y -= self.lava_rise * 2.5
            self.surge_duration -= 1

            if self.surge_duration <= 0:
                self.surge_active = False
                self.surge_duration = 180
                self.surge_interval = random.randint(480, 720)
        else:
            self.lava_y -= self.lava_rise

        self.lava_rise = min(1.2, self.lava_rise + 0.0003)
        self.score = max(0, (GROUND_Y - self.player.rect.y) // 10)
        self.frame += 1

        if self.player.rect.bottom >= self.lava_y:
            self.game_over = True

        if self.player.rect.top <= self.top_y - 20:
            self.won = True

    def draw(self):
        self.screen.fill(BG)

        for platform in self.platforms:
            platform_id = id(platform)
            offset_x = 0

            if platform_id in self.crumble_timers:
                offset_x = int(math.sin(self.frame * 2) * 3)

            rect = platform.move(offset_x, -int(self.cam_y))
            color = PLATFORM_COLOR

            if platform_id in self.spring_platform_ids:
                color = (50, 220, 120)
            elif platform_id in self.crumble_timers:
                color = (220, 170, 60)

            pygame.draw.rect(self.screen, color, rect, border_radius=4)

        self.player.draw(self.screen, self.cam_y)
        draw_lava(
            self.screen, self.lava_y, self.cam_y, WIDTH, HEIGHT, self.frame
        )

        label = self.font.render(
            f"Height: {self.score}m  R=Restart", True, (220, 200, 180)
        )
        self.screen.blit(label, (8, 10))
        # Danger meter based on the lava's distance from the player.
        distance = self.player.rect.bottom - self.lava_y
        danger = max(0, min(100, int(100 - distance / 5)))

        meter_x, meter_y = 10, 45
        meter_width, meter_height = 200, 18

        pygame.draw.rect(
            self.screen, (70, 70, 70),
            (meter_x, meter_y, meter_width, meter_height)
        )

        pygame.draw.rect(
            self.screen, (230, 50, 30),
            (meter_x, meter_y, meter_width * danger // 100, meter_height)
        )

        danger_label = self.font.render(
            f"DANGER: {danger}%", True, (255, 255, 255)
        )
        self.screen.blit(danger_label, (220, 40))

        if self.surge_active:
            surge_label = self.font.render(
                "LAVA SURGE!", True, (255, 80, 40)
            )
            self.screen.blit(surge_label, (10, 75))

        if self.game_over:
            self._msg("LAVA GOT YOU!", (220, 80, 40))
        if self.won:
            self._msg("ESCAPED!", (80, 220, 100))

        pygame.display.flip()

    def _msg(self, text, color):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        message = self.big_font.render(text, True, color)
        subtitle = self.font.render(
            "Press R to Play Again", True, (200, 200, 200)
        )

        self.screen.blit(
            message,
            (WIDTH // 2 - message.get_width() // 2, HEIGHT // 2 - 40),
        )
        self.screen.blit(
            subtitle,
            (WIDTH // 2 - subtitle.get_width() // 2, HEIGHT // 2 + 20),
        )

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
