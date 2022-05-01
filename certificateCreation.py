import concurrent.futures

from ttkbootstrap import font
from PIL import Image, ImageDraw, ImageFont

from widgets.constants import *



class CertificateCreator:
    """Class used in creating certificates. Can also log actions.
    """
    def __init__(
        self,
        image_path:str,
        output_folder_path:str,
        font:font.Font,
        font_color:tuple,
        image_coords:tuple,
        word_position:str,
        logging:bool,
        log_func
        ) -> None:
        """
        Create a CertificateCreator instanse
        """
        self.image = Image.open(image_path)
        self.output_folder_path = output_folder_path
        self.font = font
        self.font_color = font_color
        self.font_truetype = ImageFont.truetype('fonts/roboto-Regular.ttf',
            self.font.cget('size'))
        # starting position of the message
        self.coords = image_coords
        self.logging = logging
        self.log = log_func
        # list where are the certificate_creation output is stored
        self._info_list = []

        if word_position == MIDDLE:
            self.anchor = 'ms'
            self.align = 'middle'
        elif word_position == LEFT:
            self.anchor = 'ls'
            self.align = 'left'
        elif word_position == RIGHT:
            self.anchor = 'rs'
            self.align = 'right'

    def create_certificates_from_list(self, item_list:list|tuple) -> list:
        """create multiple certificates for each item in a list

        Args:
            Each item inside `items` is a tuple with
            3 elements, (item_index, name, email)

        Return a list where each entry is (item_index, filename, email)
        """
        # reset info list
        self._info_list.clear()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(self._create_certificate, item_list)

        #return self._info_list

    def _create_certificate(self, entry_info:tuple) -> None:
        # NEED to have a temp copy of image, else the base template
        # is going to get replaced!!
        temp = self.image.copy()
        # draw the message on the background
        draw = ImageDraw.Draw(temp)
        draw.text(
            self.coords,
            entry_info[1],
            fill=self.font_color,
            font=self.font_truetype,
            anchor=self.anchor,
            align=self.align
        )
        # save the edited image
        name = entry_info[1].replace(' ', '_')
        image_name = f'{name}.png'
        image_location = f'{self.output_folder_path}/{image_name}'
        temp.save(image_location, optimize=True)

        if self.logging:
            self.log('<<Created Certificate>>:: {}. name: {} | email: {}'
                .format(entry_info[0], image_name, entry_info[2]), LogLevel.WARNING)

        self._info_list.append((entry_info[0], image_name, entry_info[2]))
