![Run tests](https://github.com/csm10495/pynom/workflows/Run%20tests/badge.svg) [![PyPI version](https://badge.fury.io/py/pynom.svg)](https://badge.fury.io/py/pynom)

# PyNom

A simple library to eat exceptions, until enough of a given exception type has been raised. The name has the word 'Nom' in it because it can sometimes sound like a person eating.

# Installation
```
pip install pynom
```

# Simple Usage Example
```
from pynom import PyNom
pn = PyNom([ValueError], 5)
while True:
    # This block will raise after 5 (so on the 6th) ValueErrors.
    #  It will raise an Exception containing tracebacks, exceptions, approx timestamps for each ValueError
    # If a non-ValueError is raised, it will be immediately raised (and not eaten)
    with pn:
        do_something()
```
See [https://csm10495.github.io/pynom/](https://csm10495.github.io/pynom/) for full API documentation.

## License
MIT License