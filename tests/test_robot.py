from unittest.mock import MagicMock

import pytest
from pybricks.parameters import Stop, Button

from robot import Robot


@pytest.fixture
def robot():
    ev3_mock = MagicMock()
    motor_x_mock = MagicMock()
    motor_y_mock = MagicMock()
    motor_z_mock = MagicMock()
    color_sensor_mock = MagicMock()
    horizontal_speed = 350
    vertical_speed = 300
    max_x = 785
    max_y = 1000
    max_z = 400

    robot = Robot(
        ev3=ev3_mock,
        max_x=max_x,
        max_y=max_y,
        max_z=max_z,
        motor_x=motor_x_mock,
        motor_y=motor_y_mock,
        motor_z=motor_z_mock,
        color_sensor=color_sensor_mock,
        horizontal_speed=horizontal_speed,
        vertical_speed=vertical_speed
    )
    return robot


def test_calibrate(robot):
    robot.calibrate()
    robot.motor_z.run_until_stalled.assert_called_with(-robot.vertical_speed, Stop.HOLD, 40)
    robot.motor_x.run_until_stalled.assert_called_with(-robot.horizontal_speed, Stop.HOLD, 40)
    robot.motor_y.run_until_stalled.assert_called_with(-robot.horizontal_speed, Stop.HOLD, 40)
    robot.motor_z.reset_angle.assert_called_with(0)
    robot.motor_x.reset_angle.assert_called_with(0)
    robot.motor_y.reset_angle.assert_called_with(0)


def test_move_to_position(robot):
    position = (100, 200)
    robot.move_to_position(position)
    robot.motor_x.run_target.assert_called_with(robot.horizontal_speed, position[0], then=Stop.HOLD, wait=True)
    robot.motor_y.run_target.assert_called_with(robot.horizontal_speed, position[1], then=Stop.HOLD, wait=True)


def test_detect_color(robot):
    robot.color_sensor.rgb.return_value = (8, 0, 0)
    color = robot.detect_color()
    assert color == "red"

    robot.color_sensor.rgb.return_value = (0, 2, 24)
    color = robot.detect_color()
    assert color == "blue"

    robot.color_sensor.rgb.return_value = (15, 15, 15)
    color = robot.detect_color()
    assert color is None


def test_manual_control(robot):
    # Simulate pressing UP in z-axis mode (positive movement)
    z_axis_mode = True
    robot.ev3.buttons.pressed.return_value = [Button.UP]
    robot.motor_z.angle.return_value = robot.max_z - 1  # Just below max_z
    robot.motor_z.run.reset_mock()
    robot.manual_control(z_axis_mode)
    robot.motor_z.run.assert_called_with(-robot.MOTOR_SPEED)

    # Simulate pressing DOWN in z-axis mode (negative movement)
    robot.ev3.buttons.pressed.return_value = [Button.DOWN]
    robot.motor_z.angle.return_value = 1  # Just above min_z (which is z_axis_top)
    robot.motor_z.run.reset_mock()
    robot.manual_control(z_axis_mode)
    robot.motor_z.run.assert_called_with(robot.MOTOR_SPEED)

    # Simulate pressing RIGHT in horizontal movement
    z_axis_mode = False
    robot.ev3.buttons.pressed.return_value = [Button.RIGHT]
    robot.motor_x.angle.return_value = robot.max_x - 1  # Just below max_x
    robot.motor_x.run.reset_mock()
    robot.manual_control(z_axis_mode)
    robot.motor_x.run.assert_called_with(robot.MOTOR_SPEED)
