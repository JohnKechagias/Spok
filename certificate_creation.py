from functools import partial
from time import sleep

import multiprocessing as mp
import threading

from PIL import Image, ImageDraw
from widgets.constants import *
from ttkbootstrap import IntVar



NUMBER_OF_PROCESSES = mp.cpu_count() - 1


class CertificateCreator:
    """Class used in creating certificates. Can also log actions."""
    def __init__(
        self,
        image_path:str,
        output_folder_path:str,
        font,
        font_color:tuple,
        image_coords:tuple,
        word_position:str,
        compress_level:int,
        log_func
        ) -> None:
        """
        Create a CertificateCreator instanse
        """
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
        lock:threading.Lock,
        progress_var:IntVar,
        item_list:list,
        cleanup_func=None
        ) -> list:
        """Create a certificate for each item in a list

        Args:
            Each item is a tuple (item_index, name, email)

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

        pool = mp.Pool(processes=NUMBER_OF_PROCESSES)
        log_list = pool.imap(
            func,
            item_list,
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
        image:Image.Image,
        coords:tuple,
        font,
        font_color:tuple,
        anchor:str,
        align:str,
        compress_level:int,
        entry_info:tuple
        ) -> None:
        # NEED to have a temp copy of image, else the base template
        # is going to get replaced!!
        # draw the message on the background
        image_copy = image.copy()
        draw = ImageDraw.Draw(image_copy)
        draw.text(
            coords,
            entry_info[1],
            fill=font_color,
            font=font,
            anchor=anchor,
            align=align
        )
        # save the edited image
        name = entry_info[1].replace(' ', '_')
        image_name = f'{name}.png'
        image_location = f'certificates/{image_name}'
        image_copy.save(image_location, format='png', compress_level=compress_level)
        return entry_info

    def log(self, entry_info):
        self.log_func('Created Certificate', '{}. name: {} | email: {}'
            .format(entry_info[0], entry_info[1], entry_info[2]), LogLevel.WARNING)
