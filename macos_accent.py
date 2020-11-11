"""This module allows for interactions with MacOS's highlight and accent color preferences.
It does so through system command using the default command. It is also able to determine
a "closest" color to a given hex input and set the accent and highlight colors to that
color. This module is indended for use with pywal"""

import os
import subprocess
from typing import Tuple

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
    """Uses OS commands to se the MacOS accent color

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
        color_text = str.split(output.stdout.decode("utf-8"), ' ')[3]
        color_text = color_text[0:len(color_text) - 1]

        for i in set(dict.keys(ACCENT_DEFINITIONS)):
            if ACCENT_DEFINITIONS[i][0] == color_text:
                return i

        raise ValueError('Defaults returned unexpected color text')
    else:
        return -2


def set_highlight(value: int) -> None:
    """Uses OS commands to se the MacOS highlight color

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


def hex_color_to_decimal_rgb(hex_color: str) -> Tuple[float, float, float]:
    """Convert a given hex color into a decimal rgb tuple
    >>> from math import isclose
    >>> expected = (0.941176471, 0.682352941, 0.356862745)
    >>> result = hex_color_to_decimal_rgb('f0ae5b')
    >>> all([isclose(expected[i], result[i]) for i in range(0, 3)])
    True
    """
    if hex_color[0] == '#':
        return (int(hex_color[1:3], 16) / 255,
                int(hex_color[3:5], 16) / 255,
                int(hex_color[5:7], 16) / 255)
    else:
        return (int(hex_color[0:2], 16) / 255,
                int(hex_color[2:4], 16) / 255,
                int(hex_color[4:6], 16) / 255)


def get_closeness(color1: Tuple[float, float, float], color2: Tuple[float, float, float]) -> float:
    """Return a float representing how close two decimal rgb color values are

    >>> from math import isclose
    >>> result = get_closeness((0.5, 0.5, 0.5), (0.4, 0.4, 0.4))
    >>> isclose(result, 0.29999999999999993)
    True
    >>> get_closeness((0, 0, 0), (0, 1, 0))
    1
    """
    return sum([abs(color1[i] - color2[i]) for i in range(0, 3)])


def get_closest_color(hex_color: str) -> int:
    """Return the closest color to the input in ACCENT_DEFINITIONS"""
    lowest_closeness_so_far = 1
    closest_color = -2

    decimal_rgb = hex_color_to_decimal_rgb(hex_color)

    for i in list(dict.keys(ACCENT_DEFINITIONS)):
        current_closeness = get_closeness(decimal_rgb, ACCENT_DEFINITIONS[i][1])
        if current_closeness < lowest_closeness_so_far:
            lowest_closeness_so_far = current_closeness
            closest_color = i

    return closest_color


def set_closest_color(hex_color: str) -> None:
    """Get the closest color with get_closest_color
    then set both the highlight and accent colors"""
    closest = get_closest_color(hex_color)
    set_accent(closest)
    set_highlight(closest)


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
