from typing import Any, TypeVar, Union


T = TypeVar("T")
Value = Any
JSON = dict[str, Union[dict[str, Value], bool, int, str, list]]


class BasicObject:
    """Base class for objects that need to be converted from/to JSON."""

    def __init__(self, **kwargs) -> None:
        """Initialize the object with the given keyword arguments.

        :param kwargs: Keyword arguments to initialize the object's properties.
        :type kwargs: dict
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def from_dict(cls, value: dict[str, Value]) -> "BasicObject":
        """Create an object from a dictionary.

        :param value: The dictionary to use to create the object.
        :type value: dict[str, Value]

        :return: The created object.
        :rtype: BasicObject
        """
        return BasicObject(**value)
