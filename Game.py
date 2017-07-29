import pygame
from Constants import *
from Spritesheet import *
from Enemy import *

class Player():
    def __init__(self):
        self.state = STATE_IDLE
        self.max_power = 100.0
        self.power = self.max_power
        self.drain_per_atk = 30.0
        self.pos = [200, 600]

    def lose_power(self, amt):
        self.power -= amt

    def fire_weapon(self):
        self.lose_power(self.drain_per_atk)

class Game():
    def initialize(self):
        pygame.init()
        pygame.mixer.init()
        self.BPM = 100
        self.player = Player()
        self.disp = Display(self.player)
        self.time = 0.0
        self.clock = pygame.time.Clock()
        self.press_tolerance = 0.08

        self.JUMP_KEY = pygame.K_w
        self.BLK_KEY = pygame.K_s
        self.ATK_KEY = pygame.K_d
        self.CHARGE_KEY = pygame.K_a

        self.enemy_list = self.generate_enemies()

    def run(self):
        is_running = 1
        dif_from_beat_pos = 0
        has_pressed_button = True
        while is_running:
            self.time += 1
            current_enemy = self.enemy_list[0]
            pygame.event.pump()
            self.sec = self.time/self.disp.framerate
            self.disp.screen.fill((0, 0, 0))
            beat_is_occuring = self.is_in_press_window()
            if beat_is_occuring:
                self.disp.screen.fill((100, 10, 10))
            button_pressed = self.det_button_pressed()
            if button_pressed != "False" and self.is_in_press_window():
                self.player.state = button_pressed
                has_pressed_button = True
            last_dif = dif_from_beat_pos
            dif_from_beat_pos = self.sec % (60.0/self.BPM)
            if dif_from_beat_pos > self.press_tolerance and last_dif < self.press_tolerance:
                current_enemy.attack()
                if not has_pressed_button:
                    self.player.state = STATE_IDLE
                has_pressed_button = False
                print(self.time)
            self.disp.tic_enemy(current_enemy, current_enemy.pos, not self.is_time_for_next_frame())
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
        #print(dif_from_beat_pos, dif_from_beat_neg)
        if min([dif_from_beat_pos, dif_from_beat_neg]) < self.press_tolerance:
            return True
        else:
            return False

    def is_time_for_next_frame(self):
        return self.time % int(self.disp.framerate / self.disp.anim_framerate) == 0

    def generate_enemies(self):
        enemy_list = []
        FIST_MAN_SPRITE_SEQ = [Sprite("enemy_idle.png", (200, 200), 2, self.disp.screen, self.player, 400, is_enemy = True),
                                Sprite("enemy_idle.png", (200, 200), 2, self.disp.screen, self.player, 400, is_enemy = True),
                                Sprite("enemy_prep_atk_down.png", (200, 200), 2, self.disp.screen, self.player, 400, is_enemy = True),
                                Sprite("enemy_atk_down.png", (200, 200), 2, self.disp.screen, self.player, 400, is_enemy = True),
                                Sprite("enemy_idle.png", (200, 200), 2, self.disp.screen, self.player, 400, is_enemy = True),
                                Sprite("enemy_idle.png", (200, 200), 2, self.disp.screen, self.player, 400, is_enemy = True),
                                Sprite("enemy_prep_atk_low.png", (200, 200), 2, self.disp.screen, self.player, 400, is_enemy = True),
                                Sprite("enemy_atk_low.png", (200, 200), 2, self.disp.screen, self.player, 400, is_enemy = True)]
        enemy_list.append(Enemy("Fist man", FIST_MAN_SEQ,
            FIST_MAN_SPRITE_SEQ, (200, 400)))
        return enemy_list

class Display():
    def __init__(self, player):
        self.screen = pygame.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])
        self.screen.fill((0, 0, 0))
        pygame.display.set_caption("POWER LEVEL 9000+")
        self.framerate = 20
        self.anim_framerate = 9.0
        self.player = player

        self.idle_sprite = Sprite('PlayerIdle.png', (60, 60), 4, self.screen, self.player, 200)
        self.atk_sprite = Sprite('PlayerShooting.png', (120, 60), 4, self.screen, self.player, 200)
        self.blk_sprite = Sprite('PlayerBlocking.png', (60, 60), 4, self.screen, self.player, 200)
        self.jump_sprite = Sprite('jomp.png', (100, 100), 2, self.screen, self.player, 200)
        self.charge_sprite = Sprite('charge.png', (100, 100), 2, self.screen, self.player, 200)

        self.sprite_dict = {STATE_IDLE: self.idle_sprite,
                            STATE_ATK: self.atk_sprite,
                            STATE_BLK: self.blk_sprite,
                            STATE_JUMP: self.jump_sprite,
                            STATE_CHG: self.charge_sprite}

    def tic_enemy(self, enemy, pos, freeze):
        tic_time = self.framerate/self.anim_framerate
        cur_anim = enemy.sprite_sequence[enemy.state]
        cur_anim.tic(pos, freeze)

    def make_tic(self, player, pos, freeze):
        tic_time = self.framerate/self.anim_framerate
        cur_anim = self.sprite_dict[player.state]
        cur_anim.tic(pos, freeze)

if __name__ == "__main__":
    game = Game()
    game.initialize()
    game.run()
