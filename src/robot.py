from pybricks.parameters import Stop, Button
from pybricks.tools import wait


class Robot:
    def __init__(self, ev3, max_x, max_y, max_z, motor_x, motor_y, motor_z,
                 color_sensor, horizontal_speed, vertical_speed):
        self.ev3 = ev3
        self.max_x = max_x
        self.max_y = max_y
        self.max_z = max_z
        self.motor_x = motor_x
        self.motor_y = motor_y
        self.motor_z = motor_z
        self.color_sensor = color_sensor
        self.horizontal_speed = horizontal_speed
        self.vertical_speed = vertical_speed

        self.MOTOR_SPEED = 200
        self.z_axis_top = 0
        self.standby_position = (0, 0)
        self.pick_up_position = (350, 54)
        self.drop_off_position = (350, 0)
        self.colors_storage = {"red": 0, "blue": 0, "green": 0, "yellow": 0, "lightGreen": 0, "orange": 0}
        self.color_positions = {
            "red": [(360, 450), (600, 450)],
            "blue": [(360, 450), (75, 450)],
            "green": [(360, 680), (600, 680)],
            "yellow": [(360, 680), (75, 680)],
            "lightGreen": [(360, 910), (600, 910)],
            "orange": [(360, 910), (75, 910)]
        }

    def manual_control(self, z_axis_mode):
        """Handle manual button-based control of the robot."""
        pressed_buttons = self.ev3.buttons.pressed()

        if z_axis_mode:
            self._handle_vertical_movement(pressed_buttons)
        else:
            self._handle_forward_movement(pressed_buttons)

        self._handle_horizontal_movement(pressed_buttons)

    def _handle_movement(self, motor, min_angle, max_angle, pos_button, neg_button, pressed_buttons):
        """Handle movement for a specified motor in a given axis, with min and max angle limits."""
        current_angle = motor.angle()
        if pos_button in pressed_buttons and neg_button not in pressed_buttons and current_angle < max_angle:
            motor.run(self.MOTOR_SPEED)
        elif neg_button in pressed_buttons and pos_button not in pressed_buttons and current_angle > min_angle:
            motor.run(-self.MOTOR_SPEED)
        else:
            motor.stop()

    def _handle_vertical_movement(self, pressed_buttons):
        """Handle up/down movement in z-axis mode."""
        self._handle_movement(self.motor_z, self.z_axis_top, self.max_z, Button.DOWN, Button.UP, pressed_buttons)

    def _handle_forward_movement(self, pressed_buttons):
        """Handle forward/backward movement."""
        self._handle_movement(self.motor_y, 0, self.max_y, Button.UP, Button.DOWN, pressed_buttons)

    def _handle_horizontal_movement(self, pressed_buttons):
        """Handle left/right movement."""
        self._handle_movement(self.motor_x, 0, self.max_x, Button.RIGHT, Button.LEFT, pressed_buttons)

    def automatic_storage(self, timer):
        """Handle automatic storage of the LEGO bricks."""
        color = self.detect_color()

        if color is not None and self.colors_storage.get(color, 0) == 1:
            if timer.time() > 500:
                self.ev3.screen.clear()
                self.ev3.screen.print("\n")
                self.ev3.screen.print("Color is already".center(21))
                self.ev3.screen.print("in storage".center(25))
                timer.reset()
            return

        # Display the detected color every 500 ms
        if color is not None:
            wait(250)
            color = self.detect_color()
            self.display_color(color)
            timer.reset()
        elif timer.time() > 500:
            self.ev3.screen.clear()
            self.ev3.screen.print("\n")
            self.ev3.screen.print("No color".center(25))
            self.ev3.screen.print("detected".center(25))
            timer.reset()

        # Exit if color is not recognized
        if color not in self.color_positions:
            return

        self.colors_storage[color] += 1
        # Perform the storage sequence
        self.lift_to_top()
        self.move_to_pickup_position()
        self.lower_to_grab()
        self.move_to_storage(color)
        self.release_brick(color)
        self.move_to_dropoff_position()
        self.move_to_standby_position()
        self.ev3.screen.clear()

    def display_color(self, color):
        """Display the detected color on the EV3 screen."""
        self.ev3.screen.clear()
        self.ev3.screen.print("\n")
        self.ev3.screen.print("Detected color:".center(21))
        self.ev3.screen.print(str(color).center(25))

    def lift_to_top(self):
        """Move the z-axis to the top position."""
        self.motor_z.run_target(self.vertical_speed, self.z_axis_top, then=Stop.HOLD, wait=True)

    def lower_to_grab(self):
        """Move the z-axis to the bottom to grab the LEGO brick."""
        self.motor_z.run_target(self.vertical_speed, self.max_z, then=Stop.HOLD, wait=True)

    def move_to_storage(self, color):
        """Move to the hallway and target position for the specified color."""
        positions = self.color_positions[color]
        self.move_to_position(positions[0])
        self.move_to_position(positions[1])

    def release_brick(self, color):
        """Release the LEGO brick by lifting the z-axis, then move back to hallway."""
        self.lift_to_top()
        hallway_position = self.color_positions[color][0][0]
        self.motor_x.run_target(self.horizontal_speed, hallway_position, then=Stop.HOLD, wait=True)

    def move_to_standby_position(self):
        """Move to the standby position."""
        self.move_to_position(self.standby_position, wait_x=False)

    def move_to_pickup_position(self):
        """Move to the pickup position."""
        self.move_to_position(self.pick_up_position, wait_y=False)

    def move_to_dropoff_position(self):
        """Move to the drop-off position."""
        self.move_to_position(self.drop_off_position)

    def move_to_position(self, position, wait_x=True, wait_y=True):
        """Move the robot to a specific position."""
        self.motor_x.run_target(self.horizontal_speed, position[0], then=Stop.HOLD, wait=wait_x)
        self.motor_y.run_target(self.horizontal_speed, position[1], then=Stop.HOLD, wait=wait_y)

    def retrieve(self, color):
        """Retrieve a brick of the specified color from storage."""
        if self.colors_storage.get(color, 0) == 0:
            return

        self.colors_storage[color] -= 1

        self.move_to_position(self.color_positions[color][0])
        self.move_to_position(self.color_positions[color][1])
        self.lower_to_grab()
        self.move_to_position(self.color_positions[color][0])
        self.move_to_dropoff_position()
        self.lift_to_top()
        self.move_to_standby_position()

    def detect_color(self):
        """Detect the color of the object in front of the color sensor."""
        threshold = 3
        colors = {
            "red": (8, 0, 0),
            "blue": (0, 2, 24),
            "green": (-1, 5, 0),
            "yellow": (12, 8, 1),
            "lightGreen": (4, 7, 1),
            "orange": (13, 1, 0)
        }
        value = self.color_sensor.rgb()

        for color, rgb in colors.items():
            if all(abs(value[i] - rgb[i]) < threshold for i in range(3)):
                return color

    def calibrate(self):
        """Calibrate the motors to the zero position."""
        stall_torque = 40  # Percentage of the maximum torque
        self.motor_z.run_until_stalled(-self.vertical_speed, Stop.HOLD, stall_torque)
        self.motor_x.run_until_stalled(-self.horizontal_speed, Stop.HOLD, stall_torque)
        self.motor_y.run_until_stalled(-self.horizontal_speed, Stop.HOLD, stall_torque)
        self.motor_z.reset_angle(0)
        self.motor_x.reset_angle(0)
        self.motor_y.reset_angle(0)
        self.motor_z.run_target(self.vertical_speed, 20, then=Stop.HOLD, wait=False)
        self.motor_x.run_target(self.vertical_speed, 50, then=Stop.HOLD, wait=False)
        self.motor_y.run_target(self.vertical_speed, 55, then=Stop.HOLD, wait=True)
        self.motor_z.reset_angle(0)
        self.motor_x.reset_angle(0)
        self.motor_y.reset_angle(0)
