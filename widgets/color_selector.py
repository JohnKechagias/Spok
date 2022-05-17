from functools import partial
import clipboard

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *



class ColorSelector(ttk.Frame):
    def __init__(self, master=None, color: tuple[int, int, int] = None):
        super().__init__(master)

        if color is None:
            color = (75, 75, 75)

        self.color = {'red': {}, 'green': {}, 'blue': {}}
        self.color['red']['style'] = DANGER
        self.color['green']['style'] = SUCCESS
        self.color['blue']['style'] = DEFAULT

        # Theshold that dictates the color of the colored button
        # foreground. Whem the button bg is dark, the fg is white
        # and when the bg is bright, the fg is black
        self.foreground_threshold = 300

        # Is used to lock and unlock event handlers like a mutex
        self.update_in_progress = False

        for i, (channel_name, channel) in enumerate(self.color.items()):
            channel['value'] = tk.IntVar(value=color[i])

            channel['frame'] = ttk.Frame(master=self)
            channel['frame'].pack(fill=X, expand=YES, pady=3)

            channel['entry'] = ttk.Entry(master=channel['frame'],
                width=3,
                textvariable=channel['value']
            )
            channel['entry'].pack(side=LEFT)

            channel['scale'] = ttk.Scale(
                master=channel['frame'],
                orient=HORIZONTAL,
                bootstyle=channel['style'],
                variable=channel['value'],
                value=75, to=255
            )
            channel['scale'].pack(side=RIGHT, fill=X, expand=YES, padx=6, pady=6)

            channel['value'].trace_add('write',
                partial(self.update_color_value, channel_name))
            channel['entry'].bind('<Any-KeyPress>',
                partial(self._keys_pressed, channel['value']), add='+')

        colored_button_frame = ttk.Frame(master=self, border=3, bootstyle=DARK)
        colored_button_frame.pack(fill=BOTH, expand=YES, pady=10)

        self.colored_button = tk.Button(
            master=colored_button_frame,
            autostyle=False,
            foreground='white',
            activeforeground='white',
            background=self.get_color_code(),
            activebackground=self.get_color_code(),
            text=self.get_color_code(),
            bd=0,
            highlightthickness=0
        )
        self.colored_button.pack(side=TOP, expand=YES, fill=X)
        self.colored_button.bind('<Button-1>', self._colored_button_clicked, add='+')

    @staticmethod
    def from_RGB(rgb: tuple[int, int, int]) -> str:
        """translates an rgb tuple of int to a tkinter friendly color code"""
        r, g, b = rgb
        return f'#{r:02x}{g:02x}{b:02x}'

    def update_color_value(self, color: str, *_):
        # Normalize and update color value
        if self.update_in_progress == True: return
        try:
            temp_value = self.color[color]['value'].get()
        except:
            return

        # aquire lock
        self.update_in_progress = True
        # Round the float value
        self.color[color]['value'].set(round(temp_value))
        self.update_button_bg()
        # release lock
        self.update_in_progress = False

    def update_button_bg(self):
        """Set button background to be the same as the color that the
        user has selected"""
        # Sum of RGB channel values
        sum_of_color_values = sum(self.get_color_tuple())
        color_code = self.get_color_code()

        if sum_of_color_values > self.foreground_threshold:
            self.colored_button.configure(
                foreground='black',
                activeforeground='black'
            )
        else:
            self.colored_button.configure(
                foreground='white',
                activeforeground='white'
            )
        self.colored_button.configure(
            background=color_code,
            activebackground=color_code,
            text=color_code
        )

    def get_color_tuple(self) -> tuple[str, str, str]:
        return (i['value'].get() for i in self.color.values())

    def get_color_code(self) -> str:
        color_RGB_tuple = self.get_color_tuple()
        return self.from_RGB(color_RGB_tuple)

    def set_color(self, color: tuple[int, int, int] | str):
        if isinstance(color, str):
            color = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))

        for i, channel in enumerate(self.color.values()):
            channel['value'].set(color[i])

    def _keys_pressed(top_widget, entry_text_var, event: tk.Event):
        min_value = 0
        max_value = 255

        if event.keysym == 'Right':
            # Check if the cursor is in the end of the word
            # (don't want to fire the event if the user just wants
            # to move the cursor)
            if event.widget.index(INSERT) == len(str(entry_text_var.get())):
                value = entry_text_var.get() + 1
                if value <= max_value:
                    entry_text_var.set(value)
        elif event.keysym == 'Left':
            # Check if the cursor is at the start of the word
            # (don't want to fire the event if the user just wants
            # to move the cursor)
            if event.widget.index(INSERT) == 0:
                value = entry_text_var.get() - 1
                if value >= min_value:
                    entry_text_var.set(value)

    def _colored_button_clicked(self, *args):
        clipboard.copy(self.get_color_code())