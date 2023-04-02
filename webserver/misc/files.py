import uuid

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

from pathlib import Path


@deconstructible
class PathAndRename:
    def __init__(self, path):
        self.path = Path(path)

    def __call__(self, instance, filename):
        ext = Path(filename).suffix
        name = uuid.uuid4().hex
        return str(Path(self.path, f"{name}{ext}"))


def max_file_size(megabyte_limit):
    def _max_file_size(file_fild):
        filesize = file_fild.size
        if filesize > megabyte_limit * 1024 * 1024:
            raise ValidationError(f"Max file size is {megabyte_limit}MB ({filesize}MB provided)")
    return _max_file_size
