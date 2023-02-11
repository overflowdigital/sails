from cProfile import Profile
import logging
from pstats import Stats
import time
from typing import Callable

from sails.common.typing import Value
from sails.core.random import RandomString
from sails.sdk.directory import SDKDirectory


def simple_time_profiler(function: Callable) -> Callable:
    """
    A simple decorator function to log the execution time of a function.

    :param function: The function to be decorated.
    :type function: Callable
    :return: The decorated function.
    :rtype: Callable
    """

    def wrapper(*args, **kwargs) -> Value:
        """
        A wrapper function that logs the execution time of the decorated function.

        :param args: The arguments to be passed to the decorated function.
        :type args: Tuple
        :param kwargs: The keyword arguments to be passed to the decorated function.
        :type kwargs: Dict
        :return: The result of the decorated function.
        :rtype: Value
        """
        start_time: float = time.time()
        result: Value = function(*args, **kwargs)
        end_time: float = time.time()
        elapsed_time: float = end_time - start_time

        logging.getLogger().debug(
            f"[Sails Profiler]: {function.__name__} took {elapsed_time} seconds to execute."
        )

        return result

    return wrapper


def profiler(function: Callable) -> Callable:
    """
    A decorator function that profiles a given function and logs the profile stats.

    :param function: The function to be profiled.
    :type function: Callable
    :return: The decorated function that profiles the given function.
    :rtype: Callable
    """

    def wrapper(*args, **kwargs) -> Value:
        """
        The decorated function that profiles the given function.

        :param args: The positional arguments passed to the function.
        :type args: tuple
        :param kwargs: The keyword arguments passed to the function.
        :type kwargs: dict
        :return: The result of the function.
        :rtype: Value
        """
        profile: Profile = Profile()
        result: Value = profile.runcall(function, *args, **kwargs)
        file_name: str = SDKDirectory().get_file_name(
            "/profiles/" + function.__name__ + "-" + RandomString().generate()
        )

        profile.dump_stats(file_name)

        logging.getLogger().debug(
            f"[Sails Profiler]: {function.__name__} full profile was saved to {file_name}."
        )

        return result

    return wrapper
