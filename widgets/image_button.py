import tkinter as tk



class ImageButton(tk.Button):
    def __init__(
        self,
        master,
        default_image: tk.PhotoImage,
        hover_image: tk.PhotoImage,
        active_image: tk.PhotoImage = None,
        background: str = '#ffffff',
        *args,
        **kwargs
        ) -> None:
        super().__init__(
            master=master,
            image=default_image,
            *args,
            autostyle=False,
            border=0,
            borderwidth=0,
            highlightthickness=0,
            background=background,
            activebackground=background,
            **kwargs
        )

        self.default_image = default_image
        self.hover_image = hover_image

        if active_image is None:
            self.active_image = self.hover_image
        else:
            self.active_image = active_image

        super().bind('<Enter>', self.enter)
        super().bind('<Leave>', self.leave)
        super().bind('<Button>', self.button)
        super().bind('<ButtonRelease>', self.button_release)

    def enter(self, event: tk.Event):
        super().configure(image=self.hover_image)

    def leave(self, event: tk.Event):
        super().configure(image=self.default_image)

    def button(self, event: tk.Event):
        super().configure(image=self.active_image)

    def button_release(self, event: tk.Event):
        super().configure(image=self.hover_image)