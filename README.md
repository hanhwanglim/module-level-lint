# Module Level Lint

A Flake8 plugin to enforce code quality by checking module level docstrings, future-imports, and module level dunders as specified in [PEP 8](https://peps.python.org/pep-0008/#module-level-dunder-names)

## Installation

You can install this plugin via pip:

```bash
pip install module-level-lint
```

## Usage

After installation, you can use this plugin with the `flake8` command. Here's how to run it:

```bash
flake8 [path]
```

To show only module level lint errors, run:

```bash
flake8 --select MLL [path]
```

To show only specific errors

```bash
flake8 --select MLL001,MLL002 [path]
```

## Features

### Module Docstring Check: Ensure that your docstrings are always at the top of the file

- Linting Error: **MLL001**

Example:

```python
import random

# Bad: Module docstring is not at the top of the file
"""This is a docstring"""

def foo():
    pass
```

```python
# Good: Docstring present at the top of the file
""" This is a docstring. """

def foo():
    pass
```

### Future-Imports Check: Ensure that future-imports are always at the top after module docstrings

- Linting Error: **MLL002**

Example:

```python
import random

# Bad: Future-imports is not at the top of the file
from __future__ import print_function
```

```python
# Good: Future-imports is at the top of the file
from __future__ import division

import random
```

- Linting Error: **MLL003**

Example:

```python
from __future__ import print_function

# Bad: Docstring is not at the top of the file
"""This is a docstring."""
```

```python
"""This is a docstring."""

# Good: Future-imports is at the top of the file after docstring
from __future__ import division
```

### Module-Level Dunders: Ensure that module level dunders are always at the top after future-imports or docstrings

- Linting Error: **MLL004**

Example:

```python
import random

# Bad: Module level dunder after imports
__all__ = ["foo"]

def foo():
    pass
```

```python
# Bad: Module level dunder before docstring
__all__ = ["foo"]

"""This is a docstring"""

def foo():
    pass
```

```python
def foo():
    pass

# Bad: Module level dunder after code
__all__ = ["foo"]
```

```python
# Good: Module level dunder at the top of the file
__all__ = ["foo"]

def foo():
    pass
```

## Configuration

This plugin doesn't require any specific configuration, but you can include its error codes in your Flake8 configuration file to disable or enable specific checks:

```ini
[flake8]
extend-ignore = MLL001, MLL002, MLL003, MLL004
```

## Contributing

Contributions, issues, and feature requests are welcome! Please feel free to submit a pull request or open an issue.

## License

This plugin is licensed under the MIT License.
