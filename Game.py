import pygame
from Constants import *
from Spritesheet import *

class Player():
    def __init__(self):
        self.state = STATE_IDLE
        self.max_power = 100.0
        self.power = self.max_power
        self.drain_per_atk = 30.0
        self.pos = [200, 200]

    def lose_power(self, amt):
        self.power -= amt

    def fire_weapon(self):
        self.lose_power(self.drain_per_atk)


class Game():
    def initialize(self):
        pygame.init()
        pygame.mixer.init()
        self.BPM = 100.0
        self.player = Player()
        self.disp = Display(self.player)
        self.time = 0.0
        self.clock = pygame.time.Clock()
        self.press_tolerance = 0.10

        self.JUMP_KEY = pygame.K_w
        self.BLK_KEY = pygame.K_s
        self.ATK_KEY = pygame.K_d
        self.CHARGE_KEY = pygame.K_a

    def run(self):
        is_running = 1
        while is_running:
            self.time += 1
            pygame.event.pump()
            self.sec = self.time/self.disp.framerate
            self.disp.screen.fill((0, 0, 0))
            if self.is_in_press_window():
                self.disp.screen.fill((100, 10, 10))
            button_pressed = self.det_button_pressed()
            if button_pressed != "False":
                self.player.state = button_pressed
            self.disp.make_tic(self.player, self.player.pos, not self.is_time_for_next_frame())
            self.clock.tick(self.disp.framerate)
            pygame.display.flip()

    def det_button_pressed(self):
        pressed = pygame.key.get_pressed()
        jump_pressed = pressed[self.JUMP_KEY]
        atk_pressed = pressed[self.ATK_KEY]
        block_pressed = pressed[self.BLK_KEY]
        charge_pressed = pressed[self.CHARGE_KEY]
        if jump_pressed:
            return STATE_JUMP
        elif atk_pressed:
            return STATE_ATK
        elif block_pressed:
            return STATE_BLK
        elif charge_pressed:
            return STATE_CHG
        else:
            return "False"

    def is_in_press_window(self):
        dif_from_beat_pos = self.sec % (60.0/self.BPM)
        dif_from_beat_neg = 60.0/self.BPM - dif_from_beat_pos
        print(dif_from_beat_pos, dif_from_beat_neg)
        if min([dif_from_beat_pos, dif_from_beat_neg]) < self.press_tolerance:
            return True
        else:
            return False

    def is_time_for_next_frame(self):
        return self.time % int(self.disp.framerate / self.disp.anim_framerate) == 0

class Display():
    def __init__(self, player):
        self.screen = pygame.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])
        self.screen.fill((0, 0, 0))
        pygame.display.set_caption("POWER LEVEL 9000+")
        self.framerate = 50.0
        self.anim_framerate = 4.0
        self.player = player

        self.idle_sprite = Sprite('idle.png', (100, 100), 2, self.screen, self.player, 100)
        self.atk_sprite = Sprite('atk.png', (100, 100), 2, self.screen, self.player, 100)
        self.blk_sprite = Sprite('block.png', (100, 100), 2, self.screen, self.player, 100)
        self.jump_sprite = Sprite('jomp.png', (100, 100), 2, self.screen, self.player, 100)
        self.charge_sprite = Sprite('charge.png', (100, 100), 2, self.screen, self.player, 100)

        self.sprite_dict = {STATE_IDLE: self.idle_sprite,
                            STATE_ATK: self.atk_sprite,
                            STATE_BLK: self.blk_sprite,
                            STATE_JUMP: self.jump_sprite,
                            STATE_CHG: self.charge_sprite}

    def make_tic(self, player, pos, freeze):
        tic_time = self.framerate/self.anim_framerate
        cur_anim = self.sprite_dict[player.state]
        cur_anim.tic(pos, freeze)

if __name__ == "__main__":
    game = Game()
    game.initialize()
    game.run()
