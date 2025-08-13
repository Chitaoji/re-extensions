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
### v0.0.8
* Bugfix: Updated the required Python version to `3.12.7`.

### v0.0.7
* Imported * from the `re_extensions.smart` namespace into the main `re_extensions` namespace.

### v0.0.6
* Removed `smart.real_findall()` - use `smart.finditer()` or `smart.line_finditer()` instead.

### v0.0.5
* New (advanced) regex operations `smart.finditer()` and `smart.line_finditer()`.
* Removed `pattern_inreg()` because it has the same functionality as `re.escape()` - use that instead.

### v0.04
* New string operation `quote_collapse()`.
* Renamed the namespace `Smart` as `smart`. Please run `from re_extensions import smart` to activate this namespace.
* Bugfix for `smart.rsplit()`;

### v0.0.3
* The basic structure of the package is completed, including:
  * advanced regex operations `smart.search()`, `smart.match()`, `smart.fullmatch()`, `smart.sub()`, `smart.subn()`, and `smart.split()`;
  * new regex operations `smart.rsplit()`, `smart.lsplit()`, `smart.line_findall()`, and `smart.real_findall()`;
  * string operations `counted_strip()`, `line_count()`, `line_count_iter()`, and `word_wrap()`;
  * utility classes `Smart`, `SmartPattern` and `SmartMatch`;
  * and other utility functions: `find_right_bracket()`, `find_left_bracket()`, and `pattern_inreg()`.

### v0.0.2
* Bugfix for `setup.py`.

### v0.0.1
* Initial release.