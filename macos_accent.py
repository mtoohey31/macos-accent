"""This module allows for interactions with MacOS's highlight and accent colour preferences.
It does so through system command using the default command. It is also able to determine
a "closest" colour to a given hex input and set the accent and highlight colours to that
colour. This module is indended for use with pywal"""

import os
import subprocess
from typing import List, Tuple

ACCENT_DEFINITIONS = {
    -2: ('Blue', (0.000000, 0.874510, 1.000000)),
    5: ('Purple', (0.968627, 0.831373, 1.000000)),
    6: ('Pink', (1.000000, 0.749020, 0.823529)),
    0: ('Red', (1.000000, 0.733333, 0.721569)),
    1: ('Orange', (1.000000, 0.874510, 0.701961)),
    2: ('Yellow', (1.000000, 0.937255, 0.690196)),
    3: ('Green', (0.752941, 0.964706, 0.678431)),
    -1: ('Graphite', (0.847059, 0.847059, 0.862745))
}


def read_accent() -> int:
    """Uses OS commands to read the MacOS accent colour
    >>> set_accent(3)
    >>> read_accent()
    3
    >>> set_accent(256)
    >>> read_accent()
    -2
    """
    output = subprocess.run("defaults read 'Apple Global Domain' AppleAccentColor",
                            shell=True, capture_output=True)
    if output.returncode == 0:
        return int(output.stdout.decode("utf-8"))
    else:
        return -2


def set_accent(value: int) -> None:
    """Uses OS commands to se the MacOS accent colour

    Preconditions:
        - value in set(dict.keys(ACCENT_DEFINITIONS))

    >>> set_accent(6)
    >>> read_accent()
    6
    >>> set_accent(-1)
    >>> read_accent()
    -1
    """
    if value in set.difference(set(dict.keys(ACCENT_DEFINITIONS)), {-2}):
        os.system("defaults write 'Apple Global Domain' AppleAccentColor '" + str(value) + "'")
    else:
        os.system("defaults delete 'Apple Global Domain' AppleAccentColor")


def read_highlight() -> int:
    """Uses OS commands to read the MacOS highlight colour
    >>> set_highlight(3)
    >>> read_highlight()
    3
    >>> set_highlight(256)
    >>> read_highlight()
    -2
    """
    output = subprocess.run("defaults read 'Apple Global Domain' AppleHighlightColor",
                            shell=True, capture_output=True)
    if output.returncode == 0:
        colour_text = str.split(output.stdout.decode("utf-8"), ' ')[3]
        colour_text = colour_text[0:len(colour_text) - 1]

        for i in set(dict.keys(ACCENT_DEFINITIONS)):
            if ACCENT_DEFINITIONS[i][0] == colour_text:
                return i

        raise ValueError('Defaults returned unexpected colour text')
    else:
        return -2


def set_highlight(value: int) -> None:
    """Uses OS commands to se the MacOS highlight colour

    Preconditions:
        - value in set(dict.keys(ACCENT_DEFINITIONS))

    >>> set_highlight(6)
    >>> read_highlight()
    6
    >>> set_highlight(-1)
    >>> read_highlight()
    -1
    """
    if value in set.difference(set(dict.keys(ACCENT_DEFINITIONS)), {-2}):
        value_text = str.join(' ', [str(val) for val in
                                    ACCENT_DEFINITIONS[value][1]] + [ACCENT_DEFINITIONS[value][0]])
        os.system("defaults write 'Apple Global Domain' AppleHighlightColor '" + value_text + "'")
    else:
        os.system("defaults delete 'Apple Global Domain' AppleHighlightColor")


def hex_colour_to_decimal_rgb(hex_colour: str) -> Tuple[float, float, float]:
    """Convert a given hex colour into a decimal rgb tuple
    >>> from math import isclose
    >>> expected = (0.941176471, 0.682352941, 0.356862745)
    >>> result = hex_colour_to_decimal_rgb('f0ae5b')
    >>> all([isclose(expected[i], result[i]) for i in range(0, 3)])
    True
    """
    if hex_colour[0] == '#':
        return (int(hex_colour[1:3], 16) / 255,
                int(hex_colour[3:5], 16) / 255,
                int(hex_colour[5:7], 16) / 255)
    else:
        return (int(hex_colour[0:2], 16) / 255,
                int(hex_colour[2:4], 16) / 255,
                int(hex_colour[4:6], 16) / 255)


def get_closeness(colour1: Tuple[float, float, float], colour2: Tuple[float, float, float]) -> float:
    """Return a float representing how close two decimal rgb colour values are. The lower the number, the closer the colours.

    >>> from math import isclose
    >>> result = get_closeness((0.5, 0.5, 0.5), (0.4, 0.4, 0.4))
    >>> isclose(result, 0.29999999999999993)
    True
    >>> get_closeness((0, 0, 0), (0, 1, 0))
    1
    """
    return sum([abs(colour1[i] - colour2[i]) for i in range(0, 3)])


def get_closest_to_single_colour(hex_colour: str) -> int:
    """Return the closest colour to the input in ACCENT_DEFINITIONS"""
    lowest_closeness_so_far = 3
    closest_colour = -2

    decimal_rgb = hex_colour_to_decimal_rgb(hex_colour)

    for i in list(dict.keys(ACCENT_DEFINITIONS)):
        current_closeness = get_closeness(decimal_rgb, ACCENT_DEFINITIONS[i][1])
        if current_closeness < lowest_closeness_so_far:
            lowest_closeness_so_far = current_closeness
            closest_colour = i

    return closest_colour


def get_cumulative_closest_to_multiple_colours(hex_colours: List[str]) -> int:
    """Return the closest colour to all of the input colours that is in ACCENT_DEFINITIONS
    based on a cumulative comparison"""
    decimal_rgb_colours = [hex_colour_to_decimal_rgb(hex_colour) for hex_colour in hex_colours]

    lowest_closeness_so_far = 3 * len(decimal_rgb_colours)
    closest_colour = -2

    for i in list(dict.keys(ACCENT_DEFINITIONS)):
        current_closeness = sum([get_closeness(decimal_rgb_colour, ACCENT_DEFINITIONS[i][1]) for decimal_rgb_colour in decimal_rgb_colours])
        if current_closeness < lowest_closeness_so_far:
            lowest_closeness_so_far = current_closeness
            closest_colour = i

    return closest_colour


def get_mean_closest_to_multiple_colours(hex_colours: List[str]) -> int:
    """Return the closest colour to all of the input colours that is in ACCENT_DEFINITIONS
    based on a mean of the individuals"""
    closest_colours = [get_closest_to_single_colour(hex_colour) for hex_colour in hex_colours]

    occurrences_of_closest_colours = {list.count(closest_colours, closest_colour): closest_colour for closest_colour in closest_colours}

    return occurrences_of_closest_colours[max(dict.keys(occurrences_of_closest_colours))]


def set_closest_colour(hex_colours: List[str]) -> None:
    """Get the closest colour with get_closest_colour
    then set both the highlight and accent colours"""
    closest = get_mean_closest_to_multiple_colours(hex_colours)
    set_accent(closest)
    set_highlight(closest)


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
