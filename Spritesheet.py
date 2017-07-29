import pygame
import os
from Constants import *

class Sprite():
    def __init__(self, file, framesize, frame_num, screen, player, scale, rev = False, is_enemy = False):
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

    def get_frame_rect(self, frame):
        framesize = (self.frame_width, self.frame_height)
        position = (self.frame_width * (frame - 1), 0)
        return position + framesize

    def tic(self, pos, halt = False):
        self.render_frame(self.curr_frame, pos)
        if not halt:
            self.curr_frame += 1
        if self.curr_frame > self.frame_num:
            if not self.is_enemy:
                self.player.state = STATE_IDLE
            self.curr_frame = 1

    def render_frame(self, frame, pos):
        surface = pygame.Surface((self.frame_width, self.frame_height)).convert_alpha()
        surface.fill((255, 0, 0))
        surface.set_alpha(127)
        position = self.get_frame_rect(frame)
        surface.blit(self.source, (0, 0), position)
        self.remove_trans(surface)
        surface = pygame.transform.scale(surface, (int(self.scale * self.frame_width/float(self.frame_height)), self.scale))
        self.screen.blit(surface, pos)

    def remove_trans(self, img):
        width, height = img.get_size()
        for x in range(0, width):
            for y in range(0, height):
                r, g, b, alpha = img.get_at((x, y))
                if r > 180 and g < 50 and b < 50:
                    img.set_at((x, y), (r, g, b, 0))
