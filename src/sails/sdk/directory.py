import os
from typing import TypedDict

from sails.core.path import set_windows_file_hidden

FOLDER_NAME: str = ".overflow/sails/"


class ListResult(TypedDict):
    """
    This class represents the result of a list operation.

    :param files: A list of file names in the folder.
    :param subfolders: A list of subfolder names in the folder.
    """

    files: list[str]
    subfolders: list[str]


class SDKDirectory:
    """The `SDKDirectory` class provides functionality to manage the directory structure for the Sails SDK.

    This class is used to create a root directory for the Sails SDK if it does not exist. It also provides functionality
    to list the files and subdirectories within a specified directory and to generate a file name in the Sails SDK directory structure.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the `SDKDirectory` class.

        This constructor creates the root directory for the Sails SDK if it does not exist and sets it as hidden if the operating system is Windows.
        """
        self.folder = os.path.join(os.path.expanduser(), FOLDER_NAME)

        if not os.path.exists(self.folder):
            os.mkdir(self.folder)
            set_windows_file_hidden(self.folder)

    def list_files(self, subfolder: str = "") -> ListResult:
        """Lists the files and subdirectories within the specified SDK subfolder.

        :param subfolder: the subfolder to list files and subfolders from.
        :type subfolder: str, optional
        :return: a dictionary containing a list of files and a list of subfolders.
        :rtype: ListResult
        """
        folder: str = os.path.join(self.folder, subfolder)
        listdir: list[str] = os.listdir(folder)

        files: list[str] = [item for item in listdir if os.path.isfile(item)]
        folders: list[str] = [item for item in listdir if os.path.isdir(item)]

        return ListResult(files, folders)

    def get_file_name(self, file: str) -> str:
        """Generates a file name in the Sails SDK directory structure.

        :param file: the name of the file.
        :type file: str
        :return: the full file name.
        :rtype: str
        """
        return os.path.join(self.folder, file)
