from Constants import *

class Enemy():
    def __init__(self, name, attack_sequence, sprite_sequence, pos):
        self.name = name
        self.attack_sequence = attack_sequence
        self.sprite_sequence = sprite_sequence
        self.state = 0
        self.invulnerable = False
        self.pos = pos

    def attack(self):
        self.state += 1
        if self.state == len(self.attack_sequence):
            self.state = 0
        if self.state in [ENM_BOT_ATK, ENM_TOP_ATK]:
            self.invulnerable = True
        else:
            self.invulnerable = False
