from django.core.exceptions import ValidationError


def max_file_size(megabyte_limit):
    def _max_file_size(file_fild):
        print(file_fild.size)
        filesize = file_fild.size
        if filesize > megabyte_limit * 1024 * 1024:
            raise ValidationError(f"Max file size is {megabyte_limit}MB ({filesize}MB provided)")
    return _max_file_size
