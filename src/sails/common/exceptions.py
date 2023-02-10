class MessagedException(Exception):
    """An exception with a message."""

    def __init__(self, message: str):
        """Initialize the exception with the given message.

        :param message: The message for the exception.
        :type message: str

        """
        super().__init__(f"{message}")
        self.message = message
