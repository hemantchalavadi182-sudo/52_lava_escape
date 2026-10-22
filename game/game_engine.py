import pygame
from game.player import Player
from game.world import generate_platforms, draw_lava, PLATFORM_COLOR

WIDTH,HEIGHT=500,640
FPS=60
BG=(20,15,30)
GROUND_Y=HEIGHT+200

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen=pygame.display.set_mode((WIDTH,HEIGHT))
        pygame.display.set_caption("Lava Escape")
        self.clock=pygame.time.Clock()
        self.font=pygame.font.SysFont("monospace",24,bold=True)
        self.big_font=pygame.font.SysFont("monospace",42,bold=True)
        self.reset()

    def reset(self):
        self.platforms=generate_platforms(WIDTH,GROUND_Y)
        self.player=Player(WIDTH//2-16,GROUND_Y-50)
        self.cam_y=0
        self.lava_y=GROUND_Y+60
        self.lava_rise=0.4
        self.score=0
        self.game_over=False
        self.won=False
        self.top_y=self.platforms[-1].y
        self.frame=0
        self.crumble_timers = {}
        

    def handle_events(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT: return False
            if event.type==pygame.KEYDOWN and event.key==pygame.K_r: self.reset()
        return True

    def update(self):
        if self.game_over or self.won: return
        keys=pygame.key.get_pressed()
        self.player.update(keys, self.platforms, WIDTH)

        # Detect which platform the player has landed on.
        if self.player.on_ground:
            for platform in self.platforms:
                if (
                    self.player.rect.bottom == platform.top
                    and self.player.rect.right > platform.left
                    and self.player.rect.left < platform.right
                ):
                    # The ground never crumbles.
                    if platform.top != GROUND_Y:
                        platform_id = id(platform)

                        # Only some platforms crumble.
                        if platform_id not in self.crumble_timers:
                            import random
                            if random.random() < 0.25:
                                self.crumble_timers[platform_id] = 0
                    break

        # Advance timers and remove platforms after 45 frames.
        for platform in self.platforms[1:]:
            platform_id = id(platform)

            if platform_id in self.crumble_timers:
                self.crumble_timers[platform_id] += 1

                if self.crumble_timers[platform_id] >= 45:
                    self.platforms.remove(platform)
                    del self.crumble_timers[platform_id]
                    break
        target=self.player.rect.centery-HEIGHT//2
        if target<self.cam_y: self.cam_y=target
        self.lava_y-=self.lava_rise
        self.lava_rise=min(1.2,self.lava_rise+0.0003)
        self.score=max(0,(GROUND_Y-self.player.rect.y)//10)
        self.frame+=1
        if self.player.rect.bottom>=self.lava_y:
            self.game_over=True
        if self.player.rect.top<=self.top_y-20:
            self.won=True

    def draw(self):
        self.screen.fill(BG)
        for p in self.platforms:
            offset_x = 0
            platform_id = id(p)

            if platform_id in self.crumble_timers:
                import math
                offset_x = int(math.sin(self.frame * 2) * 3)

            dr = p.move(offset_x, -int(self.cam_y))

            color = PLATFORM_COLOR
            if platform_id in self.crumble_timers:
                color = (220, 170, 60)

            pygame.draw.rect(
                self.screen,
                color,
                dr,
                border_radius=4,
            )
        self.player.draw(self.screen,self.cam_y)
        draw_lava(self.screen,self.lava_y,self.cam_y,WIDTH,HEIGHT,self.frame)
        sc=self.font.render(f"Height: {self.score}m  R=Restart",True,(220,200,180))
        self.screen.blit(sc,(8,10))
        if self.game_over:
            self._msg("LAVA GOT YOU!",(220,80,40))
        if self.won:
            self._msg("ESCAPED!",(80,220,100))
        pygame.display.flip()

    def _msg(self,text,color):
        ov=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        ov.fill((0,0,0,150))
        self.screen.blit(ov,(0,0))
        m=self.big_font.render(text,True,color)
        s=self.font.render("Press R to Play Again",True,(200,200,200))
        self.screen.blit(m,(WIDTH//2-m.get_width()//2,HEIGHT//2-40))
        self.screen.blit(s,(WIDTH//2-s.get_width()//2,HEIGHT//2+20))

    def run(self):
        running=True
        while running:
            running=self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
