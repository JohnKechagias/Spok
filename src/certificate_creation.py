from functools import partial
from pathlib import Path
from time import sleep

import multiprocessing as mp
import threading
from typing import Any, Tuple, Callable, List, Optional

from PIL import Image, ImageDraw, ImageFont
from widgets.constants import *
import ttkbootstrap as ttk



class CertificateCreator:
    """ Used in creating certificates. Can also log actions. """
    def __init__(
        self,
        image_path: str,
        output_folder_path: str,
        font: ImageFont.FreeTypeFont,
        font_color: Tuple[int, int, int],
        image_coords: Tuple[int, int],
        word_position: str,
        compress_level: int,
        log_func,
        num_of_processes: int = mp.cpu_count() - 1
    ) -> None:
        self.num_of_processes = num_of_processes
        self.image = Image.open(image_path)
        self.output_folder_path = output_folder_path
        self.font = font
        self.font_color = font_color
        self.coords = image_coords
        if word_position == MIDDLE:
            self.anchor = 'ms'
            self.align = 'middle'
        elif word_position == LEFT:
            self.anchor = 'ls'
            self.align = 'left'
        elif word_position == RIGHT:
            self.anchor = 'rs'
            self.align = 'right'
        self.compress_level = compress_level
        self.log_func = log_func

    def create_certificates_from_list(
        self,
        lock: threading.Lock,
        progress_var: ttk.IntVar,
        user_list: List[User],
        cleanup_func: Optional[Callable[[], Any]] = None
    ):
        """ Creates a certificate for each user in the `user_list`.

        Args:
            lock: A threading lock.
            progress_var: An IntVar that represents the amount of certificates done.
                The IntVar is linked to a progressbar.
            user_list: The list of Users.
            cleanup_func: The cleanup func is optional and if given, will be run
                at the end, after all the certificates have been created.
        """

        func = partial(
            CertificateCreator.create_certificate,
            self.image,
            self.coords,
            self.font,
            self.font_color,
            self.anchor,
            self.align,
            self.compress_level
        )

        pool = mp.Pool(processes=self.num_of_processes)
        log_list = pool.imap(
            func,
            user_list,
            chunksize=15
        )

        for log in log_list:
            lock.acquire()
            progress_var.set(progress_var.get() + 1)
            self.log(log)
            lock.release()
        pool.close()
        pool.join()

        if cleanup_func is not None:
            sleep(0.5)
            cleanup_func()

    @staticmethod
    def create_certificate(
        image: Image.Image,
        coords: Tuple[int, int],
        font: ImageFont.FreeTypeFont,
        font_color: Tuple[int, int, int],
        anchor: str,
        align: str,
        compress_level: int,
        user: User
    ) -> User:
        """ Creates a certificate. For more information about `anchor` and `align`
        visit https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html.

        Args:
            image: The image draw on.
            coords: The image coords to start drawing on.
            font: The font to use.
            font_color: The font color to use.
            anchor: The text anchor. For more information visit
            align: The text alignment.
            compress_level: The level of png compression to use.
                Compression levels range from 0 to 9.
            user: The user that the certificate will be based on.
                user is (user_index, user_email, user_name).

        Returns:
            The passed `user`. This is done for logging purposes.
        """
        # NEED to have a temp copy of image, else the base template
        # is going to get replaced!!
        # Draw the message on the background
        image_copy = image.copy()
        draw = ImageDraw.Draw(image_copy)
        draw.text(
            coords,
            user[1],
            fill=font_color,
            font=font,
            anchor=anchor,
            align=align
        )
        # Save the edited image
        name = user[1].replace(' ', '_')
        image_name = f'{name}.{image.format}'
        image_location = Path('certificates') / image_name
        image_copy.save(image_location, format='png', compress_level=compress_level)
        return user

    def log(self, entry_info):
        self.log_func('Created Certificate', '{}. name: {} | email: {}'
            .format(entry_info[0], entry_info[1], entry_info[2]), LogLevel.WARNING)
