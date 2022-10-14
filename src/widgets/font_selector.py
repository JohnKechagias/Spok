import tkinter as tk
from tkinter.font import ROMAN, Font
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from widgets.color_selector import ColorSelector
from widgets.cmeter import CMeter
from widgets.constants import RGB, Hex



class FontSelector(ttk.Labelframe):
    def __init__(
        self,
        master: tk.Misc,
        font_families: list[str],
        font: ttk.font.Font | None = None,
        color: RGB | Hex | None = None,
        *args,
        **kwargs
    ) -> None:
        super().__init__(
            master,
            text='Font Configuration',
            padding=10,
            *args,
            **kwargs
        )
        super().columnconfigure(0, weight=1)
        super().rowconfigure(9, weight=1)

        self.preview_font_size = 12

        if font is None:
            font = ttk.font.Font(
                name='default_font',
                exists=False,
                family=font_families[0],
                size=self.preview_font_size,
                weight=NORMAL,
                slant=ROMAN,
                underline=False,
                overstrike=False
            )
        self._font = font

        self._family = ttk.StringVar(value=font.cget('family'))
        self._size = ttk.IntVar(value=font.cget('size'))
        self._weight = ttk.Variable(value=font.cget('weight'))
        self._slant = ttk.Variable(value=font.cget('slant'))

        self._family.trace_add('write', self._update_font_preview)
        self._size.trace_add('write', self._update_font_preview)
        self._weight.trace_add('write', self._update_font_preview)
        self._slant.trace_add('write', self._update_font_preview)

        # =-=-=-=-=-=- Colors Options -=-=-=-=-=--=-=

        self.color_Label = ttk.Label(
            master=self,
            text='Font Color',
            bootstyle=(INVERSE, SECONDARY),
            anchor=CENTER,
            font='-weight bold'
        )
        self.color_Label.grid(row=1, column=0, sticky=EW, pady=6)

        self.color_selector = ColorSelector(master=self)
        self.color_selector.grid(row=2, column=0, sticky=EW)

        if color is not None:
            self.color = color

        # =-=-=-=-=-=- Family Options -=-=-=-=-=--=-=

        self.family_label = ttk.Label(
            master=self,
            font='-weight bold',
            text='Font Family'
        )
        self.family_label.grid(row=3, column=0, sticky=EW)

        self.font_families = font_families
        self.font_family_combobox= ttk.Combobox(
            master=self,
            bootstyle=(LIGHT),
            state=READONLY,
            textvariable=self._family,
            values=self.font_families
        )
        self.font_family_combobox.current(0)
        self.font_family_combobox.grid(row=4, column=0, sticky=EW, pady=6)

        # =-=-=-=-=-=- Weight Options -=-=-=-=-=--=-=

        self.weight_frame = ttk.LabelFrame(
            self,
            text='Weight',
            padding=5
        )
        self.weight_frame.grid(row=5, column=0, sticky=EW, pady=5)

        self.weight_normal = ttk.Radiobutton(
            self.weight_frame,
            bootstyle=WARNING,
            text='Normal',
            variable=self._weight,
            value='normal'
        )
        self.weight_normal.grid(row=0, column=0, padx=(0, 30), sticky=EW)

        self.weight_bold = ttk.Radiobutton(
            self.weight_frame,
            bootstyle=WARNING,
            text='Bold',
            variable=self._weight,
            value='bold'
        )
        self.weight_bold.grid(row=0, column=1, sticky=EW)

        # =-=-=-=-=-=- Slant Options -=-=-=-=-=--=-=

        self.slant_frame = ttk.Labelframe(
            self,
            text='Slant',
            padding=5
        )
        self.slant_frame.grid(row=6, column=0, sticky=EW, pady=5)

        self.slant_roman = ttk.Radiobutton(
            self.slant_frame,
            bootstyle=WARNING,
            text='Roman',
            variable=self._slant,
            value='roman'
        )
        self.slant_roman.grid(row=0, column=0, padx=(0, 30), sticky=EW)

        self.slant_italic = ttk.Radiobutton(
            self.slant_frame,
            bootstyle=WARNING,
            text='Italic',
            variable=self._slant,
            value='italic'
        )
        self.slant_italic.grid(row=0, column=1, sticky=EW)

        # =-=-=-=-=-=- Size Options -=-=-=-=-=--=-=

        self.font_size_selector = CMeter(
            master=self,
            bootstyle=WARNING,
            maxfontsize=60,
            variable=self._size
        )
        self.font_size_selector.grid(row=7, column=0, sticky=EW, pady=6)

        # =-=-=-=-=-=- Preview Text -=-=-=-=-=--=-=

        self.preview_text_label = ttk.Label(
            master=self,
            font='-weight bold',
            text='Preview'
        )
        self.preview_text_label.grid(row=8, column=0, sticky=EW)

        preview_font = self._font.copy()
        preview_font.configure(size=self.preview_font_size)
        self.preview_text = ttk.Text(
            self,
            width=18,
            font=preview_font
        )
        self.preview_text.grid(row=9, column=0, sticky=EW, pady=(6, 0))
        self.preview_text.insert(END, 'Name Surname')

    @property
    def color(self) -> Hex:
        return self.color_selector.get_color_HEX()

    @color.setter
    def color(self, value: RGB | Hex):
        self.color_selector.set_color(value)

    @property
    def font(self) -> Font:
        return self._font

    @font.setter
    def font(self, value: Font):
        self._font = value
        self._family.set(value.cget('family'))
        self._size.set(value.cget('size'))
        self._weight.set(value.cget('weight'))
        self._slant.set(value.cget('slant'))


    def _update_font_preview(self, *_):
        family = self._family.get()
        size = self._size.get()
        weight = self._weight.get()
        slant = self._slant.get()

        self._font.config(
            family=family,
            size=size,
            weight=weight,
            slant=slant
        )
        try:
            preview_font = self._font.copy()
            preview_font.configure(size=self.preview_font_size)
            self.preview_text.configure(font=preview_font)
        except:
            pass
