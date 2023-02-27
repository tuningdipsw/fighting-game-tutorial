from __future__ import annotations
# https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from enum import Enum

import pygame.locals as locals
import pygame as pg
import constants

class Button(Enum):
    LEFT = 0
    DOWN = 1
    RIGHT = 2
    UP = 3
    PUNCH = 10
    KICK = 11
    SLASH = 12
    HEAVY = 13
    DUST = 14
    MACRO_PK = 20
    MACRO_PD = 21
    MACRO_PKS = 22
    MACRO_PKSH = 23

# define keybindings manually here
# TODO: eventually replace with a proper menu interface for rebinding keys
keybinds = {}
keybinds["P1"] = {}
keybinds["P1"][locals.K_7] = Button.LEFT
keybinds["P1"][locals.K_8] = Button.DOWN
keybinds["P1"][locals.K_9] = Button.RIGHT
keybinds["P1"][locals.K_SPACE] = Button.UP
keybinds["P1"][locals.K_z] = Button.PUNCH
keybinds["P1"][locals.K_x] = Button.KICK
keybinds["P1"][locals.K_c] = Button.SLASH
keybinds["P1"][locals.K_v] = Button.HEAVY
keybinds["P1"][locals.K_d] = Button.DUST
keybinds["P1"][locals.K_f] = Button.MACRO_PKS
keybinds["P1"][locals.K_g] = Button.MACRO_PK
keybinds["P1"][locals.K_h] = Button.MACRO_PD
keybinds["P1"][locals.K_j] = Button.MACRO_PKSH

# placeholder arbitrary P2 keybinds
keybinds["P2"] = {}
keybinds["P2"][locals.K_LEFT] = Button.LEFT
keybinds["P2"][locals.K_DOWN] = Button.DOWN
keybinds["P2"][locals.K_RIGHT] = Button.RIGHT
keybinds["P2"][locals.K_UP] = Button.UP
keybinds["P2"][locals.K_1] = Button.PUNCH
keybinds["P2"][locals.K_2] = Button.KICK
keybinds["P2"][locals.K_3] = Button.SLASH
keybinds["P2"][locals.K_4] = Button.HEAVY
keybinds["P2"][locals.K_5] = Button.DUST
keybinds["P2"][locals.K_6] = Button.MACRO_PKS
keybinds["P2"][locals.K_q] = Button.MACRO_PK
keybinds["P2"][locals.K_w] = Button.MACRO_PD
keybinds["P2"][locals.K_e] = Button.MACRO_PKSH

macro_defs = {}
macro_defs[Button.MACRO_PK] = [Button.PUNCH, Button.KICK]
macro_defs[Button.MACRO_PD] = [Button.PUNCH, Button.DUST]
macro_defs[Button.MACRO_PKS] = [Button.PUNCH, Button.KICK, Button.SLASH]
macro_defs[Button.MACRO_PKSH] = [Button.PUNCH, Button.KICK, Button.SLASH, Button.HEAVY]

def keysPressedToInput(current_frame: int, player: str) -> Input:
    '''
    Takes an int current_frame,
    checks pygame.key.keys_pressed() for all keys currently pressed,
    and returns an Input created with a dict of all assigned Buttons pressed (after SOCD cleaning) and current_frame.
    '''
    keys_pressed = pg.key.get_pressed()
    frame_buttons: dict[Button, bool] = {}
    for (key, button) in keybinds[player].items():
        frame_buttons[button] = keys_pressed[key]
        
    for macro_button in macro_defs.keys():
        if frame_buttons.get(macro_button) and frame_buttons[macro_button]:
            for button in macro_defs[macro_button]:
                frame_buttons[button] = True
    
    frame_buttons = cleanSocdButtons(frame_buttons)
    return Input(frame_buttons, current_frame, current_frame + 1)

def cleanSocdButtons(frame_buttons: dict[Button, bool]) -> dict[Button, bool]:
    '''
    Takes a dict with each assigned Button pressed this frame, 
    and returns a copy of it with SOCD cases handled:
    - UP + DOWN = neutral, remove both
    - LEFT + RIGHT = neutral, remove both
    
    Note that these don't both have to be handled the same way.
    HitBox hardware uses L+R = neutral and U+D = U.
    See https://www.hitboxarcade.com/blogs/support/what-is-socd
    for other possible SOCD resolutions.
    '''
    cleaned_inputs = frame_buttons
    if cleaned_inputs[Button.LEFT] and cleaned_inputs[Button.RIGHT]:
        cleaned_inputs[Button.LEFT] = False
        cleaned_inputs[Button.RIGHT] = False
    if cleaned_inputs[Button.UP] and cleaned_inputs[Button.DOWN]:
        cleaned_inputs[Button.UP] = False
        cleaned_inputs[Button.DOWN] = False
    return cleaned_inputs

def directionsToArrow(buttons: dict[Button, bool]) -> str:
    '''
    Takes a dict of buttons pressed,
    and returns a character of the arrow corresponding to their direction (or ' ' for neutral).
    
    It is assumed that the buttons have already been SOCD cleaned.
    '''
    if buttons[Button.LEFT]:
        if buttons[Button.UP]:
            return '↖' #
        elif buttons[Button.DOWN]:
            return '↙'
        else:
            return '←'
    elif buttons[Button.RIGHT]:
        if buttons[Button.UP]:
            return '↗'
        elif buttons[Button.DOWN]:
            return '↘' #
        else:
            return '→'
    elif buttons[Button.DOWN]:
        return '↓'
    elif buttons[Button.UP]:
        return '↑'
    else:
        return ' '

def attackButtonsToLetters(buttons: dict[Button, bool]) -> str:
    '''
    Takes a dict of buttons pressed
    and returns a string of letters (or ' ' for nothing) representing all attack buttons pressed.
    '''
    string = ""
    if buttons[Button.PUNCH]:
        string = string + "P"
    if buttons[Button.KICK]:
        string = string + "K"
    if buttons[Button.SLASH]:
        string = string + "S"
    if buttons[Button.HEAVY]:
        string = string + "H"
    if buttons[Button.DUST]:
        string = string + "D"
    return string

class Input():
    def __init__(self, buttons: dict[Button, bool], start_frame: int, end_frame: int):
        self.buttons = buttons
        # Frame number that this Input began on, inclusive.
        self.start_frame = start_frame
        # Frame number that this Input was released on, exclusive (self.buttons changed on this frame).
        self.end_frame = end_frame
        
    # https://stackoverflow.com/questions/390250/elegant-ways-to-support-equivalence-equality-in-python-classes
    def __eq__(self, other):
        if isinstance(other, Input):
            return self.buttons == other.buttons and self.start_frame == other.start_frame and self.end_frame == other.end_frame
        return NotImplemented

class InputHistory():
    def __init__(self, player: str):
        self.player = player # "P1" or "P2"
        self.inputs: list[Input] = []
    
    def append(self, input: Input) -> None:
        '''
        Takes an Input and adds it to self.inputs,
        and removes old inputs from self.inputs.
        '''
        if len(self.inputs) > 0 and input.buttons == self.inputs[-1].buttons:
            # If input buttons are the same as last input, combine it with last input instead of making a duplicate.
            self.inputs[-1].end_frame = self.inputs[-1].end_frame + 1
        else:
            self.inputs.append(input)
            
        # Don't need to keep inputs after a certain amount of time has passed.
        # Down/back charge history will be stored in game state, so deleting old inputs has no effect on charge moves.
        if len(self.inputs) > 30:
            self.inputs.pop(0)
            
    def getFrameButtons(self, frame_number: int) -> dict[Button, bool]:
        '''
        Takes a frame number, and returns the dict of buttons pressed on that frame.
        
        Throws an IndexError if no input can be found for that frame number.
        '''
        if frame_number < self.inputs[0].start_frame:
            raise IndexError(f"Frame number {frame_number} < earliest input start frame {self.inputs[0].start_frame}")
        elif frame_number >= self.inputs[-1].end_frame:
            raise IndexError(f"Frame number {frame_number} >= latest input end frame {self.inputs[-1].end_frame}")
        
        for input in reversed(self.inputs):
            if frame_number >= input.start_frame and frame_number < input.end_frame:
                return input.buttons
        
        raise IndexError(f"Frame number {frame_number} not found in inputs")
    
    def render(self, display: pg.surface.Surface) -> None:
        # Font that supports Unicode arrows
        font = pg.font.Font("assets/seguisym.ttf", 20)
    
        for i in range(len(self.inputs)):
            # Print the newest inputs first, closer to the top.
            input = self.inputs[len(self.inputs) - 1 - i]
            
            arrow_direction = directionsToArrow(input.buttons)
            attack_buttons = attackButtonsToLetters(input.buttons)
            input_string = f"{arrow_direction} {attack_buttons} {input.end_frame - input.start_frame}"
            
            text = font.render(f"{input_string}", True, constants.WHITE)
            # TODO remove magic numbers that don't account for window size
            if self.player == "P1":
                x = 10
            else:
                x = constants.WINDOW_WIDTH - 80
            display.blit(text, (x, 15 * i))