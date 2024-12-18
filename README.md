# re-extensions
Extensions for the `re` package.

## Installation
```sh
$ pip install re-extensions
```

## Requirements
```txt

```

## See Also
### Github repository
* https://github.com/Chitaoji/re-extensions/

### PyPI project
* https://pypi.org/project/re-extensions/

## License
This project falls under the BSD 3-Clause License.

## History
### v0.0.6
* Removed `real_findall()` - use `smart_finditer()` or `line_finditer()` instead.

### v0.0.5
* New (advanced) regex operations `smart_finditer()` and `line_finditer()`.
* Removed `pattern_inreg()` because it has the same functionality as `re.escape()` - use that instead.

### v0.04
* New string operation `quote_collapse()`.
* Renamed the namespace `Smart` as `smart`. Please run `from re_extensions import smart` to activate this namespace.
* Bugfix for `rsplit()`;

### v0.0.3
* The basic structure of the package is completed, including:
  * advanced regex operations `smart_search()`, `smart_match()`, `smart_fullmatch()`, `smart_sub()`, `smart_subn()`, and `smart_split()`;
  * new regex operations `rsplit()`, `lsplit()`, `line_findall()`, and `real_findall()`;
  * string operations `counted_strip()`, `line_count()`, `line_count_iter()`, and `word_wrap()`;
  * utility classes `Smart`, `SmartPattern` and `SmartMatch`;
  * and other utility functions: `find_right_bracket()`, `find_left_bracket()`, and `pattern_inreg()`.

### v0.0.2
* Bugfix for `setup.py`.

### v0.0.1
* Initial release.