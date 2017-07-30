import pygame
import os
from Constants import *

class Sprite():
    def __init__(self, file, framesize, frame_num, screen, player, scale, rev = False, is_enemy = False, enemy = None):
        self.source = pygame.image.load(os.path.join(file)).convert_alpha()
        self.frame_width = framesize[0]
        self.frame_height = framesize[1]
        self.curr_frame = 1
        self.rev = rev
        self.frame_num = frame_num
        if rev:
            self.curr_frame = self.frame_num
        self.screen = screen
        self.scale = scale
        self.player = player
        self.is_enemy = is_enemy
        self.frame_dict = {}
        self.process_frames()

    def get_frame_rect(self, frame):
        framesize = (self.frame_width, self.frame_height)
        position = (self.frame_width * (frame - 1), 0)
        return position + framesize

    def tic(self, pos, halt = False, enemy = None):
        self.render_frame(self.curr_frame, pos)
        if not halt:
            self.curr_frame += 1
        if self.curr_frame == self.frame_num + 1:
            if not self.is_enemy:
                self.player.anim = STATE_IDLE
            self.curr_frame = 1

    def process_frames(self):
        for i in range(0, self.frame_num):
            surface = pygame.Surface((self.frame_width, self.frame_height)).convert_alpha()
            surface.fill((0, 0, 255))
            surface.set_alpha(127)
            position = self.get_frame_rect(i)
            surface.blit(self.source, (0, 0), position)
            self.remove_trans(surface)
            if self.frame_width > self.frame_height:
                surface = pygame.transform.scale(surface, (int(self.scale * self.frame_width/float(self.frame_height)), self.scale))
            else:
                surface = pygame.transform.scale(surface, (self.scale, int(self.scale * self.frame_height/float(self.frame_width))))
            self.frame_dict[i] = surface
            self.frame_dict[i + 1] = surface

    def render_frame(self, frame, pos):
        surface = self.frame_dict[frame]
        self.screen.blit(surface, pos)

    def remove_trans(self, img):
        width, height = img.get_size()
        for x in range(0, width):
            for y in range(0, height):
                r, g, b, alpha = img.get_at((x, y))
                if r < 50 and g < 50 and b > 200:
                    img.set_at((x, y), (r, g, b, 0))
