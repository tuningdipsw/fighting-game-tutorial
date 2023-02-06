import pytest
from unittest import mock

from pygame import key, locals

import inputs
from inputs import Button

default_keybinds = {}
default_keybinds[locals.K_7] = Button.LEFT
default_keybinds[locals.K_8] = Button.DOWN
default_keybinds[locals.K_9] = Button.RIGHT
default_keybinds[locals.K_SPACE] = Button.UP
default_keybinds[locals.K_z] = Button.PUNCH
default_keybinds[locals.K_x] = Button.KICK
default_keybinds[locals.K_c] = Button.SLASH
default_keybinds[locals.K_v] = Button.HEAVY
default_keybinds[locals.K_d] = Button.DUST
default_keybinds[locals.K_f] = Button.MACRO_PKS
default_keybinds[locals.K_g] = Button.MACRO_PK
default_keybinds[locals.K_h] = Button.MACRO_PD
default_keybinds[locals.K_j] = Button.MACRO_PKSH

def create_key_mock(pressed_key_list):
    '''
    Takes a list of key names (pygame.locals, which are technically ints)
    and returns a simulated pygame.key.get_pressed() output with those keys pressed.
    '''
    tmp = [0] * 300
    for key in pressed_key_list:
        tmp[key] = 1
    return tmp

def create_buttons_dict(pressed_buttons: list[Button]) -> dict[Button, bool]:
    '''
    Takes a list of Buttons and returns a proper dict[Button, bool].
    '''
    buttons = {}
    for button in list(Button):
        buttons[button] = button in pressed_buttons
    return buttons

keysPressedToInput_testcases = [
    # single key
    ([locals.K_z],
     [Button.PUNCH]),
    
    # all single keys
    ([locals.K_z, locals.K_x, locals.K_c, locals.K_v, locals.K_d],
     [Button.PUNCH, Button.KICK, Button.SLASH, Button.HEAVY, Button.DUST]),
    
    # macro keys
    ([locals.K_f],
     [Button.PUNCH, Button.KICK, Button.SLASH, Button.MACRO_PKS]),
    
    # multiple macro keys
    ([locals.K_f, locals.K_h],
     [Button.PUNCH, Button.KICK, Button.SLASH, Button.DUST, Button.MACRO_PKS, Button.MACRO_PD]),
    
    # macro + single
    ([locals.K_z, locals.K_f],
     [Button.PUNCH, Button.KICK, Button.SLASH, Button.MACRO_PKS]),
    
    # simple SOCD
    ([locals.K_7, locals.K_9],
     [])
]

# Note: Mocking keybinds to default prevents test from breaking when hardcoded keys are changed
@pytest.mark.parametrize("test_input_keys, expected_buttons", keysPressedToInput_testcases)
@mock.patch.object(inputs, "keybinds", default_keybinds)
@mock.patch.object(key, "get_pressed")
def test_keysPressedToInput(mock_key_get_pressed, test_input_keys, expected_buttons):
    mock_key_get_pressed.return_value = create_key_mock(test_input_keys)
    current_frame = 1
    
    output = inputs.keysPressedToInput(current_frame)
    expected = inputs.Input(create_buttons_dict(expected_buttons), 1, 2)
    
    assert output == expected


cleanSocdButtons_testcases = [
    # L+R = neutral
    ({Button.LEFT: True, Button.RIGHT: True, Button.UP: False, Button.DOWN: True},
     {Button.LEFT: False, Button.RIGHT: False, Button.UP: False, Button.DOWN: True}),
    
    # U+D = neutral
    ({Button.LEFT: True, Button.RIGHT: False, Button.UP: True, Button.DOWN: True},
     {Button.LEFT: True, Button.RIGHT: False, Button.UP: False, Button.DOWN: False}),
    
    # both rules at the same time
    ({Button.LEFT: True, Button.RIGHT: True, Button.UP: True, Button.DOWN: True},
     {Button.LEFT: False, Button.RIGHT: False, Button.UP: False, Button.DOWN: False})
]

@pytest.mark.parametrize("test_input, expected", cleanSocdButtons_testcases)
def test_cleanSocdButtons(test_input, expected):
    assert inputs.cleanSocdButtons(test_input) == expected
    

def test_inputHistory_append():
    ih = inputs.InputHistory("P1")
    ih.append(inputs.Input(create_buttons_dict([Button.PUNCH]), 1, 2))
    ih.append(inputs.Input(create_buttons_dict([Button.PUNCH]), 2, 3))
    
    # test input deduplication
    expected = inputs.Input(create_buttons_dict([Button.PUNCH]), 1, 3)
    assert len(ih.inputs) == 1
    assert ih.inputs[-1] == expected
    
    # regular case
    ih.append(inputs.Input(create_buttons_dict([Button.KICK]), 3, 4))
    expected = inputs.Input(create_buttons_dict([Button.KICK]), 3, 4)
    assert len(ih.inputs) == 2
    assert ih.inputs[-1] == expected
