import base64
import binascii
from dataclasses import dataclass
from datetime import timedelta
import hashlib
import hmac
import struct
import time
from typing import Type
from cryptography.fernet import Fernet

from sails.common.exceptions import MessagedException


BYTE_FORMAT = struct.Struct("<BxxI")
"""The format of a signature header in bytes.

:type: `struct.Struct`
"""

VERSION = 1
"""The current version number of the signature header.

:type: int
"""


@dataclass
class SignatureHeader:
    """Class representing the header of a signature.

    :param version: The version number of the signature header.
    :type version: int
    :param expiry: The number of seconds after which the signature will expire.
    :type expiry: int
    """

    version: int
    expiry: int


@dataclass
class Secret:
    """Class representing a secret.

    :param data: The data of the secret.
    :type data: bytes
    """

    data: bytes


SignedSecret: Type[bytes] = bytes
"""A type alias for bytes representing a signed secret.

:type: `Type[bytes]`
"""


class SignatureError(MessagedException):
    """Exception raised when a signature error occurs.

    :param message: The error message to be raised.
    :type message: str
    """

    def __init__(self, message: str):
        """Initialize the SignatureError exception.

        :param message: The error message to be raised.
        :type message: str
        """
        super().__init__(message)


class Signature:
    @staticmethod
    def sign(secret: Secret, message: str, max_age: timedelta) -> SignedSecret:
        """Sign a message using a secret and a maximum age.

        :param secret: The secret to use for signing the message.
        :type secret: `Secret`
        :param message: The message to sign.
        :type message: str
        :param max_age: The maximum age of the signature.
        :type max_age: `timedelta`
        :return: The signed secret.
        :rtype: `SignedSecret`
        """
        expiry: int = int(time.time() + max_age.total_seconds())
        header: bytes = BYTE_FORMAT.pack(VERSION, expiry)
        payload: bytes = header + message.encode("utf8")
        digest: bytes = hmac.new(secret.data, payload, hashlib.sha384).digest()

        return base64.urlsafe_b64encode(header + digest)

    @staticmethod
    def verify(
        secret: Secret, message: str, signature: SignedSecret
    ) -> SignatureHeader:
        """Verify a signed message using a secret.

        :param secret: The secret used to sign the message.
        :type secret: `Secret`
        :param message: The original message that was signed.
        :type message: str
        :param signature: The signature of the message.
        :type signature: `SignedSecret`
        :return: The header of the signature.
        :rtype: `SignatureHeader`
        :raises: `SignatureError`: If the signature was corrupt, has expired, or is not valid.
        """
        try:
            decoded_signature: bytes = base64.urlsafe_b64decode(signature)
            header: bytes = decoded_signature[: BYTE_FORMAT.size]
            digest: bytes = decoded_signature[BYTE_FORMAT.size :]
            version, expiry = BYTE_FORMAT.unpack(header)

            if version != VERSION:
                raise ValueError
            if len(digest) != hashlib.sha384().digest_size:
                raise ValueError
        except (struct.error, KeyError, binascii.Error, TypeError, ValueError):
            raise SignatureError("The signature was corrupt and cannot be read.")

        if time.time() > expiry:
            raise SignatureError("The signature has expired and is no longer valid.")

        payload: bytes = header + message.encode("utf8")
        compared_digest: bytes = hmac.new(
            secret.data, payload, hashlib.sha384()
        ).digest()

        if not hmac.compare_digest(compared_digest, digest):
            raise SignatureError(
                "The signature digest is not the same, the signature is not valid."
            )

        return SignatureHeader(version, expiry)


class Encrypt:
    @staticmethod
    def write(message: str, secret: Secret) -> bytes:
        """Encrypt a message using a given secret.

        :param message: The message to be encrypted.
        :type message: str
        :param secret: The secret key to use for encryption.
        :type secret: `Secret`
        :return: The encrypted message as bytes.
        :rtype: bytes
        """
        fernet: Fernet = Fernet(secret.data)
        xor_message: str = message ^ secret
        return fernet.encrypt(xor_message.encode())

    @staticmethod
    def read(raw: bytes, secret: Secret) -> bytes:
        """Decrypt a message using a given secret.

        :param raw: The encrypted message as bytes.
        :type raw: bytes
        :param secret: The secret key to use for decryption.
        :type secret: `Secret`
        :return: The decrypted message as bytes.
        :rtype: bytes
        """
        fernet: Fernet = Fernet(secret.data)
        decoded_message: bytes = fernet.decrypt(raw)
        return decoded_message ^ secret.data
