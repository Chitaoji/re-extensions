"""
Namespace for smart operations.

NOTE: run `from re_extensions import smart` to use this module.

"""

import re
from typing import TYPE_CHECKING, Iterable, Iterator, TypeVar

if TYPE_CHECKING:
    from re import Pattern

    from ._typing import FlagType, MatchType, PatternType, ReplType


T = TypeVar("T")

__all__ = [
    "SmartPattern",
    "search",
    "match",
    "fullmatch",
    "finditer",
    "sub",
    "subn",
    "split",
    "rsplit",
    "lsplit",
    "findall",
    "line_finditer",
    "line_findall",
]


class SmartPattern:
    """
    Similar to `re.Pattern` but it can "smartly" match the content in a
    pair of brackets, no matter how many pairs of brackets are contained in
    the content.

    "{}" is used to mark where the smart match should take place. Pattern
    "{()}" matches a pair of brackets and all the contents within the
    brackets. If you want to match the content within a pair of square
    brackets or braces, use "{[]}" or "{{}}" instead.

    Examples
    --------
    * pattern "a{()}b" matches "a(...)b", but not "ab" or "a(b)";
    * pattern "a{[]}b" matches "a[...]b";
    * pattern "a{{}}b" matches "a{...}b".

    Parameters
    ----------
    pattern : str | Pattern[str]
        Regex pattern.
    flags : FlagType, optional
        Regex flag, by default 0.

    """

    def __init__(self, pattern: "str | Pattern[str]", flags: "FlagType" = 0) -> None:
        if isinstance(pattern, re.Pattern):
            pattern, flags = pattern.pattern, pattern.flags | flags
        self.pattern = pattern
        self.flags = flags

    def get_pattern(self, string: str, /) -> str:
        """Get the real pattern according to the string."""
        substrs = re.split("({.*?})", self.pattern)
        is_smart_pattern, new_pattern = False, ""
        for x in substrs:
            if is_smart_pattern:
                if not len(x) == 4:
                    raise ValueError(f"invalid subpattern: {x}")
                s, e = re.escape(x[1]), re.escape(x[2])
                neg = f"[^{s}{e}]"
                p = f"{s}{neg}*{e}"
                for _ in range(1, find_bracket_depth(x[1], x[2], string)):
                    p = f"{s}{neg}*(?:{p}{neg}*)*{e}"
                new_pattern += f"(?:{p})"
                is_smart_pattern = False
            else:
                new_pattern += x
                is_smart_pattern = True
        return new_pattern

    def get_flags(self, flags: "FlagType", /) -> "FlagType":
        """Get the real flags."""
        return self.flags | flags


class SmartMatch:
    """
    Acts like `re.Match`.

    NOTE: properties `pos`, `endpos`, `lastindex`, `lastgroup`, `re`, and
    `string` are not implemented for faster speed.

    Parameters
    ----------
    span : tuple[int, int]
        The indices of the start and end of the substring matched by `group`.
    group : str
        Group of the match.

    """

    def __init__(
        self,
        span: tuple[int, int],
        group: str,
        groups: Iterable[str],
        groupdict: dict[str, str],
    ) -> None:
        self.__span = span
        self.__group = group
        self.__groups = tuple(groups)
        self.__groupdict = groupdict

    def __repr__(self) -> str:
        return f"<SmartMatch object; span={self.__span}, match={self.__group!r}>"

    def span(self) -> tuple[int, int]:
        """
        The indices of the start and end of the substring matched by `group`.

        """
        return self.__span

    def group(self) -> str:
        """Return one or more subgroups of the match of the match."""
        return self.__group

    def groups(self, default: T = None) -> tuple[str, ...]:
        """Return a tuple containing all the subgroups of the match."""
        if default is None:
            return self.__groups
        return tuple(default if x is None else x for x in self.__groups)

    def groupdict(self, default: T = None) -> dict[str, str]:
        """
        Return a dictionary containing all the named subgroups of the match,
        keyed by the subgroup name.

        """
        if default is None:
            return self.__groupdict
        return {k: default if v is None else v for k, v in self.__groupdict.items()}

    def start(self) -> int:
        """Return the indice of the start of the substring matched by `group`."""
        return self.__span[0]

    def end(self) -> int:
        """Return the indice of the end of the substring matched by `group`."""
        return self.__span[1]


def find_bracket_depth(left: str, right: str, string: str) -> int:
    """Find the maximum depth of pairs of brackets."""
    depth_now, depth_max = 0, 0
    for c in string:
        if c == left:
            depth_now += 1
            depth_max = max(depth_max, depth_now)
        elif c == right and depth_now > 0:
            depth_now -= 1
    return depth_max


# ==============================================================================
#                             Smart Operations
# ==============================================================================


def search(pattern: "PatternType", string: str, flags: "FlagType" = 0) -> "MatchType":
    """
    Finds the first match in the string. Differences to `re.search()` that
    the pattern can be a `SmartPattern` object.

    Parameters
    ----------
    pattern : PatternType
        Regex pattern.
    string : str
        String to be searched.
    flags : FlagType, optional
        Regex flags, by default 0.

    Returns
    -------
    MatchType
        Match result.

    """
    if isinstance(pattern, (str, re.Pattern)):
        return re.search(pattern, string, flags=flags)
    if not isinstance(pattern, SmartPattern):
        raise TypeError(f"invalid pattern type: {type(pattern)}")
    return re.search(
        pattern.get_pattern(string), string, flags=pattern.get_flags(flags)
    )


def match(pattern: "PatternType", string: str, flags: "FlagType" = 0) -> "MatchType":
    """
    Match the pattern. Differences to `re.match()` that the pattern can
    be a `SmartPattern` object.

    Parameters
    ----------
    pattern : PatternType
        Regex pattern.
    string : str
        String to be searched.
    flags : FlagType, optional
        Regex flags, by default 0.

    Returns
    -------
    MatchType
        Match result.

    """
    if isinstance(pattern, (str, re.Pattern)):
        return re.match(pattern, string, flags=flags)
    if not isinstance(pattern, SmartPattern):
        raise TypeError(f"invalid pattern type: {type(pattern)}")
    return re.match(pattern.get_pattern(string), string, flags=pattern.get_flags(flags))


def fullmatch(
    pattern: "PatternType", string: str, flags: "FlagType" = 0
) -> "MatchType":
    """
    Match the pattern. Differences to `re.match()` that the pattern can
    be a `SmartPattern` object.

    Parameters
    ----------
    pattern : PatternType
        Regex pattern.
    string : str
        String to be searched.
    flags : FlagType, optional
        Regex flags, by default 0.

    Returns
    -------
    MatchType
        Match result.

    """
    if isinstance(pattern, (str, re.Pattern)):
        return re.fullmatch(pattern, string, flags=flags)
    if not isinstance(pattern, SmartPattern):
        raise TypeError(f"invalid pattern type: {type(pattern)}")
    return re.fullmatch(
        pattern.get_pattern(string), string, flags=pattern.get_flags(flags)
    )


def finditer(
    pattern: "PatternType", string: str, flags: "FlagType" = 0
) -> Iterator["MatchType"]:
    """
    Return an iterator over all non-overlapping matches in the string.
    Differences to `re.finditer()` that the pattern can be a
    `SmartPattern` object.

    Parameters
    ----------
    pattern : PatternType
        Regex pattern.
    string : str
        String to be searched.
    flags : FlagType, optional
        Regex flags, by default 0.

    Returns
    -------
    Iterator[MatchType]
        An iterator over all non-overlapping matches.

    """
    if isinstance(pattern, (str, re.Pattern)):
        return re.finditer(pattern, string, flags=flags)
    if not isinstance(pattern, SmartPattern):
        raise TypeError(f"invalid pattern type: {type(pattern)}")
    return re.finditer(
        pattern.get_pattern(string), string, flags=pattern.get_flags(flags)
    )


def findall(pattern: "PatternType", string: str, flags: "FlagType" = 0) -> list[str]:
    """
    Returns a list of all non-overlapping matches in the string. Differences
    to `re.findall()` that the pattern can be a `SmartPattern` object.

    Parameters
    ----------
    pattern : PatternType
        Regex pattern.
    string : str
        String to be searched.
    flags : FlagType, optional
        Regex flags, by default 0.

    Returns
    -------
    list[str]
        List of all non-overlapping matches.

    """
    if isinstance(pattern, (str, re.Pattern)):
        return re.findall(pattern, string, flags=flags)
    if not isinstance(pattern, SmartPattern):
        raise TypeError(f"invalid pattern type: {type(pattern)}")
    return re.findall(
        pattern.get_pattern(string), string, flags=pattern.get_flags(flags)
    )


def sub(
    pattern: "PatternType",
    repl: "ReplType",
    string: str,
    count: int = 0,
    flags: "FlagType" = 0,
) -> str:
    """
    Return the string obtained by replacing the leftmost non-overlapping
    occurrences of the pattern in string by the replacement repl. Differences
    to `re.sub()` that the pattern can be a `SmartPattern` object.

    Parameters
    ----------
    pattern : PatternType
        Regex pattern.
    repl : ReplType
        Speficies the string to replace the patterns. If Callable, should
        be a function that receives the Match object, and gives back
        the replacement string to be used.
    string : str
        String to be searched.
    count : int, optional
        Max number of replacements; if set to 0, there will be no limits;
        if < 0, the string will not be replaced; by default 0.
    flags : FlagType, optional
        Regex flags, by default 0.

    Returns
    -------
    str
        New string.

    """
    if isinstance(pattern, (str, re.Pattern)):
        return re.sub(pattern, repl, string, count=count, flags=flags)
    if not isinstance(pattern, SmartPattern):
        raise TypeError(f"invalid pattern type: {type(pattern)}")
    return re.sub(
        pattern.get_pattern(string),
        repl,
        string,
        count=count,
        flags=pattern.get_flags(flags),
    )


def subn(
    pattern: "PatternType",
    repl: "ReplType",
    string: str,
    count: int = 0,
    flags: "FlagType" = 0,
) -> tuple[str, int]:
    """
    Return a 2-tuple containing (new_string, number); new_string is the string
    obtained by replacing the leftmost non-overlapping occurrences of the
    pattern in string by the replacement repl; number is the number of
    substitutions that were made. Differences to `re.subn()` that the pattern
    can be a `SmartPattern` object.

    Parameters
    ----------
    pattern : PatternType
        Regex pattern.
    repl : ReplType
        Speficies the string to replace the patterns. If Callable, should
        be a function that receives the Match object, and gives back
        the replacement string to be used.
    string : str
        String to be searched.
    count : int, optional
        Max number of replacements; if set to 0, there will be no limits;
        if < 0, the string will not be replaced; by default 0.
    flags : FlagType, optional
        Regex flags, by default 0.

    Returns
    -------
    tuple[str, int]
        (new_string, number).

    """
    if isinstance(pattern, (str, re.Pattern)):
        return re.subn(pattern, repl, string, count=count, flags=flags)
    if not isinstance(pattern, SmartPattern):
        raise TypeError(f"invalid pattern type: {type(pattern)}")
    return re.subn(
        pattern.get_pattern(string),
        repl,
        string,
        count=count,
        flags=pattern.get_flags(flags),
    )


def split(
    pattern: "PatternType", string: str, maxsplit: int = 0, flags: "FlagType" = 0
) -> list[str]:
    """
    Split the source string by the occurrences of the pattern, returning a
    list containing the resulting substrings. Differences to `re.split()`
    that the pattern can be a `SmartPattern` object.

    NOTE: If the pattern is an instance of `SmartPattern`, any group
    (...) in the pattern will be regarded as (?:...), so that the
    substring matched by the group cannot be retrieved.

    Parameters
    ----------
    pattern : PatternType
        Regex pattern.
    string : str
        String to be searched.
    maxsplit : int, optional
        Max number of splits; if set to 0, there will be no limits; if
        < 0, the string will not be splitted; by default 0.
    flags : FlagType, optional
        Regex flags, by default 0.

    Returns
    -------
    list[str]
        List containing the resulting substrings.

    """
    if isinstance(pattern, (str, re.Pattern)):
        return re.split(pattern, string, maxsplit=maxsplit, flags=flags)
    if not isinstance(pattern, SmartPattern):
        raise TypeError(f"invalid pattern type: {type(pattern)}")
    return re.split(
        pattern.get_pattern(string),
        string,
        maxsplit=maxsplit,
        flags=pattern.get_flags(flags),
    )


def rsplit(
    pattern: "PatternType", string: str, maxsplit: int = 0, flags: "FlagType" = 0
) -> list[str]:
    """
    Split the string by the occurrences of the pattern. Differences to
    `smart_split()` that the matched substrings are also returned, each
    connected with the unmatched substring on its right.

    NOTE: any group (...) in the pattern will be regarded as (?:...), so
    that the substring matched by the group cannot be retrieved.

    Parameters
    ----------
    pattern : PatternType
        Pattern string.
    string : str
        String to be splitted.
    maxsplit : int, optional
        Max number of splits; if set to 0, there will be no limits; if
        < 0, the string will not be splitted; by default 0.
    flags : FlagType, optional
        Regex flags, by default 0.

    Returns
    -------
    list[str]
        List of substrings.

    """
    if not isinstance(pattern, (str, re.Pattern)):
        if not isinstance(pattern, SmartPattern):
            raise TypeError(f"invalid pattern type: {type(pattern)}")
        pattern, flags = pattern.get_pattern(string), pattern.get_flags(flags)
    splits = re.split(pattern, string, maxsplit=maxsplit, flags=flags)
    idxmax = len(splits) - 1
    new_splits: list[str] = [splits[0]]
    idx = 0
    for f in re.finditer(pattern, string, flags=flags):
        idx += 1 + len(f.groups())
        if idx > idxmax:
            break
        new_splits.append(f.group() + splits[idx])
    return new_splits


def lsplit(
    pattern: "PatternType", string: str, maxsplit: int = 0, flags: "FlagType" = 0
) -> list[str]:
    """
    Split the string by the occurrences of the pattern. Differences to
    `smart_split()` that the matched substrings are also returned, each
    connected with the unmatched substring on its left.

    NOTE: any group (...) in the pattern will be regarded as (?:...), so
    that the substring matched by the group cannot be retrieved.

    Parameters
    ----------
    pattern : PatternType
        Pattern string.
    string : str
        String to be splitted.
    maxsplit : int, optional
        Max number of splits; if set to 0, there will be no limits; if
        < 0, the string will not be splitted; by default 0.
    flags : FlagType, optional
        Regex flags, by default 0.

    Returns
    -------
    list[str]
        List of substrings.

    """

    if not isinstance(pattern, (str, re.Pattern)):
        if not isinstance(pattern, SmartPattern):
            raise TypeError(f"invalid pattern type: {type(pattern)}")
        pattern, flags = pattern.get_pattern(string), pattern.get_flags(flags)
    splits = re.split(pattern, string, maxsplit=maxsplit, flags=flags)
    idxmax = len(splits) - 1
    new_splits: list[str] = []
    idx = 0
    for f in re.finditer(pattern, string, flags=flags):
        new_splits.append(splits[idx] + f.group())
        idx += 1 + len(f.groups())
        if idx > idxmax:
            break
    else:
        new_splits.append(splits[-1])
    return new_splits


def line_finditer(
    pattern: "PatternType", string: str, flags: "FlagType" = 0
) -> Iterator[tuple[int, "MatchType"]]:
    """
    Return an iterator over all non-overlapping matches in the string.
    Differences to `smart_finditer()` that it returns an iterator of
    2-tuples containing (nline, match); nline is the line number of the
    matched substring.

    NOTE: If the pattern is an instance of `SmartPattern`, any group
    (...) in the pattern will be regarded as (?:...), so that the
    substring matched by the group cannot be retrieved.

    Parameters
    ----------
    pattern : PatternType
        Regex pattern.
    string : str
        String to be searched.
    flags : FlagType, optional
        Regex flags, by default 0.

    Returns
    -------
    Iterator[tuple[int, MatchType]]
        List of 2-tuples containing (nline, substring).

    """
    nline, line_pos = 1, 0

    while searched := search(pattern, string, flags=flags):
        span, group = searched.span(), searched.group()
        left = string[: span[0]]
        lc_left = left.count("\n")
        nline += lc_left
        if lc_left > 0:
            line_pos = 0
        lastline_pos = len(left) - 1 - left.rfind("\n")
        matched = SmartMatch(
            (line_pos + lastline_pos, line_pos + lastline_pos + span[1] - span[0]),
            group,
            searched.groups(),
            searched.groupdict(),
        )
        yield (nline, matched)
        nline += group.count("\n")
        if "\n" in group:
            line_pos = len(group) - 1 - group.rfind("\n")
        else:
            line_pos += max(lastline_pos + span[1] - span[0], 1)

        if len(string) == 0:
            break
        if span[1] == 0:
            nline += 1 if string[0] == "\n" else 0
            line_pos = 0 if string[0] == "\n" else line_pos
            string = string[1:]
        else:
            string = string[span[1] :]


def line_findall(
    pattern: "PatternType", string: str, flags: "FlagType" = 0
) -> list[tuple[int, str]]:
    """
    Finds all non-overlapping matches in the string. Differences to
    `smart_findall()` that it returns a list of 2-tuples containing (nline,
    substring); nline is the line number of the matched substring.

    NOTE: If the pattern is an instance of `SmartPattern`, any group
    (...) in the pattern will be regarded as (?:...), so that the
    substring matched by the group cannot be retrieved.

    Parameters
    ----------
    pattern : PatternType
        Regex pattern.
    string : str
        String to be searched.
    flags : FlagType, optional
        Regex flags, by default 0.

    Returns
    -------
    list[tuple[int, str]]
        List of 2-tuples containing (nline, substring).

    """
    finds = []
    nline: int = 1

    while searched := search(pattern, string, flags=flags):
        span, group = searched.span(), searched.group()

        left = string[: span[0]]
        nline += left.count("\n")

        finds.append((nline, group))
        nline += group.count("\n")

        if len(string) == 0:
            break
        if span[1] == 0:
            nline += 1 if string[0] == "\n" else 0
            string = string[1:]
        else:
            string = string[span[1] :]
    return finds
