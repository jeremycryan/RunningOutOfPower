import pygame
import math
from Constants import *
from Spritesheet import *
from Enemy import *

class Player():
    def __init__(self):
        self.state = STATE_IDLE
        self.anim = STATE_IDLE
        self.max_power = 250.0
        self.power = self.max_power
        self.drain_per_atk = 75.0
        self.pos = [490, 450]
        self.weapon_damage = 100

    def lose_power(self, amt):
        self.power = max(self.power - amt, 0)

    def fire_weapon(self):
        self.lose_power(self.drain_per_atk)

    def take_damage(self, amt):
        self.lose_power(amt)

class Game():
    def initialize(self):
        pygame.init()
        pygame.mixer.init()

        self.gun_sound = pygame.mixer.Sound('LaserSound.wav')
        self.block_sound = pygame.mixer.Sound('Blocked.wav')
        self.failed_gun_sound = pygame.mixer.Sound('FailLaser.wav')
        self.damage_sound = pygame.mixer.Sound('Hurt.wav')
        self.dodge_sound = pygame.mixer.Sound('Dodge.wav')
        self.recharge_sound = pygame.mixer.Sound('Charge.wav')
        self.enemy_defeat_sound = pygame.mixer.Sound('EnemyDefeat.wav')

        self.BPM = 100
        self.player = Player()
        self.disp = Display(self.player)
        self.time = 0.0
        self.clock = pygame.time.Clock()
        self.press_tolerance = 0.125

        self.JUMP_KEY = pygame.K_w
        self.BLK_KEY = pygame.K_s
        self.ATK_KEY = pygame.K_d
        self.CHARGE_KEY = pygame.K_a

        self.enemy_list = self.generate_enemies()

        pygame.mixer.music.load(os.path.join('LD39.wav'))
        pygame.mixer.music.play(-1)

    def run(self):
        is_running = 1
        dif_from_beat_pos = 0
        has_pressed_button = True
        time_of_press = 0
        self.time_ms = 550
        while is_running and len(self.enemy_list):
            self.time += 1
            current_enemy = self.enemy_list[0]
            pygame.event.pump()
            self.sec = self.time/self.disp.framerate
            beat_length = 60.0/self.BPM
            time_since_beat = self.time_ms/1000.0 % beat_length
            if time_since_beat == self.time_ms/1000.0 % (beat_length * 2):
                self.disp.screen.blit(self.disp.backdrop, (0, 0))
            else:
                self.disp.screen.blit(self.disp.backdrop_lit, (0, 0))
            button_pressed = self.det_button_pressed()
            if button_pressed != "False" and self.is_in_press_window() and not has_pressed_button:
                self.player.state = button_pressed
                self.player.anim = button_pressed
                self.disp.sprite_dict[self.player.anim].curr_frame = 1
                has_pressed_button = True
                if self.time_ms/1000.0 - time_of_press > 2 * self.press_tolerance:
                    time_of_press = self.time_ms / 1000.0
            last_dif = dif_from_beat_pos
            dif_from_beat_pos = (self.time_ms / 1000.0) % (60.0/self.BPM)
            time_since_press = (self.time_ms/1000.0 - time_of_press)
            self.disp.energy_bar_y_offset = math.sin(time_since_beat * 40) / ((time_since_beat + 0.37) ** 2)
            if self.player.state == STATE_JUMP:
                prop = time_since_press / (1.0/self.BPM * 60.0) * 4.0
                try:
                    if prop < 0.5:
                        jump_offset = prop ** 0.3 * 180
                    else:
                        jump_offset = (1 - prop) ** 0.3 * 180
                except:
                    jump_offset = 0
                if jump_offset < 0:
                    jump_offset = 0
            else:
                jump_offset = 0
            if dif_from_beat_pos >= self.press_tolerance and last_dif < self.press_tolerance:
                current_enemy.attack()
                self.player.power = max(self.player.power - 5, 0)
                if not has_pressed_button:
                    self.player.state = STATE_IDLE
                    self.player.anim = STATE_IDLE
                if self.player.state == STATE_BLK and current_enemy.attack_sequence[current_enemy.state] == ENM_TOP_ATK:
                    self.disp.make_blip("Blocked", (self.player.pos[0] + 160, self.player.pos[1] + 40), 7)
                    self.block_sound.play()
                if self.player.state == STATE_CHG and not current_enemy.invulnerable:
                    self.disp.make_blip("Recharge", (self.player.pos[0] + 140, self.player.pos[1] + 40), 7)
                    self.player.power = min(self.player.power + 45 - 25 * self.player.power/self.player.max_power, self.player.max_power)
                    self.recharge_sound.play()
                if self.player.state == STATE_JUMP and current_enemy.attack_sequence[current_enemy.state] == ENM_BOT_ATK:
                    self.disp.make_blip("Dodged", (self.player.pos[0] + 160, self.player.pos[1] + 40), 7)
                    self.dodge_sound.play()
                if (current_enemy.attack_sequence[current_enemy.state] == ENM_BOT_ATK and self.player.state != STATE_JUMP) or \
                        (current_enemy.attack_sequence[current_enemy.state] == ENM_TOP_ATK and self.player.state != STATE_BLK):
                    self.player.take_damage(current_enemy.damage)
                    self.disp.make_blip("Damage", (self.player.pos[0] + 70, self.player.pos[1] + 70), 7)
                    self.player.state = STATE_DAMAGED
                    self.player.anim = STATE_DAMAGED
                    self.damage_sound.play()
                if not current_enemy.invulnerable and self.player.state == STATE_ATK:
                    self.player.fire_weapon()
                    current_enemy.health = max(0, current_enemy.health - self.player.weapon_damage)
                    self.gun_sound.play()
                    print(current_enemy.health)
                if self.player.state == STATE_FAIL_ATK:
                    self.failed_gun_sound.play()
                self.player.anim = self.player.state
                has_pressed_button = False

            if current_enemy.health == 0:
                self.enemy_list.remove(current_enemy)
                self.player.power = self.player.max_power
                self.disp.make_blip("Recharge", (self.player.pos[0] + 140, self.player.pos[1] + 40), 7)
                self.disp.make_blip("Next opponent", (self.player.pos[0] - 20, self.player.pos[1] - 160), 7)
                self.enemy_defeat_sound.play()

            self.disp.render_instructions(current_enemy)
            self.disp.render_enemy_hp(current_enemy.health/current_enemy.max_health, current_enemy)
            self.disp.tic_enemy(current_enemy, current_enemy.pos, not self.is_time_for_next_frame())
            self.disp.render_energy_bar(self.player.power/self.player.max_power)
            self.disp.make_tic(self.player, [self.player.pos[0], self.player.pos[1] - jump_offset], not self.is_time_for_next_frame())
            self.disp.render_blips(not self.is_time_for_next_frame())
            time_diff = self.clock.tick(self.disp.framerate)
            self.time_ms += time_diff
            #self.disp.screen = pygame.transform.scale(self.disp.screen, (int(WINDOW_WIDTH * self.disp.zoom), int(WINDOW_HEIGHT * self.disp.zoom)))
            self.disp.screen_commit.blit(self.disp.screen, (0, 0))
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
            if self.player.power > self.player.drain_per_atk + 10:
                return STATE_ATK
            else:
                return STATE_FAIL_ATK
        elif block_pressed:
            return STATE_BLK
        elif charge_pressed:
            return STATE_CHG
        else:
            return "False"

    def is_in_press_window(self):
        dif_from_beat_pos = (self.time_ms / 1000.0) % (60.0/self.BPM)
        dif_from_beat_neg = 60.0/self.BPM - (self.time_ms / 1000.0) % (60.0/self.BPM)
        if min([dif_from_beat_pos, dif_from_beat_neg]) < self.press_tolerance:
            return True
        else:
            return False

    def is_time_for_next_frame(self):
        return self.time % int(self.disp.framerate / self.disp.anim_framerate) == 0

    def generate_enemies(self):
        enemy_list = []
        FREDERICK_SPRITE_SEQ = [Sprite("FrederickIdle.png", (60, 60), 4, self.disp.screen, self.player, 200, is_enemy = True)]
        FIST_MAN_SPRITE_SEQ = [Sprite("FistmanIdle.png", (180, 120), 4, self.disp.screen, self.player, 400, is_enemy = True),
                                Sprite("FistmanIdle.png", (180, 120), 4, self.disp.screen, self.player, 400, is_enemy = True),
                                Sprite("FistmanTopAttackPrep.png", (180, 120), 4, self.disp.screen, self.player, 400, is_enemy = True),
                                Sprite("FistmanTopAttack.png", (180, 120), 17, self.disp.screen, self.player, 400, is_enemy = True),
                                Sprite("FistmanIdle.png", (180, 120), 4, self.disp.screen, self.player, 400, is_enemy = True),
                                Sprite("FistmanIdle.png", (180, 120), 4, self.disp.screen, self.player, 400, is_enemy = True),
                                Sprite("FistmanBotPrep.png", (180, 120), 4, self.disp.screen, self.player, 400, is_enemy = True),
                                Sprite("FistmanBotAtk.png", (180, 120), 16, self.disp.screen, self.player, 400, is_enemy = True)]
        PURPLE_FIST_MAN_SPRITE_SEQ = [Sprite("PurpleFistmanTopAttackPrep.png", (180, 120), 4, self.disp.screen, self.player, 400, is_enemy = True),
                                Sprite("PurpleFistmanTopAttack.png", (180, 120), 17, self.disp.screen, self.player, 400, is_enemy = True),
                                Sprite("PurpleFistmanBotPrep.png", (180, 120), 4, self.disp.screen, self.player, 400, is_enemy = True),
                                Sprite("PurpleFistmanBotAtk.png", (180, 120), 16, self.disp.screen, self.player, 400, is_enemy = True),
                                Sprite("PurpleFistmanIdle.png", (180, 120), 4, self.disp.screen, self.player, 400, is_enemy = True),
                                Sprite("PurpleFistmanBotPrep.png", (180, 120), 4, self.disp.screen, self.player, 400, is_enemy = True),
                                Sprite("PurpleFistmanBotAtk.png", (180, 120), 16, self.disp.screen, self.player, 400, is_enemy = True),
                                Sprite("PurpleFistmanIdle.png", (180, 120), 4, self.disp.screen, self.player, 400, is_enemy = True)]
        HYDRA_SPRITE_SEQ = [Sprite("HydraIdle.png", (180, 120), 4, self.disp.screen, self.player, 400, is_enemy = True),
                            Sprite("HydraTopPrep.png", (180, 120), 4, self.disp.screen, self.player, 400, is_enemy = True),
                            Sprite("HydraTopAtk.png", (180, 120), 15, self.disp.screen, self.player, 400, is_enemy = True)]
        enemy_list.append(Enemy("Frederick", FREDERICK_SEQ,
            FREDERICK_SPRITE_SEQ, (860, 450), 100, 300.0))
        enemy_list.append(Enemy("Hydra", HYDRA_SEQ, HYDRA_SPRITE_SEQ, (520, 258), 60, 500.0))
        enemy_list.append(Enemy("Fist man", FIST_MAN_SEQ,
            FIST_MAN_SPRITE_SEQ, (460, 250), 100, 500.0))
        enemy_list.append(Enemy("Purple fist man", PURPLE_FIST_MAN_SEQ,
            PURPLE_FIST_MAN_SPRITE_SEQ, (460, 250), 100, 800.0))
        return enemy_list

class Display():
    def __init__(self, player):
        self.screen = pygame.Surface([WINDOW_WIDTH, WINDOW_HEIGHT])
        self.screen_commit = pygame.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])
        self.loading_screen = pygame.image.load(os.path.join('LoadingScreen.png'))
        self.loading_screen = pygame.transform.scale(self.loading_screen, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.screen_commit.blit(self.loading_screen, (0, 0))
        pygame.display.flip()
        pygame.display.set_caption("POWER LEVEL 9000+")
        self.framerate = 30.0
        self.anim_framerate = 12.0
        self.player = player
        self.energy_bar_y_offset = 0
        self.zoom = 1.0

        self.idle_sprite = Sprite('PlayerIdle.png', (60, 60), 4, self.screen, self.player, 200)
        self.atk_sprite = Sprite('PlayerShootingLaserShortened.png', (180, 60), 6, self.screen, self.player, 200)
        self.failed_atk_sprite = Sprite('PlayerShooting.png', (120, 60), 4, self.screen, self.player, 200)
        self.blk_sprite = Sprite('PlayerBlockingExtended.png', (60, 60), 6, self.screen, self.player, 200)
        self.jump_sprite = Sprite('PlayerJumpStationary.png', (60, 120), 4, self.screen, self.player, 200)
        self.charge_sprite = Sprite('PlayerRecharge.png', (60, 60), 4, self.screen, self.player, 200)
        self.damaged_sprite = Sprite('PlayerDamaged.png', (60, 60), 6, self.screen, self.player, 200)

        self.blips = []
        self.blocked_blip = Sprite('Blocked.png', (120, 60), 7, self.screen, self.player, 75)
        self.dodged_blip = Sprite('Dodged.png', (120, 60), 7, self.screen, self.player, 75)
        self.recharge_blip = Sprite('+Energy.png', (160, 60), 7, self.screen, self.player, 75)
        self.damage_blip = Sprite('-100HP.png', (120, 60), 7, self.screen, self.player, 75)
        self.next_opponent_blip = Sprite('NextOpponent.png', (120, 60), 7, self.screen, self.player, 125)


        self.energy_bar = pygame.image.load(os.path.join('EnergyBar.png')).convert_alpha()
        self.energy_meter = pygame.image.load(os.path.join('EnergyMeter.png')).convert_alpha()
        self.backdrop = pygame.image.load(os.path.join("Backdropv1.png"))
        self.backdrop_lit = pygame.image.load(os.path.join("Backdropv2.png"))
        self.backdrop = pygame.transform.scale(self.backdrop, (1600, 900))
        self.backdrop_lit = pygame.transform.scale(self.backdrop_lit, (1600, 900))
        self.vis_energy_percent = 1.0
        self.vis_hp_percent = 1.0

        self.instructions_box = pygame.image.load(os.path.join('InstructionsBox.png')).convert_alpha()
        change_alpha(self.instructions_box, 40, False)
        self.instructions_1 = pygame.image.load(os.path.join('Instructions1.png')).convert_alpha()
        self.instructions_2 = pygame.image.load(os.path.join('Instructions2.png')).convert_alpha()
        self.instructions_3 = pygame.image.load(os.path.join('Instructions3.png')).convert_alpha()
        self.instructions_box = pygame.transform.scale(self.instructions_box, (997, 347))
        self.instructions_1 = pygame.transform.scale(self.instructions_1, (997, 347))
        self.instructions_2 = pygame.transform.scale(self.instructions_2, (997, 347))
        self.instructions_3 = pygame.transform.scale(self.instructions_3, (997, 347))

        self.enemy_cur_anim = self.idle_sprite

        self.sprite_dict = {STATE_IDLE: self.idle_sprite,
                            STATE_ATK: self.atk_sprite,
                            STATE_FAIL_ATK: self.failed_atk_sprite,
                            STATE_BLK: self.blk_sprite,
                            STATE_JUMP: self.jump_sprite,
                            STATE_CHG: self.charge_sprite,
                            STATE_DAMAGED: self.damaged_sprite}

        self.blip_dict = {"Blocked": self.blocked_blip,
                        "Dodged": self.dodged_blip,
                        "Recharge": self.recharge_blip,
                        "Damage": self.damage_blip,
                        "Next opponent": self.next_opponent_blip}

    def render_energy_bar(self, energy_percent):
        dif = energy_percent - self.vis_energy_percent
        self.vis_energy_percent += 0.15 * dif
        pos = (self.player.pos[0] - 0, self.player.pos[1] - 20 - self.energy_bar_y_offset)
        surface = pygame.Surface((9, 24)).convert_alpha()
        bar_surface = pygame.Surface((3, int(18.0 * self.vis_energy_percent))).convert_alpha()
        if self.vis_energy_percent > 0.5:
            bar_surface.fill((133, 176, 229))
        elif self.vis_energy_percent > 0.2:
            bar_surface.fill((219, 229, 133))
        else:
            bar_surface.fill((239, 124, 124))
        surface.blit(self.energy_meter, (0, 0))
        surface.blit(bar_surface, (3, 3 + (18 - int(18.0 * self.vis_energy_percent))))
        surface = pygame.transform.scale(surface, (36, 96))
        self.screen.blit(surface, pos)

    def render_instructions(self, current_enemy):
        pos = (280, 47)
        if current_enemy.name == "Frederick":
            self.screen.blit(self.instructions_box, pos)
            self.screen.blit(self.instructions_1, pos)
        elif current_enemy.name == "Hydra":
            self.screen.blit(self.instructions_box, pos)
            self.screen.blit(self.instructions_2, pos)
        elif current_enemy.name == "Fist man":
            self.screen.blit(self.instructions_box, pos)
            self.screen.blit(self.instructions_3, pos)

    def render_enemy_hp(self, hp_percent, enemy):
        dif = hp_percent - self.vis_hp_percent
        self.vis_hp_percent += 0.15 * dif
        if enemy.name == "Frederick":
            pos = (enemy.pos[0] + 160, enemy.pos[1] - 30 - self.energy_bar_y_offset)
        elif enemy.name == "Hydra":
            pos = (enemy.pos[0] + 460, enemy.pos[1] + 95 - self.energy_bar_y_offset)
        else:
            pos = (enemy.pos[0] + 530, enemy.pos[1] + 70 - self.energy_bar_y_offset)
        surface = pygame.Surface((9, 24)).convert_alpha()
        bar_surface = pygame.Surface((3, int(18.0 * self.vis_hp_percent))).convert_alpha()
        if self.vis_hp_percent > 0.5:
            bar_surface.fill((133, 229, 176))
        elif self.vis_hp_percent > 0.2:
            bar_surface.fill((219, 229, 133))
        else:
            bar_surface.fill((239, 124, 124))
        surface.blit(self.energy_meter, (0, 0))
        surface.blit(bar_surface, (3, 3 + (18 - int(18.0 * self.vis_hp_percent))))
        surface = pygame.transform.scale(surface, (36, 96))
        self.screen.blit(surface, pos)

    def render_blips(self, halt):
        for blip in self.blips:
            blip.tic(halt)
            if blip.duration <= 0:
                self.blips.remove(blip)

    def make_blip(self, blip_type, pos, duration):
        self.blips.append(Blip(self.blip_dict[blip_type], pos, duration))

    def tic_enemy(self, enemy, pos, freeze):
        tic_time = self.framerate/self.anim_framerate
        if self.enemy_cur_anim != enemy.sprite_sequence[enemy.state]:
            self.enemy_cur_anim = enemy.sprite_sequence[enemy.state]
            self.enemy_cur_anim.curr_frame = 1
        self.enemy_cur_anim.tic(pos, freeze, enemy)

    def make_tic(self, player, pos, freeze):
        tic_time = self.framerate/self.anim_framerate
        cur_anim = self.sprite_dict[player.anim]
        cur_anim.tic(pos, freeze)
        #for key in self.sprite_dict:
        #    if self.sprite_dict[key] != cur_anim:
        #        self.sprite_dict[key].curr_frame = 1

def change_alpha(img, alpha=255, redden = True): #   change opacity of img to alpha
    width,height=img.get_size()
    for x in range(0,width):
        for y in range(0,height):
            r,g,b,old_alpha=img.get_at((x,y))
            if redden:
                prop = (1 - (alpha + 100)/600.0)
                g, b = prop*g, prop*b
            img.set_at((x,y),(r,g,b,alpha/255.0*float(old_alpha)))

if __name__ == "__main__":
    game = Game()
    game.initialize()
    game.run()
