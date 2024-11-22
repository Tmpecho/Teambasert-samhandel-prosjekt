from pybricks.ev3devices import Motor, ColorSensor, TouchSensor
from pybricks.hubs import EV3Brick
from pybricks.parameters import Port, Direction, Color, Button
from pybricks.tools import StopWatch, wait

from menu import MenuSystem
from robot import Robot


class RobotController:
    def __init__(self):
        # Initialize EV3 brick, motors, sensors, and timer
        self.ev3 = EV3Brick()
        self.timer = StopWatch()

        self.motor_x = Motor(Port.D, positive_direction=Direction.COUNTERCLOCKWISE)
        self.motor_y = Motor(Port.C, positive_direction=Direction.COUNTERCLOCKWISE)
        self.motor_z = Motor(Port.B, positive_direction=Direction.COUNTERCLOCKWISE)

        self.color_sensor = ColorSensor(Port.S4)
        self.touch_sensor = TouchSensor(Port.S1)

        # Initialize Robot and MenuSystem
        self.robot = Robot(
            ev3=self.ev3,
            max_x=785,
            max_y=1000,
            max_z=400,
            motor_x=self.motor_x,
            motor_y=self.motor_y,
            motor_z=self.motor_z,
            color_sensor=self.color_sensor,
            horizontal_speed=550,
            vertical_speed=550
        )

        self.menu_system = MenuSystem(self.ev3, self.robot)

        # Initialize mode variables
        self.mode = "manual"
        self.z_axis_mode = False
        self.center_button_pressed = False
        self.mode_switch_button_is_pressed = False

        # Calibrate the robot
        self.robot.calibrate()

    def run(self):
        while True:
            pressed_buttons = self.ev3.buttons.pressed()
            mode_switch_button = self.touch_sensor.pressed()

            # Mode switching logic
            if Button.LEFT in pressed_buttons and Button.RIGHT in pressed_buttons and self.mode != "calibrate":
                self.ev3.light.on(Color.RED)
                self.ev3.screen.clear()
                self.ev3.screen.print("Calibration active.")
                self.ev3.screen.print("Please wait.")
                self.robot.calibrate()
                self.mode = "manual"
                self.ev3.light.on(Color.GREEN)
                self.ev3.screen.clear()
                self.ev3.screen.print("Mode: Manual control")
                continue

            if mode_switch_button and not self.mode_switch_button_is_pressed:
                self.mode_switch_button_is_pressed = True

                if self.mode == "manual":
                    self.mode = "automatic_storage"
                    self.ev3.light.on(Color.ORANGE)
                    self.ev3.screen.clear()
                    wait(100)
                elif self.mode == "automatic_storage":
                    self.mode = "automatic_retrieval"
                    self.ev3.light.on(Color.YELLOW)
                    self.ev3.screen.clear()
                elif self.mode == "automatic_retrieval":
                    self.menu_system.menu_rendered = False
                    self.mode = "manual"
                    self.ev3.light.on(Color.GREEN)
                    self.ev3.screen.clear()
                    self.ev3.screen.print("Mode: Manual control")

            elif not mode_switch_button:
                self.mode_switch_button_is_pressed = False

            # Handle modes
            if self.mode == "manual":
                # Update display every 1000 ms
                if self.timer.time() > 1000:
                    self.ev3.screen.clear()
                    self.ev3.screen.print("\nZ-axis mode: " + str(self.z_axis_mode))
                    self.ev3.screen.print("X-axis: " + str(self.robot.motor_x.angle()))
                    self.ev3.screen.print("Y-axis: " + str(self.robot.motor_y.angle()))
                    self.ev3.screen.print("Z-axis: " + str(self.robot.motor_z.angle()))
                    self.ev3.screen.print("Colors: " + str(self.robot.color_sensor.rgb()))
                    self.timer.reset()

                # Toggle z-axis mode with center button
                if Button.CENTER in pressed_buttons and not self.center_button_pressed:
                    self.z_axis_mode = not self.z_axis_mode
                    self.center_button_pressed = True
                elif Button.CENTER not in pressed_buttons:
                    self.center_button_pressed = False

                self.robot.manual_control(self.z_axis_mode)

            elif self.mode == "automatic_storage":
                self.robot.automatic_storage(self.timer)

            elif self.mode == "automatic_retrieval":
                self.menu_system.navigate_menu()
