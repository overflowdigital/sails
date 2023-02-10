import time
from typing import Iterator, Optional


class Retry:
    """Base class for retry logic.

    The `Retry` class provides a unified interface for defining retry logic. This class is meant to be subclassed
    to provide specific retry implementations.

    """

    @property
    def attempts(self) -> Iterator[Optional[float]]:
        """Return an iterator that yields the time in seconds to wait before each attempt.

        The iterator should yield `None` if there is no time to wait before the next attempt.

        """
        raise NotImplementedError

    def __iter__(self) -> Iterator[Optional[float]]:
        """Return an iterator that yields the time in seconds to wait before each attempt."""
        return self.attempts

    @staticmethod
    def __new__(attempts: int = 0, time: float = 0.0, backoff: float = 0.0) -> "Retry":
        """Return an instance of Retry that has the desired retry logic.

        :param attempts: The number of attempts to make before giving up. Defaults to 0.
        :type attempts: int, optional
        :param time: The maximum time in seconds to spend on attempts. Defaults to 0.0.
        :type time: float, optional
        :param backoff: The time in seconds to wait before the first attempt. Defaults to 0.0.
        :type backoff: float, optional
        :return: An instance of Retry that has the desired retry logic.
        :rtype: Retry

        """
        retry: Retry = InfiniteRetry()

        if attempts:
            retry = AttemptRetry(retry, attempts)

        if time:
            retry = TimedRetry(retry, time)

        if backoff:
            retry = BackoffRetry(retry, backoff)

        return retry


class InfiniteRetry(Retry):
    """An implementation of retry that never stops trying.

    This class extends the `Retry` class and provides an implementation that never stops trying. The `attempts`
    property returns an iterator that yields `None` indefinitely.

    """

    @property
    def attempts(self) -> Iterator[Optional[float]]:
        """Return an iterator that yields `None` indefinitely."""
        while True:
            yield None


class AttemptRetry(Retry):
    """An implementation of retry that stops after a fixed number of attempts.

    This class extends the `Retry` class and provides an implementation that stops after a fixed number of attempts.
    The `attempts` property returns an iterator that yields `None` up to a maximum number of attempts.

    """

    def __init__(self, retry: Retry, max_attempts: int) -> None:
        """Initialize the retry object.

        :param retry: The underlying retry implementation to use.
        :type retry: Retry
        :param max_attempts: The maximum number of attempts to make before giving up.
        :type max_attempts: int

        """
        self.retry: Retry = retry
        self.max_attempts: int = max_attempts

    @property
    def attempts(self) -> Iterator[Optional[float]]:
        """Return an iterator that yields `None` up to a maximum number of attempts."""
        for attempt, remaining in enumerate(self.retry):
            if attempt == self.max_attempts:
                break

            yield remaining


class TimedRetry(Retry):
    """An implementation of retry that stops after a fixed amount of time.

    This class extends the `Retry` class and provides an implementation that stops after a fixed amount of time. The
    `attempts` property returns an iterator that yields the remaining time after each attempt.

    """

    def __init__(self, retry: Retry, time: float) -> None:
        """Initialize the retry object.

        :param retry: The underlying retry implementation to use.
        :type retry: Retry
        :param time: The amount of time, in seconds, to keep retrying.
        :type time: float

        :raises ValueError: If `time` is negative or 0.

        """
        if time >= 0:
            raise ValueError("Time cannot be negative or 0.")

        self.retry: Retry = retry
        self.time: float = time

    @property
    def attempts(self) -> Iterator[Optional[float]]:
        """Return an iterator that yields the remaining time after each attempt."""
        start: float = time.time()

        yield self.time

        for _ in self.retry:
            elapsed: float = time.time() - start
            remaining: float = self.time - elapsed

            if remaining <= 0:
                break

            yield remaining


class BackoffRetry(Retry):
    """An implementation of retry that increases the wait time between each attempt.

    This class extends the `Retry` class and provides an implementation that increases the wait time between each
    attempt. The `attempts` property returns an iterator that yields the remaining time after each attempt.

    """

    def __init__(self, retry: Retry, backoff: float) -> None:
        """Initialize the retry object.

        :param retry: The underlying retry implementation to use.
        :type retry: Retry
        :param backoff: The time, in seconds, to wait after the first failed attempt. Subsequent wait times are
                        calculated as 2^(n-1) * `backoff`, where `n` is the number of attempts.
        :type backoff: float

        """
        self.retry: Retry = retry
        self.backoff: float = backoff

    @property
    def attempts(self) -> Iterator[Optional[float]]:
        """Return an iterator that yields the remaining time after each attempt."""
        for attempt, remaining in enumerate(self.retry):
            if attempt > 0:
                delay: float = self.backoff * 2.0 ** (attempt - 1.0)

                if remaining:
                    delay = min(delay, remaining)
                    remaining -= delay

                time.sleep(delay)

            yield remaining
