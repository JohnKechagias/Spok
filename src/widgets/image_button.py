import tkinter as tk
from typing import Optional

from assets_manager import ICONS
from .constants import *



class ImageButton(tk.Button):
    def __init__(
        self,
        master: tk.Widget,
        codename: Optional[str] = None,
        default_image: Optional[tk.PhotoImage] = None,
        active_image: Optional[tk.PhotoImage] = None,
        hover_image: Optional[tk.PhotoImage] = None,
        background: Hex = THEME['bg'],
        *args,
        **kwargs
    ) -> None:
        """ Constructor.

        Args:
            master: Parent widget.
            codename: Can be used to identify the image family
                and select the proper default_image, hover_image and
                active_image. An images (tk.PhotoImage) codename is
                the image name without the part that denotes the images
                use. ex. The codename of the image `background-active`
                is `background`. The codename of the image `add-hover`
                is `add`. `If we don't supply the image codename we
                have to supply the individual images`.
            default_image: The image to be used when the button is in
                its default state.
            hover_image The image to be used when the user is hovering
                over the button.
            active_image The image to be used when to user clicks the
                button.
            background: The buttons background color.
        """
        if codename is not None:
            default_image = codename + '-default'
            active_image = codename + '-active'
            hover_image = codename + '-hover'

        super().__init__(
            master=master,
            image=default_image,
            autostyle=False,
            border=0,
            borderwidth=0,
            highlightthickness=0,
            background=background,
            activebackground=background,
            *args,
            **kwargs
        )

        self.default_image = default_image
        self.active_image = active_image
        self.hover_image = hover_image

        if hover_image not in ICONS:
            self.hover_image = self.active_image

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
