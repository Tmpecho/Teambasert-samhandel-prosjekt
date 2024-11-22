from unittest.mock import MagicMock

import pytest
from pybricks.parameters import Button

from menu import MenuSystem


@pytest.fixture
def menu_system():
    ev3_mock = MagicMock()
    robot_mock = MagicMock()
    menu_system = MenuSystem(ev3_mock, robot_mock)
    return menu_system


def test_navigate_menu_up(menu_system):
    menu_system.ev3.buttons.pressed.return_value = [Button.UP]
    menu_system.up_button_pressed = False
    menu_system.menu_page = 0
    menu_system.menu_rendered = True

    menu_system.navigate_menu()

    assert menu_system.up_button_pressed is True
    assert menu_system.menu_page == 5
    assert menu_system.menu_rendered is True  # menu_rendered should be True after rendering


def test_navigate_menu_down(menu_system):
    menu_system.ev3.buttons.pressed.return_value = [Button.DOWN]
    menu_system.down_button_pressed = False
    menu_system.menu_page = 5
    menu_system.menu_rendered = True

    menu_system.navigate_menu()

    assert menu_system.down_button_pressed is True
    assert menu_system.menu_page == 0
    assert menu_system.menu_rendered is True  # menu_rendered should be True after rendering


def test_navigate_menu_select(menu_system):
    menu_system.ev3.buttons.pressed.return_value = [Button.CENTER]
    menu_system.center_button_pressed = False
    menu_system.menu_page = 2  # 'green'
    menu_system.robot.colors_storage = {"green": 1}

    menu_system.navigate_menu()

    assert menu_system.center_button_pressed is True
    menu_system.robot.retrieve.assert_called_with("green")
