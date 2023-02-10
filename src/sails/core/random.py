import random

from sails.common.dictionary import words


class RandomString:
    """Class to generate a random string made up of multiple segments separated by a given separator."""

    def generate(segments: int, seperator: str = "-") -> str:
        """Generates a random string made up of multiple segments separated by a given separator.

        :param segments: The number of segments to generate.
        :type segments: int
        :param seperator: The string to use as a separator between the generated segments.
        :type seperator: str
        :return: The generated string.
        :rtype: str
        """
        generated_words: list[str] = random.sample(words, segments)
        return seperator.join(generated_words)
