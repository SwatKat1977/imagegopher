"""
This source file is part of Image Gopher
For the latest info, see https://github.com/SwatKat1977/imagegopher

Copyright 2024 Image Gopher Development Team

This program is free software : you can redistribute it and /or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.If not, see < https://www.gnu.org/licenses/>.
"""
import hashlib
import logging
import os
import time
from PIL import Image

class FileGatherer:
    """ Class that manages gathering a list of fils to import """
    __slots__ = ["_document_root", "_logger"]

    @property
    def document_root(self) -> str:
        """
        Get the document root string.

        returns:
            Document root.
        """
        return self._document_root

    @document_root.setter
    def document_root(self, value : str):
        self._document_root = value

    def __init__(self, logger : logging.Logger, document_root : str) -> None:
        self._document_root = document_root
        self._logger = logger.getChild(__name__)

    def gather_images(self) -> dict:
        """
        Walk the docoment root and create a dictionary of any file that is a
        valid image file, along with it's name gennerate a hash.

        returns:
            The return for this method is a dictionary, where the key is path
            and the value is a list of tuples containning filename, hash and
            scan time.
        """
        images_list = {}

        for subdir, _, files in os.walk(self._document_root):
            images_list[subdir] = []

            for file in files:
                filename = os.path.join(subdir, file)

                if self._is_file_readable(filename) and self._is_image(filename):
                    file_hash = self._generate_file_hash(filename)
                    self._logger.debug(
                        "File Gatherer detected image: '%s' with hash '%s'",
                        filename, file_hash)
                    scan_time = int(round(time.time() * 1000))
                    entry = (file, file_hash, scan_time)
                    images_list[subdir].append(entry)

            if not images_list[subdir]:
                del images_list[subdir]

        return images_list

    def _is_image(self, filename : str) -> bool:
        """
        Check to see if the file has been detected as an image type.

        parameters:
            file: File name with path

        returns:
            bool - True if an image, otherwise false is returned
        """
        try:
            with Image.open(filename) as img:
                img.verify()
                return True

        except (IOError, SyntaxError):
            return False

    def _generate_file_hash(self, filename : str) -> str:
        md5_object = hashlib.md5()
        block_size = 128 * md5_object.block_size

        with open(filename, 'rb') as file_handle:
            chunk = file_handle.read(block_size)
            while chunk:
                md5_object.update(chunk)
                chunk = file_handle.read(block_size)

        return md5_object.hexdigest()

    def _is_file_readable(self, filename : str) -> bool:
        readable = False

        try:
            with open(filename, "r+", encoding="utf-8") as _:
                readable = True

        except IOError:
            pass

        return readable
