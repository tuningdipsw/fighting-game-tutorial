import pygame as pg
import sys

import fps_counter as fps
import constants
import inputs

pg.init()
window = pg.display.set_mode((constants.WINDOW_WIDTH, constants.WINDOW_HEIGHT))
fpsCounter = fps.FpsCounter()

current_frame = 0
inputHistoryP1 = inputs.InputHistory("P1")
inputHistoryP2 = inputs.InputHistory("P2")

def processInput():
    # Method (1): Use key.get_pressed()
    parseKeysPressed()
    
    # Method (2): Event queue (not used)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            cleanupGame()
            break

def parseKeysPressed():
    '''
    Checks what keys are currently being pressed, 
    and creates a corresponding Input in input_history.
    '''
    input = inputs.keysPressedToInput(current_frame)
    inputHistoryP1.append(input)

def cleanupGame():
    '''
    Run any cleanup before exiting the game.
    '''
    pg.quit()
    sys.exit()
        
def update():
    pass

def render():
    window.fill(constants.BLACK)
    fpsCounter.render(window)
    inputHistoryP1.render(window)
    inputHistoryP2.render(window) # no Inputs being added here right now
    
    pg.display.update()

running = True
while running:
    processInput()
    update()
    render()
    
    current_frame = current_frame + 1
    fpsCounter.clock.tick(constants.FRAME_RATE_CAP)

