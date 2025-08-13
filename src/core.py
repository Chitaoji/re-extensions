"""
Contains the core of re-extensions: rsplit(), lsplit(), smart_search(), etc.

NOTE: this module is private. All functions and objects are available in the main
`re_extensions` namespace - use that instead.

"""

import re
import textwrap
from typing import Iterable, Iterator, TypeVar

AnyStr = TypeVar("AnyStr", str, bytes)
T = TypeVar("T")

__all__ = [
    "quote_collapse",
    "find_right_bracket",
    "find_left_bracket",
    "line_count",
    "line_count_iter",
    "counted_strip",
    "word_wrap",
]


def quote_collapse(string: str) -> str:
    """
    Returns a copy of the string with the contents in quotes
    collapsed.

    """
    last_quote = ""
    quotes: list[tuple[int, int]] = []
    pos_now, last_pos, len_s = 0, 0, len(string)
    while pos_now < len_s:
        if string[pos_now] == "\\":
            pos_now += 2
            continue
        elif (char := string[pos_now]) in "'\"":
            if last_quote:
                if last_quote == char:
                    pos_now += 1
                    last_quote, last_pos = "", pos_now
                    continue
                elif last_quote == char * 3:
                    pos_now += 3
                    last_quote, last_pos = "", pos_now
                    continue
            elif string[pos_now + 1 : pos_now + 3] == char * 2:
                quotes.append((last_pos, pos_now))
                last_quote = char * 3
                pos_now += 3
                continue
            else:
                quotes.append((last_pos, pos_now))
                last_quote = char
        pos_now += 1
    if last_quote:
        raise SyntaxError(f"unterminated string literal: {last_quote!r}")
    quotes.append((last_pos, pos_now))
    return "".join([string[i:j] for i, j in quotes])


def find_right_bracket(string: str, start: int, crossline: bool = False) -> int:
    """
    Find the right bracket paired with the specified left bracket.

    Parameters
    ----------
    string : str
        String.
    start : int
        Position of the left bracket.
    crossline : bool
        Determines whether the matched substring can include "\\n".

    Returns
    -------
    int
        Position of the matched right bracket + 1. If not found,
        -1 will be returned.

    Raises
    ------
    ValueError
        `string[start]` is not a left bracket.

    """
    if (left := string[start]) == "(":
        right = ")"
    elif left == "[":
        right = "]"
    elif left == "{":
        right = "}"
    else:
        raise ValueError(f"string[{start}] is not a left bracket")
    cnt: int = 1
    for pos_now in range(start + 1, len(string)):
        if (now := string[pos_now]) == left:
            cnt += 1
        elif now == right:
            cnt -= 1
        elif now == "\n" and not crossline:
            break
        if cnt == 0:
            return pos_now + 1
    return -1


def find_left_bracket(string: str, start: int, crossline: bool = False) -> int:
    """
    Find the left bracket paired with the specified right bracket.

    Parameters
    ----------
    string : str
        String.
    start : int
        Position of the right bracket + 1.
    crossline : bool
        Determines whether the matched substring can include "\\n".

    Returns
    -------
    int
        Position of the matched left bracket. If not found, -1 will
        be returned.

    Raises
    ------
    ValueError
        `string[start - 1]` is not a right bracket.

    """
    if (right := string[start - 1]) == ")":
        left = "("
    elif right == "]":
        left = "["
    elif right == "}":
        left = "{"
    else:
        raise ValueError(f"string[{start-1}] is not a right bracket")
    cnt: int = 1
    for pos_now in range(start - 2, -1, -1):
        if (now := string[pos_now]) == right:
            cnt += 1
        elif now == left:
            cnt -= 1
        elif now == "\n" and not crossline:
            break
        if cnt == 0:
            return pos_now
    return -1


def line_count(string: str) -> int:
    """
    Counts the number of lines in the string; returns (number of "\\n") + 1.

    Parameters
    ----------
    string : str
        String.

    Returns
    -------
    int
        Number of lines.

    """
    return 1 + string.count("\n")


def line_count_iter(iterstr: Iterable[str]) -> Iterator[tuple[int, str]]:
    """
    Counts the number of lines in each string, and returns the cumsumed
    values.

    Parameters
    ----------
    iter : Iterable[str]
        An iterable of strings.

    Yields
    ------
    tuple[int, str]
        Each time, yields the cumsumed number of lines til now together
        with a string found in `iter`, until `iter` is traversed.

    """
    cnt: int = 1
    for s in iterstr:
        yield cnt, s
        cnt += s.count("\n")


def word_wrap(string: str, maximum: int = 80) -> str:
    """
    Takes a string as input and wraps the text into multiple lines,
    ensuring that each line has a maximum length of characters.

    Parameters
    ----------
    string : str
        The input text that needs to be word-wrapped.
    maximum : int, optional
        Specifies the maximum length of each line in the word-wrapped
        string, by default 80.

    Returns
    -------
        Wrapped string.

    """
    return "\n".join(
        textwrap.fill(x, maximum, break_long_words=False) for x in string.splitlines()
    )


def counted_strip(string: str) -> tuple[str, int, int]:
    """
    Return a copy of the string with leading and trailing whitespace
    removed, together with the number of removed leading whitespaces
    and the number of removed leading whitespaces.

    Parameters
    ----------
    string : str
        String.

    Returns
    -------
    tuple[str, int, int]
        The new string, the number of removed leading whitespace, and
        the number of removed trailing whitespace.

    """
    l = len(re.match("\n*", string).group())
    r = len(re.search("\n*$", string).group())
    return string.strip(), l, r
