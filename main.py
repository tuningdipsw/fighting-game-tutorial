import sys
import pygame as pg
from pygame import locals

import fps_counter as fps
import constants
import inputs
from gamestate import GameState

pg.init()
window = pg.display.set_mode((constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))
fpsCounter = fps.FpsCounter()

inputHistories = {}
inputHistories["P1"] = inputs.InputHistory("P1")
inputHistories["P2"] = inputs.InputHistory("P2")
gameState = GameState(inputHistories)

def processInput():
    # Method (1): Use key.get_pressed()
    parseKeysPressed()
    
    # Method (2): Event queue. For special keys unrelated to character control (debug options)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            cleanupGame()
            break
        elif event.type == pg.KEYDOWN:
            if event.key == locals.K_F7:
                constants.SHOW_INPUT_HISTORY = not constants.SHOW_INPUT_HISTORY  

def parseKeysPressed():
    '''
    Checks what keys are currently being pressed, 
    and creates a corresponding Input in input_history.
    '''
    p1_input = inputs.keysPressedToInput(gameState.current_frame, "P1")
    inputHistories["P1"].append(p1_input)
    p2_input = inputs.keysPressedToInput(gameState.current_frame, "P2")
    inputHistories["P2"].append(p2_input)    

def cleanupGame():
    '''
    Run any cleanup before exiting the game.
    '''
    pg.quit()
    sys.exit()
        
def update():
    gameState.update()

def render():
    window.fill(constants.BLACK)
    
    gameState.render(window)
    
    # debug information (FPS, inputs) on top
    fpsCounter.render(window)
    
    if constants.SHOW_INPUT_HISTORY:
        for ih in inputHistories.values():
            ih.render(window)
    
    pg.display.update()

running = True
while running:
    processInput()
    update()
    render()
    
    fpsCounter.clock.tick(constants.FRAME_RATE_CAP)

