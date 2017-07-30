from Constants import *

class Enemy():
    def __init__(self, name, attack_sequence, sprite_sequence, pos, damage, max_health):
        self.name = name
        self.attack_sequence = attack_sequence
        self.sprite_sequence = sprite_sequence
        self.state = 0
        if self.name == "Purple fist man":
            self.state = 4
        self.invulnerable = False
        self.pos = pos
        self.damage = damage
        self.max_health = max_health
        self.health = max_health

    def attack(self):
        self.state += 1
        if self.state == len(self.attack_sequence):
            self.state = 0
        if self.attack_sequence[self.state] in [ENM_BOT_ATK, ENM_TOP_ATK]:
            self.invulnerable = True
        else:
            self.invulnerable = False

class Blip():
    def __init__(self, sprite, pos, starting_duration):
        self.sprite = sprite
        self.pos = pos
        self.duration = starting_duration

    def tic(self, halt = False):
        self.sprite.tic(self.pos, halt)
        if not halt:
            self.duration -= 1
