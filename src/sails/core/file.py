import os
from dataclasses import dataclass
from types import TracebackType
from typing import IO, Callable, Generic, Optional, Type, Union, cast

from sails.common.exceptions import MessagedException
from sails.common.typing import T
from sails.core.crypto import Secret, Encrypt
from sails.core.retry import Retry


@dataclass
class Options:
    """A class to represent the options for file opening.

    :param mode: The mode in which the file should be opened (read, write, etc.).
    :type mode: str
    :param encoding: The encoding to use when reading or writing the file (optional).
    :type encoding: Optional[str]
    :param newline: The newline character to use when writing the file (optional).
    :type newline: Optional[str]
    """

    mode: str
    encoding: Optional[str] = None
    newline: Optional[str] = None


class FileNotFoundError(MessagedException):
    """An exception to be raised when a file is not found.

    :param message: The error message to be displayed.
    :type message: str
    """

    def __init__(self, message: str):
        """Create a new instance of the `FileNotFoundError` exception.

        :param message: The error message to be displayed.
        :type message: str
        """
        super().__init__(message)


class EncryptedFileWriter:
    """A context manager for writing encrypted messages to a file.

    :param path: The file path to write to.
    :type path: str
    :param secret: The secret used to encrypt the messages.
    :type secret: Secret
    """

    def __init__(self, path: str, secret: Secret) -> None:
        """Initialize the EncryptedFileWriter object."""
        self.path: str = path
        self.secret: Secret = secret
        self.buffer: list[bytes] = []

    def __enter__(self) -> bool:
        """Enter the context."""
        return True

    def write(self, message: str) -> None:
        """Write an encrypted message to the buffer.

        :param message: The message to write.
        :type message: str
        """
        encrypted_message: bytes = Encrypt.write(message + "\n", self.secret)
        self.buffer.append(encrypted_message)

    def commit(self) -> bool:
        """Write the encrypted messages in the buffer to the file.

        :return: True if the writing was successful, False otherwise.
        :rtype: bool
        """
        with open(self.path, "wb") as handle:
            for line_number, line in enumerate(self.buffer):
                handle.write(line)
                self.buffer[line_number] = "0" * len(line)

    def __exit__(
        self,
        exc_type: Optional[BaseException],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit the context."""
        del buffer
        del secret


class EncryptedFileReader:
    """
    EncryptedFileReader is a class that reads an encrypted file and provides a decrypted version of the content.

    :param path: The path to the encrypted file
    :type path: str
    :param secret: The secret used to encrypt the file
    :type secret: Secret
    """

    def __init__(self, path: str, secret: Secret) -> None:
        """
        The constructor of the EncryptedFileReader class.

        :param path: The path to the encrypted file
        :type path: str
        :param secret: The secret used to encrypt the file
        :type secret: Secret
        """
        self.path: str = path
        self.secret: Secret = secret
        self.buffer: list[str] = []

    def __enter__(self) -> bool:
        """
        Enter the runtime context for the EncryptedFileReader object.

        :return: True if the file at the specified path exists, False otherwise.
        :rtype: bool
        """
        return os.path.exists(self.path)

    def read(self) -> list[str]:
        """
        Read the encrypted file and provide a decrypted version of its content.

        :return: A list of decrypted strings, where each string corresponds to a line in the encrypted file.
        :rtype: list[str]
        """
        with open(self.path, "rb") as handle:
            for line in handle.readlines():
                decrypted_message: str = Encrypt.read(line, self.secret).decode()
                self.buffer.append(decrypted_message.rstrip("\n"))

            return self.buffer

    def __exit__(
        self,
        exc_type: Optional[BaseException],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """
        Exit the runtime context for the EncryptedFileReader object.

        :param exc_type: The type of exception that was raised, if any
        :type exc_type: Optional[BaseException]
        :param exc_val: The value of the exception that was raised, if any
        :type exc_val: Optional[BaseException]
        :param exc_tb: The traceback of the exception that was raised, if any
        :type exc_tb: Optional[TracebackType]
        """
        del self.buffer
        del self.secret


class ObservedFile(Generic[T]):
    """A class for observing changes to a file and parsing its contents

    :param path: path to the file to be observed
    :param parser: callable that takes a file handle and returns the desired data type
    :param timeout: maximum amount of time to wait for the file to exist, default is 0.0
    :param binary: whether the file should be opened in binary mode, default is False
    :param encoding: encoding of the file, default is 'utf-8'
    :param newline: newline character(s) to use when reading the file, default is '\n'
    :param backoff: time to wait between retries when the file is not found, default is 0.01
    """

    def __init__(
        self,
        path: str,
        parser: Callable[[IO], T],
        timeout: float = 0.0,
        binary: bool = False,
        encoding: str = "utf-8",
        newline: str = "\n",
        backoff: float = 0.01,
    ) -> None:
        """Initialize the ObservedFile object"""
        if binary:
            encoding = None
            newline = None

        self.path: str = path
        self.parser: Callable[[IO], T] = parser
        self.modified_time: float = 0.0
        self.data: Union[T, Type[None]] = None
        self.backoff: float = backoff
        self.options: Options = Options("rb" if binary else "r", encoding, newline)

        if timeout:
            last_error: Optional[FileNotFoundError] = None

            for _ in Retry(time=timeout, backoff=backoff):
                if self.data:
                    break
                try:
                    self.get_data()
                except FileNotFoundError as e:
                    last_error = e
                else:
                    break
        else:
            last_error = cast(FileNotFoundError, last_error)
            raise FileNotFoundError(
                f"Timed out trying to find {self.path}, likely file does not exist"
            )

    def get_data(self) -> T:
        """Get the parsed data of the observed file.

        :returns: The parsed data of the observed file.
        """
        return self.get_data_and_modified_time()[0]

    def get_modified_time(self) -> float:
        """Get the modified time of the observed file.

        :returns: The modified time of the observed file.
        """
        return self.get_data_and_modified_time()[1]

    def get_data_and_modified_time(self) -> tuple[T, float]:
        """Get the parsed data and modified time of the observed file.

        :returns: A tuple of the parsed data and modified time of the observed file.
        """
        try:
            modified_time = os.path.getmtime(self.path)
        except OSError as e:
            if not self.data:
                raise FileNotFoundError(
                    f"Timed out trying to find {self.path}, likely file does not exist"
                )
            return cast(T, self.data), self.modified_time

        if self.modified_time < modified_time:
            try:
                with open(self.path, **self.options.__dict__) as file:
                    self.data = self.parser(file)
            except Exception as e:
                if not self.data:
                    raise FileNotFoundError(
                        f"Timed out trying to find {self.path}, likely file does not exist"
                    ) from e

            self.modified_time = modified_time

        return cast(T, self.data), self.modified_time
