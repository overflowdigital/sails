import os
import platform


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


def set_windows_file_hidden(file: str) -> bool:
    """Set the hidden attribute for a file on Windows.

    :param file: The file to set as hidden.
    :type file: str
    :return: True if the file was set as hidden, False otherwise.
    :rtype: bool

    :raises ctypes.WinError: If the file cannot be set as hidden.
    """
    if "windows" in platform.system().lower():
        import ctypes

        ctypes.windll.kernel32.SetFileAttributesW.argtypes = (
            ctypes.c_wchar_p,
            ctypes.c_uint32,
        )
        ret: int = ctypes.windll.kernel32.SetFileAttributesW(file, 0x02)

        if not ret:
            raise ctypes.WinError()

        return True
    return False
