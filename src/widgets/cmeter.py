import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *



class CMeter(ttk.Meter):
    def __init__(
        self,
        master: tk.Misc,
        fontsize: int = 25,
        maxfontsize: int = 50,
        text: str = 'Value',
        variable: ttk.IntVar | None = None,
        *args,
        **kwargs
    ) -> None:
        super().__init__(
            master=master,
            amounttotal=maxfontsize,
            metersize=150,
            amountused=fontsize,
            stripethickness=8,
            subtext=text,
            interactive=False,
            *args,
            **kwargs
        )

        if variable is not None:
            self.variable = variable
            self.amountusedvar.set(variable.get())
            self.amountusedvar.trace_add('write',
                lambda *_: self.variable.set(self.amountusedvar.get()))

        # Get label child of meter widget
        meter_child = self.winfo_children()[0].winfo_children()[0]
        meter_child.bind('<Button-5>', self._wheelScroll) # Linux, wheel scroll down
        meter_child.bind('<Button-4>', self._wheelScroll)  # Linux, wheel scroll up
        meter_child.bind('<MouseWheel>', self._wheelScroll) # Windows wheel scroll keybind

    @property
    def value(self):
        return self.amountusedvar.get()

    @value.setter
    def value(self, value: int):
        self.amountusedvar.set(value)

    def _increment_meter(self):
        new_value = self.amountusedvar.get() + 1
        # Make sure new value isn't out of bounds
        if new_value <= self.amounttotalvar.get():
            self.configure(amountused=new_value)

    def _decrement_meter(self):
        new_value = self.amountusedvar.get() - 1
        # Make sure new value isn't out of bounds
        if new_value >= 0:
            self.configure(amountused=new_value)

    def _wheelScroll(self, event: tk.Event):
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 4 or event.delta == 120: # Scroll up
            self._increment_meter()
        if event.num == 5 or event.delta == -120: # Scroll down
            self._decrement_meter()
