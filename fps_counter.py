import pygame as pg
import constants

class FpsCounter:
    def __init__(self):
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont("Verdana", 10)
        self.text = self.font.render(str(self.clock.get_fps()), True, constants.WHITE)
        
    def render(self, display):
        fps = int(self.clock.get_fps())
        self.text = self.font.render(f"{fps}FPS", True, constants.WHITE)
        display.blit(self.text, (constants.WINDOW_WIDTH - 50, 5))