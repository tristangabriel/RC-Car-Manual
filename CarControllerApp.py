from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock
from kivy.core.window import Window
from datetime import datetime
from pyfirmata import Arduino, util

# Global variables for Arduino communication
board = Arduino('COM9', baudrate=9600)  # Adjust COM port as per your setup

# Enable pins for PWM (speed control)
motor1 = board.get_pin('d:3:p')  # Enable pin for motor 1
motor2 = board.get_pin('d:11:p')  # Enable pin for motor 2

MOTOR_DIRECTION = 0x01

def set_motor_direction(direction):
    board.send_sysex(MOTOR_DIRECTION, [direction])

# Initialize speed
speed = 0
current_direction = None

class ControllerScreen(Screen):
    
    def __init__(self, **kwargs):
        super(ControllerScreen, self).__init__(**kwargs)
        self.build()

    def build(self):
        self.layout = FloatLayout()
        
        # Directional buttons with dynamic size hints
        self.btn_left = Button(text='Left', font_size=20, size_hint=(0.2, 0.1), bold=True)
        self.btn_left.pos_hint = {'center_x': 0.25, 'center_y': 0.7}
        
        self.btn_forward = Button(text='Forward', font_size=20, size_hint=(0.2, 0.1), bold=True)
        self.btn_forward.pos_hint = {'center_x': 0.5, 'center_y': 0.85}
        
        self.btn_right = Button(text='Right', font_size=20, size_hint=(0.2, 0.1), bold=True)
        self.btn_right.pos_hint = {'center_x': 0.75, 'center_y': 0.7}
        
        self.btn_backward = Button(text='Backward', font_size=20, size_hint=(0.2, 0.1), bold=True)
        self.btn_backward.pos_hint = {'center_x': 0.5, 'center_y': 0.55}
        
        self.btn_stop = Button(text='Stop', font_size=20, size_hint=(0.2, 0.1), bold=True)
        self.btn_stop.pos_hint = {'center_x': 0.5, 'center_y': 0.7}
        
        # Speed label
        self.speed_label = Label(text=f'Speed: {speed:.0f}', font_size=18, size_hint=(None, None), width=300, height=30, bold=True)
        self.speed_label.pos_hint = {'center_x': 0.5, 'center_y': 0.35}
        
        # Speed slider
        self.slider = Slider(min=0, max=255, value=speed, step=1, size_hint=(None, None), width=300, height=30)
        self.slider.pos_hint = {'center_x': 0.5, 'center_y': 0.30}
        self.slider.bind(value=self.on_slider_value_change)
        
        # Adjusting slider width to span the window
        self.slider.width = Window.width * 0.8  # Adjust as needed
        
        # Feedback label
        self.feedback_label = Label(text='Ready', font_size=20, size_hint=(None, None), width=300, height=50, bold=True)
        self.feedback_label.pos_hint = {'center_x': 0.5, 'center_y': 0.2}
        
        # Add widgets to layout
        self.layout.add_widget(self.btn_forward)
        self.layout.add_widget(self.btn_left)
        self.layout.add_widget(self.btn_stop)
        self.layout.add_widget(self.btn_right)
        self.layout.add_widget(self.btn_backward)
        self.layout.add_widget(self.speed_label)
        self.layout.add_widget(self.slider)
        self.layout.add_widget(self.feedback_label)
        
        # Bind buttons to methods
        self.btn_forward.bind(on_press=self.forward)
        self.btn_backward.bind(on_press=self.backward)
        self.btn_left.bind(on_press=self.left)
        self.btn_right.bind(on_press=self.right)
        self.btn_stop.bind(on_press=self.stop)
        
        # Bind window size change event for responsiveness
        Window.bind(on_resize=self.on_window_resize)
        
        self.add_widget(self.layout)
        
    def on_window_resize(self, instance, width, height):
        # Adjust positions and sizes of widgets when window size changes
        self.slider.width = width * 0.8
        self.speed_label.font_size = self.calculate_font_size(18)
        self.feedback_label.font_size = self.calculate_font_size(20)
        self.update_button_fonts()
        
    def calculate_font_size(self, base_size):
        # Example function to calculate font size based on window height
        return int(base_size * (Window.height / 800))  # Adjust 800 based on your design
    
    def update_button_fonts(self):
        # Update font size of buttons dynamically
        font_size = self.calculate_font_size(20)
        for button in [self.btn_left, self.btn_forward, self.btn_right, self.btn_backward, self.btn_stop]:
            button.font_size = f'{font_size}sp'
    
    def forward(self, instance):
        global speed, current_direction
        current_direction = 1
        self.update_speed()
        set_motor_direction(current_direction)
        self.feedback_label.text = 'Moving Forward'

    def backward(self, instance):
        global speed, current_direction
        current_direction = 2
        self.update_speed()
        set_motor_direction(current_direction)
        self.feedback_label.text = 'Moving Backward'

    def left(self, instance):
        global speed, current_direction
        current_direction = 3
        self.update_speed()
        set_motor_direction(current_direction)
        self.feedback_label.text = 'Turning Left'

    def right(self, instance):
        global speed, current_direction
        current_direction = 4
        self.update_speed()
        set_motor_direction(current_direction)
        self.feedback_label.text = 'Turning Right'

    def stop(self, instance):
        global current_direction
        current_direction = None
        motor1.write(0)
        motor2.write(0)
        self.feedback_label.text = 'Stopped'

    def on_slider_value_change(self, instance, value):
        global speed
        speed = value
        self.speed_label.text = f'Speed: {speed:.0f}'
        self.update_speed()

    def update_speed(self):
        if current_direction is not None:
            motor1.write(speed / 255.0)
            motor2.write(speed / 255.0)

class HistoryScreen(Screen):
    
    def __init__(self, **kwargs):
        super(HistoryScreen, self).__init__(**kwargs)
        self.build()

    def build(self):
        self.layout = FloatLayout()
        
        # History text input
        self.history_input = TextInput(text='History of Commands...\n', multiline=True, readonly=True, font_size=18, size_hint=(None, None), width=800, height=600)
        self.history_input.pos_hint = {'center_x': 0.5, 'center_y': 0.6}
        
        # Clear button
        self.clear_button = Button(text='Clear Logs', font_size=20, size_hint=(0.2, 0.1), width=200, height=50, pos_hint={'center_x': 0.5, 'center_y': 0.32}, bold=True)
        self.clear_button.bind(on_press=self.clear_logs)
        
        # Add widgets to layout
        self.layout.add_widget(self.history_input)
        self.layout.add_widget(self.clear_button)
        
        self.add_widget(self.layout)

        # Bind movement methods to log commands, delay it to ensure ControllerScreen is fully initialized
        Clock.schedule_once(self.delayed_bind, 0.1)

        # Bind window size change event for responsiveness
        Window.bind(on_resize=self.on_window_resize)

    def delayed_bind(self, dt):
        screen_manager = self.manager
        if screen_manager:
            controller_screen = screen_manager.get_screen('Controller')
            if controller_screen:
                movements = {
                    'Forward': self.log_command,
                    'Backward': self.log_command,
                    'Left': self.log_command,
                    'Right': self.log_command,
                    'Stop': self.log_command  # Assuming 'Stop' also needs to be logged
                }
                for movement, callback in movements.items():
                    button = getattr(controller_screen, f'btn_{movement.lower()}')
                    button.bind(on_press=lambda instance, move=movement: callback(move))
                
                # Bind speed slider change
                speed_slider = controller_screen.slider
                speed_slider.bind(value=self.log_speed_change)
        else:
            Clock.schedule_once(self.delayed_bind, 0.1)  # Retry binding after a short delay if not ready

    def log_command(self, movement):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{timestamp}] Moved {movement}"
        if self.history_input.text == 'History of Commands...\n':
            self.history_input.text = ''  # Clear initial text
        self.history_input.text += f"{message}\n"
    
    def log_speed_change(self, instance, value):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{timestamp}] Speed changed to {value:.2f}"
        if self.history_input.text == 'History of Commands...\n':
            self.history_input.text = ''  # Clear initial text
        self.history_input.text += f"{message}\n"

    def clear_logs(self, instance):
        self.history_input.text = 'History of Commands...\n'

    def on_window_resize(self, instance, width, height):
        # Adjust positions and sizes of widgets when window size changes
        self.history_input.width = width * 0.8
        self.history_input.height = height * 0.6
        self.history_input.font_size = self.calculate_font_size(18)
        self.clear_button.font_size = self.calculate_font_size(20)
    
    def calculate_font_size(self, base_size):
        # Example function to calculate font size based on window height
        return int(base_size * (Window.height / 800))  # Adjust 800 based on your design


class SettingsScreen(Screen):
    
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        self.build()

    def build(self):
        self.layout = FloatLayout()
        
        # Dark mode toggle switch
        self.dark_mode_toggle = ToggleButton(text='Toggle Theme', font_size=20, size_hint=(0.2, 0.1), width=300, height=100, bold=True)
        self.dark_mode_toggle.pos_hint = {'center_x': 0.5, 'center_y': 0.7}
        self.dark_mode_toggle.bind(on_press=self.toggle_dark_mode)
        
        # Set initial state based on current window background color
        self.update_dark_mode_button()
        
        # Exit button
        self.exit_button = Button(text='Exit', font_size=20, size_hint=(0.2, 0.1), width=300, height=100, bold=True)
        self.exit_button.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        self.exit_button.bind(on_press=self.exit_app)
        
        # Add widgets to layout
        self.layout.add_widget(self.dark_mode_toggle)
        self.layout.add_widget(self.exit_button)
        
        self.add_widget(self.layout)
    
    def toggle_dark_mode(self, instance):
        if instance.state == 'down':
            # Dark mode
            self.apply_dark_theme()
        else:
            # Light mode
            self.apply_light_theme()
    
    def apply_dark_theme(self):
        Window.clearcolor = (0.2, 0.2, 0.2, 1)
        self.update_widget_colors((1, 1, 1, 1), (0, 0, 0, 1))  # Update label and slider colors
        self.dark_mode_toggle.state = 'down'  # Update toggle button state
    
    def apply_light_theme(self):
        Window.clearcolor = (1, 1, 1, 1)
        self.update_widget_colors((0, 0, 0, 1), (1, 1, 1, 1))  # Update label and slider colors
        self.dark_mode_toggle.state = 'normal'  # Update toggle button state
    
    def update_dark_mode_button(self):
        # Check current window background color to set toggle button state
        if Window.clearcolor == (0.2, 0.2, 0.2, 1):
            self.dark_mode_toggle.state = 'down'
        else:
            self.dark_mode_toggle.state = 'normal'
    
    def update_widget_colors(self, label_color, slider_color):
        # Method to update label and slider colors
        for screen_name in ['Controller', 'History', 'Settings']:
            screen = self.manager.get_screen(screen_name)
            if screen:
                for widget in screen.walk(restrict=True):
                    if isinstance(widget, Label):
                        widget.color = label_color
                    elif isinstance(widget, Slider):
                        widget.cursor_color = slider_color
    
    def exit_app(self, instance):
        App.get_running_app().stop()
        
    def on_window_resize(self, instance, width, height):
        # Adjust positions and sizes of widgets when window size changes
        self.dark_mode_toggle.pos_hint = {'center_x': 0.5, 'center_y': 0.7}
        self.exit_button.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        
        self.update_button_fonts()
    
    def calculate_font_size(self, base_size):
        # Example function to calculate font size based on window height
        return int(base_size * (Window.height / 800))  # Adjust 800 based on your design
    
    def update_button_fonts(self):
        # Update font size of buttons dynamically
        font_size = self.calculate_font_size(20)
        for button in [self.dark_mode_toggle, self.exit_button]:
            button.font_size = f'{font_size}sp'

class MotorControlApp(App):
    def build(self):
        self.screen_manager = ScreenManager()
        
        # Create navigation bar at the bottom
        self.nav_bar = FloatLayout(size_hint=(1, None), height=100, pos_hint={'top': 1})
        
        # Define buttons for navigation bar
        button_width = 1 / 3  # Each button takes 1/3 of the width
        button_pos_x = 0
        
        self.btn_controller = Button(text='Controller', size_hint=(button_width, 1), pos_hint={'x': button_pos_x}, bold=True)
        button_pos_x += button_width
        
        self.btn_history = Button(text='History', size_hint=(button_width, 1), pos_hint={'x': button_pos_x}, bold=True)
        button_pos_x += button_width
        
        self.btn_settings = Button(text='Settings', size_hint=(button_width, 1), pos_hint={'x': button_pos_x}, bold=True)
        button_pos_x += button_width
        
        # Add buttons to navigation bar
        self.nav_bar.add_widget(self.btn_controller)
        self.nav_bar.add_widget(self.btn_history)
        self.nav_bar.add_widget(self.btn_settings)
        
        # Bind buttons to screen changes
        self.btn_controller.bind(on_press=self.switch_to_controller)
        self.btn_history.bind(on_press=self.switch_to_history)
        self.btn_settings.bind(on_press=self.switch_to_settings)
        
        # Add screens to screen manager
        self.screen_manager.add_widget(ControllerScreen(name='Controller'))
        self.screen_manager.add_widget(HistoryScreen(name='History'))
        self.screen_manager.add_widget(SettingsScreen(name='Settings'))
        
        # Create the main layout and add screen manager and nav bar
        self.main_layout = FloatLayout()
        self.main_layout.add_widget(self.screen_manager)
        self.main_layout.add_widget(self.nav_bar)
        
        return self.main_layout
    
    def switch_to_controller(self, instance):
        self.screen_manager.current = 'Controller'

    def switch_to_history(self, instance):
        self.screen_manager.current = 'History'

    def switch_to_settings(self, instance):
        self.screen_manager.current = 'Settings'

# Run the Kivy application
if __name__ == '__main__':
    MotorControlApp.title = 'Bluetooth Arduino Car Controller'
    MotorControlApp().run()