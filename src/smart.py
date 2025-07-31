"""
Namespace for smart operations.

NOTE: this module is not included in the main `re_extensions` namespace - run
`from re_extensions import smart` to use this module.

"""

import re
from typing import TYPE_CHECKING, Generator, Generic, Iterable, Iterator, TypeVar, Union

from .core import find_right_bracket

if TYPE_CHECKING:
    from re import Pattern

    from ._typing import FlagType, MatchType, PatternType, ReplType

AnyStr = TypeVar("AnyStr", str, bytes)
T = TypeVar("T")

__all__ = [
    "SmartPattern",
    "SmartMatch",
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


class SmartPattern(Generic[AnyStr]):
    """
    Similar to `re.Pattern` but it tells the matcher to ignore the contents
    within brackets while matching.

    By default, "{}" is used to mark where the contents can be ignored, or
    you can customize it by specifying `mark_ignore=`. Suppose the mark is
    "{}", pattern "a{}b" roughly equals to "(?>a)P?(?>b)|(?>ab)", where "P"
    matches a pair of brackets and the contents within the brackets (if
    exists).

    Presently, the matching does not support lookbehind assertions, so
    special characters like "^", "\\A", "\\b", "\\B", "(?<=...)", and
    "(?<!...)" will be removed automatically.

    If you feel confused about the above rules, run `on_earth(pattern)` to
    see what kind of string on earth will the pattern match.

    Examples
    --------
    * When ignore="()", pattern "a{}b" can match the string "ab" or "a(...)b",
    but not "a(b)".
    * When ignore="()[]", pattern "a{}b" can match the string "ab", "a(...)b"
    or "a[...]b", but not "a(...)[...]b".
    * Similarly, when ignore="()[]{}", pattern "a{}b" can match the string
    "ab", "a{c}b", etc.

    Parameters
    ----------
    ignore : ignore, optional
        Patterns to ignore while matching, by default "()[]{}".
    mark : str, optional
        Marks where the smart pattern should take effect, by default "{}".

    """

    def __init__(
        self,
        pattern: Union[AnyStr, "Pattern[AnyStr]"],
        flags: "FlagType" = 0,
        ignore: str = "()[]{}",
        mark: str = "{}",
    ) -> None:
        if isinstance(pattern, re.Pattern):
            pattern, flags = pattern.pattern, pattern.flags | flags
        self.pattern = pattern
        self.flags = flags
        self.ignore, self.mark = ignore, mark


class SmartMatch(Generic[AnyStr]):
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
        group: AnyStr,
        groups: Iterable[AnyStr],
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

    def group(self) -> AnyStr:
        """Return one or more subgroups of the match of the match."""
        return self.__group

    def groups(self, default: T = None) -> tuple[Union[AnyStr, T], ...]:
        """Return a tuple containing all the subgroups of the match."""
        if default is None:
            return self.__groups
        return tuple(default if x is None else x for x in self.__groups)

    def groupdict(self, default: T = None) -> dict[str, Union[AnyStr, T]]:
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
    Union[Match[str], SmartMatch[str], None]
        Match result.

    """
    if isinstance(pattern, (str, re.Pattern)):
        return re.search(pattern, string, flags=flags)
    p, f = pattern.pattern, pattern.flags | flags
    if pattern.ignore_mark not in p:
        return re.search(p, string, flags=f)
    to_search = p.partition(pattern.ignore_mark)[0]
    pos_now: int = 0
    while string and (searched := re.search(to_search, string, flags=f)):
        pos_now += searched.start()
        string = string[searched.start() :]
        if matched := match(pattern, string, flags=flags):
            return SmartMatch(
                (pos_now, pos_now + matched.end()),
                matched.group(),
                matched.groups(),
                matched.groupdict(),
            )
        pos_now += 1
        string = string[1:]
    return None


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
    Union[Match[str], SmartMatch[str], None]
        Match result.

    """
    if isinstance(pattern, (str, re.Pattern)):
        return re.match(pattern, string, flags=flags)
    p, f = pattern.pattern, pattern.flags | flags
    if len(splited := p.split(pattern.ignore_mark)) == 1:
        return re.match(p, string, flags=f)
    crossline = (f & re.DOTALL) > 0
    pos_now, temp, substr, left, groups, gdict = 0, "", "", pattern.ignore[::2], [], {}
    for s in splited[:-1]:
        temp += s
        if not (matched := re.match(temp, string, flags=f)):
            return None
        if matched.end() < len(string) and string[matched.end()] in left:
            n = find_right_bracket(string, matched.end(), crossline=crossline)
            if n < 0:
                return None
            pos_now += n
            substr += string[:n]
            string = string[n:]
            groups.extend(matched.groups())
            gdict.update(matched.groupdict())
            temp = ""
    if matched := re.match(temp + splited[-1], string, flags=f):
        groups.extend(matched.groups())
        gdict.update(matched.groupdict())
        return SmartMatch(
            (0, pos_now + matched.end()), substr + matched.group(), groups, gdict
        )
    return None


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
    Union[Match[str], SmartMatch[str], None]
        Match result.

    """
    if isinstance(pattern, (str, re.Pattern)):
        return re.fullmatch(pattern, string, flags=flags)
    return match(f"(?:{pattern.pattern})\\Z", string, flags=pattern.flags | flags)


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
    return _find_generator(pattern, string, flags=flags)


def _find_generator(
    pattern: "PatternType", string: str, flags: "FlagType" = 0
) -> Generator["MatchType", None, None]:
    pos_now = 0
    while searched := search(pattern, string, flags=flags):
        yield SmartMatch(
            (pos_now + searched.start(), pos_now + searched.end()),
            searched.group(),
            searched.groups(),
            searched.groupdict(),
        )
        if not string:
            break
        pos_now += (n := 1 if searched.end() == 0 else searched.end())
        string = string[n:]


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
    finds: list[str] = []
    while searched := search(pattern, string, flags=flags):
        finds.append(searched.group())
        if not string:
            break
        string = string[1 if searched.end() == 0 else searched.end() :]
    return finds


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
    if count < 0:
        return string
    new_string = ""
    while searched := search(pattern, string, flags=flags):
        new_string += string[: searched.start()]
        new_string += repl if isinstance(repl, str) else repl(searched)
        if not string or (count := count - 1) == 0:
            break
        if searched.end() == 0:
            new_string += string[0]
            string = string[1:]
        else:
            string = string[searched.end() :]
    return new_string + string


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
    if count < 0:
        return (string, 0)
    new_string = ""
    tmpcnt = count
    while searched := search(pattern, string, flags=flags):
        new_string += string[: searched.start()]
        new_string += repl if isinstance(repl, str) else repl(searched)
        if (tmpcnt := tmpcnt - 1) == 0 or not string:
            break
        if searched.end() == 0:
            new_string += string[0]
            string = string[1:]
        else:
            string = string[searched.end() :]
    return (new_string + string, count - tmpcnt)


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
    if maxsplit < 0 or not (searched := search(pattern, string, flags=flags)):
        return [string]
    splits = []
    stored = ""
    while searched and string:
        if searched.end() == 0:
            splits.append(stored)
            stored = string[0]
            string = string[1:]
        else:
            splits.append(stored + string[: searched.start()])
            stored = ""
            string = string[searched.end() :]
        if (maxsplit := maxsplit - 1) == 0:
            break
        searched = search(pattern, string, flags=flags)
    else:  # not searched or not string
        if searched:  # not string but searched
            splits.append(stored)
            splits.append("")
            return splits
    # breaked or not searched
    splits.append(stored + string)
    return splits


def rsplit(
    pattern: "PatternType", string: str, maxsplit: int = 0, flags: "FlagType" = 0
) -> list[str]:
    """
    Split the string by the occurrences of the pattern. Differences to
    `smart_split()` that the matched substrings are also returned, each
    connected with the unmatched substring on its right.

    NOTE: If the pattern is an instance of `SmartPattern`, any group
    (...) in the pattern will be regarded as (?:...), so that the
    substring matched by the group cannot be retrieved.

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
    if maxsplit < 0 or not (searched := search(pattern, string, flags=flags)):
        return [string]
    splits = [""]
    stored = ""
    while searched and string:
        if searched.end() == 0:
            splits[-1] += stored
            stored = string[0]
            string = string[1:]
        else:
            splits[-1] += stored + string[: searched.start()]
            stored = ""
            string = string[searched.end() :]
        splits.append(searched.group())
        if (maxsplit := maxsplit - 1) == 0:
            break
        searched = search(pattern, string, flags=flags)
    else:  # not searched or not string
        if searched:  # not string but searched
            splits[-1] += stored
            splits.append("")
            return splits
    # breaked or not searched
    splits[-1] += stored + string
    return splits


def lsplit(
    pattern: "PatternType", string: str, maxsplit: int = 0, flags: "FlagType" = 0
) -> list[str]:
    """
    Split the string by the occurrences of the pattern. Differences to
    `smart_split()` that the matched substrings are also returned, each
    connected with the unmatched substring on its left.

    NOTE: If the pattern is an instance of `SmartPattern`, any group
    (...) in the pattern will be regarded as (?:...), so that the
    substring matched by the group cannot be retrieved.

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

    if maxsplit < 0 or not (searched := search(pattern, string, flags=flags)):
        return [string]
    splits = []
    stored = string[: searched.start()]
    while searched and string:
        if searched.end() == 0:
            splits.append(stored)
            stored = string[0]
            string = string[1:]
        else:
            splits.append(stored + string[: searched.end()])
            stored = ""
            string = string[searched.end() :]
        if (maxsplit := maxsplit - 1) == 0:
            break
        searched = search(pattern, string, flags=flags)
    else:  # not searched or not string
        if searched:  # not string but searched
            splits.append(stored)
            splits.append("")
            return splits
    # breaked or not searched
    splits.append(stored + string)
    return splits


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
