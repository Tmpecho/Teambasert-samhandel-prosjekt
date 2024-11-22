from pybricks.parameters import Button


class MenuSystem:
    def __init__(self, ev3, robot):
        self.ev3 = ev3
        self.robot = robot
        self.menu_page = 0
        self.menu_rendered = False
        self.up_button_pressed = False
        self.down_button_pressed = False
        self.center_button_pressed = False
        self.colors = ["red", "blue", "green", "yellow", "lightGreen", "orange"]

    def navigate_menu(self):
        pressed_buttons = self.ev3.buttons.pressed()

        if Button.UP in pressed_buttons and Button.DOWN not in pressed_buttons and not self.up_button_pressed:
            self.up_button_pressed = True
            self.ev3.screen.clear()
            self.menu_rendered = False
            self.menu_page = (self.menu_page - 1) % 6
        if Button.UP not in pressed_buttons:
            self.up_button_pressed = False

        if Button.DOWN in pressed_buttons and Button.UP not in pressed_buttons and not self.down_button_pressed:
            self.down_button_pressed = True
            self.ev3.screen.clear()
            self.menu_rendered = False
            self.menu_page = (self.menu_page + 1) % 6
        if Button.DOWN not in pressed_buttons:
            self.down_button_pressed = False

        if Button.CENTER in pressed_buttons and not self.center_button_pressed:
            self.center_button_pressed = True
            self.robot.retrieve(self.colors[self.menu_page])
        if Button.CENTER not in pressed_buttons:
            self.center_button_pressed = False

        if not self.menu_rendered:
            images = [
                "images/red.png",
                "images/blue.png",
                "images/green.png",
                "images/yellow.png",
                "images/lightgreen.png",
                "images/orange.png"
            ]
            self.ev3.screen.load_image(images[self.menu_page])
            self.menu_rendered = True
