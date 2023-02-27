from __future__ import annotations
import pygame as pg

import constants
import inputs
from inputs import Button

class GameState():
    def __init__(self, inputHistories: dict[str, inputs.InputHistory]) -> None:
        self.current_frame: int = 0
        self.round_timer: float = 99.0
        self.inputHistories = inputHistories
        
        self.characters: dict[str, Character]= {}
        self.characters["P1"] = Character(inputHistories["P1"], self, "P1")
        self.characters["P2"] = Character(inputHistories["P2"], self, "P2")
        self.characters["P1"].assignOpponent(self.characters["P2"])
        self.characters["P2"].assignOpponent(self.characters["P1"])
        
        # for rendering use
        self.font = pg.font.SysFont("Verdana", 36)
        
    def update(self) -> None:
        # TODO: may add more nuance to round timer than this
        self.round_timer = self.round_timer - 1.0 / constants.FRAME_RATE_CAP
        
        for character in self.characters.values():
            character.update(self.current_frame)
            
        self.current_frame = self.current_frame + 1
        
    def render(self, display: pg.surface.Surface) -> None:
        # render UI
        self.renderRoundTimer(display)
        self.renderHpBars(display)
        
        # render characters
        for character in self.characters.values():
            character.render(display)
        
    def renderRoundTimer(self, display: pg.surface.Surface) -> None:
        '''
        Basic font-based method of rendering the round timer.
        '''
        rounded_timer = "{:.0f}".format(self.round_timer)
        self.text = self.font.render(rounded_timer, True, constants.WHITE)
        rect = self.text.get_rect()
        rect.midtop = (int(constants.WINDOW_WIDTH / 2), 5)
        display.blit(self.text, rect)
        
    def renderHpBars(self, display: pg.surface.Surface) -> None:
        '''
        Basic HP bar UI.
        '''
        hp_bar_length = constants.WINDOW_WIDTH / 2
        
        # P1
        missing_hp_rect = pg.Rect(0, 0, hp_bar_length, 20)
        p1_hp_proportion = max(0.0, self.characters["P1"].hp / self.characters["P1"].maxHp)
        current_hp_rect = pg.Rect(missing_hp_rect)
        current_hp_rect.width = int(hp_bar_length * p1_hp_proportion)
        # For P1, the last bit of HP is the rightmost one
        current_hp_rect.topright = missing_hp_rect.topright
        
        pg.draw.rect(display, constants.WHITE, missing_hp_rect)
        pg.draw.rect(display, constants.RED, current_hp_rect)
        
        # P2
        missing_hp_rect = pg.Rect(0, 0, hp_bar_length, 20)
        missing_hp_rect.topright = (constants.WINDOW_WIDTH, 0)
        
        p2_hp_proportion = max(0.0, self.characters["P2"].hp / self.characters["P2"].maxHp)
        current_hp_rect = pg.Rect(missing_hp_rect)
        current_hp_rect.width = int(hp_bar_length * p2_hp_proportion)
        # For P2, the last bit of HP is the leftmost one (no change required)
        
        pg.draw.rect(display, constants.WHITE, missing_hp_rect)
        pg.draw.rect(display, constants.BLUE, current_hp_rect)
        
        
class Character():
    def __init__(self, inputHistory: inputs.InputHistory, gameState: GameState, player: str) -> None:
        # Pass in references to other systems Character needs to know about
        self.inputHistory = inputHistory
        self.gameState = gameState
        
        if player == "P1":
            self.xpos: int = 50
        else: # P2
            self.xpos: int = constants.WINDOW_WIDTH - 50
        self.ypos: int = constants.WINDOW_HEIGHT - 50
        
        # TODO: probably want a special load_character helper for loading char's sprites en masse
        self.surface: pg.Surface = pg.image.load('assets/guy2.png').convert_alpha()
        
        # TODO: arbitrary placeholder values, would like to load this in from a character data file
        self.maxHp: int = 200
        self.hp: int = self.maxHp
        self.forwardWalkspeed: int = 10
        self.backwardWalkspeed: int = 5
        
        self.facingLeft = False
        
        self.roundsWon = 0
        
    def assignOpponent(self, opponent: Character) -> None:
        '''
        Part of initialization, but deferred until after both Characters have been created.
        '''
        self.opponent = opponent
    
    def update(self, frame_number: int) -> None:
        '''
        Takes a frame_number, and updates self based on the Buttons pressed on that frame.
        '''
        frame_buttons = self.inputHistory.getFrameButtons(frame_number)
        if (frame_buttons[Button.LEFT] or frame_buttons[Button.RIGHT]):
            self.walk(frame_buttons)
        
        # Limits on xpos
        self.xpos = min(constants.WINDOW_WIDTH, self.xpos)
        self.xpos = max(self.xpos, 0)
        
        self.faceOpponent()
    
    def walk(self, buttons: dict[Button, bool]) -> None:
        if self.facingLeft:
            if buttons[Button.LEFT]:
                self.xpos = self.xpos - self.forwardWalkspeed
            else:
                self.xpos = self.xpos + self.backwardWalkspeed
                self.hp = self.hp - 1 # TODO: temporarily added to show HP loss
        else:
            if buttons[Button.LEFT]:
                self.xpos = self.xpos - self.backwardWalkspeed
                self.hp = self.hp - 1 # TODO: temporarily added to show HP loss
            else:
                self.xpos = self.xpos + self.forwardWalkspeed
    
    def isRightOfOpponent(self) -> bool:
        '''
        Note that the blocking direction check uses this directly,
        but general input flip (forward vs back), sprite flip, hit/hurtbox flip
        are determined by self.facingLeft instead,
        a value that isn't always updated every frame.
        '''
        return self.xpos >= self.opponent.xpos
    
    def faceOpponent(self) -> None:
        '''
        Sets self.facingLeft based on Character's position relative to opponent Character.
        '''
        self.facingLeft = self.isRightOfOpponent()
        
    def render(self, display: pg.surface.Surface) -> None:
        rect = pg.Rect(self.surface.get_rect())
        rect.midbottom = (self.xpos, self.ypos)
        
        surface_facing = self.surface
        if self.facingLeft:
            surface_facing = pg.transform.flip(surface_facing, True, False)

        display.blit(surface_facing, rect)
        