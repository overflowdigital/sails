import os


def get_filename(path: str) -> str:
    """
    This function returns the base name of the path specified.

    :param path: The file path.
    :type path: str
    :return: The base name of the file.
    :rtype: str
    """
    return os.path.basename(path)


def get_directory(path: str) -> str:
    """
    This function returns the directory name of the specified path.

    :param path: The file path.
    :type path: str
    :return: The directory name of the file.
    :rtype: str
    """
    return os.path.dirname(path)


def up_directory(path: str) -> str:
    """
    This function returns the parent directory of the specified path.

    :param path: The file path.
    :type path: str
    :return: The parent directory of the file.
    :rtype: str
    """
    return os.path.sep.join(path.split(os.path.sep)[:-1])


def get_extension(path: str) -> str:
    """
    This function returns the extension of the file specified in the path.

    :param path: The file path.
    :type path: str
    :return: The extension of the file.
    :rtype: str
    """
    filename: str = get_filename(path)
    return os.path.splitext(filename)[1]


def get_filename_no_extension(path: str) -> str:
    """
    This function returns the base name of the file without the extension.

    :param path: The file path.
    :type path: str
    :return: The base name of the file without the extension.
    :rtype: str
    """
    filename: str = get_filename(path)
    return os.path.splitext(filename)[0]


def get_drive(path: str) -> str:
    """
    This function returns the drive letter or root directory of the specified path (if POSIX).

    :param path: The file path.
    :type path: str
    :return: The drive letter or root directory of the path.
    :rtype: str
    """
    return os.path.splitdrive(path)[0] or "/"
