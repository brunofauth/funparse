# Introduction

`funparse` allows you to "derive" an argument parser (such as those from 
[argparse](https://docs.python.org/3/library/argparse.html)) from type 
annotations of a function's signature, cutting down on the boilerplate code. 
It's similar to [fire](https://github.com/google/python-fire) in this way, but 
it's more lightweight and designed in a way to give its user more control over 
what is going on.


**Disclaimer:** your user experience may be much richer if you're using a 
static type checker, such as [mypy](https://mypy-lang.org/)


# Installation

With pip:

    pip install funparse[docstring]

With poetry:
    
    poetry install funparse[docstring]

If you don't need to generate per-argument help strings, you can omit the 
`[docstring]` extra when installing this package.


# Examples

## Basic Usage

```python
import sys
import funparse.api as fp


@fp.as_arg_parser
def some_parser_name(
    your_name: str,
    your_age: int,
    pets: list[str] | None = None,
    loves_python: bool = False,
) -> None:
    print("Hi", your_name)

    if pets is not None:
        for pet in pets:
            print("send greetings to", pet, "for me")

    if loves_python:
        print("Cool! I love python too!")


# Run the parser on this set of arguments
some_parser_name.run([
    "Johnny",
    "33",
    *("--pets", "Goofy"),
    *("--pets", "Larry"),
    *("--pets", "Yes"),
    "--loves-python",
])

# You can also use args from the command line
some_parser_name.run(sys.argv)
```

## Printing Help

```python
import funparse.api as fp


@fp.as_arg_parser
def some_parser_name(
    your_name: str,
    your_age: int,
) -> None:
    print("Hi", your_name)
    if your_age > 325:
        print("getting elderly, eh")


# You can print help and usage information like this:
some_parser_name.print_usage()
some_parser_name.print_help()
# These work just like they do on 'argparse.ArgumentParser'

# You can also format this information into strings
usage = some_parser_name.format_usage()
help_str = some_parser_name.format_help()
```

[See more about it 
here](https://docs.python.org/3/library/argparse.html#printing-help)


## Behavior on Booleans

```python
import funparse.api as fp


@fp.as_arg_parser
def booler(
    # This is a positional argument
    aaa: bool,

    # This is a flag which, if present, will set 'bbb' to False
    bbb: bool = True,

    # This is a flag which, if set, will set 'ccc' to True
    ccc: bool = False,
) -> None:
    print(aaa, bbb, ccc)


# This will print: True, False, False
booler.run([
    "yes",  # 'y', 'true', 'True' and '1' will also work
    "--bbb",
])

# This will print: False, True, False
booler.run([
    "false",  # 'n', 'no', 'False' and '0' will also work
])
```


## Behavior on Enums

```python
import funparse.api as fp
import enum


# This Enum functionality will work better if you use SCREAMING_SNAKE_CASE for
# the names of your enum members (if you don't, your CLI will work in a
# case-sensitive way :P)
class CommandModes(fp.Enum):  # You can use enum.Enum and similar classes too
    CREATE_USER = enum.auto()
    LIST_USERS = enum.auto()
    DELETE_USER = enum.auto()


@fp.as_arg_parser
def some_parser(mode: CommandModes) -> None:
    print(f"you picked {mode.name!r} mode!")


some_parser.run(["CREATE_USER"])  # This is valid...
some_parser.run(["create_user"])  # ...so is this...
some_parser.run(["crEatE_usEr"])  # ...and this too...

# This raises an error
some_parser.run(["NON EXISTING FUNCTIONALITY EXAMPLE"])
```

## Bypassing the command-line

If you want to pass extra data to the function which you're using as your 
parser generator, but without having to supply this data through the CLI, you 
can use the `ignore` parameter on `as_arg_parser`, like this:

```python
import funparse.api as fp


@fp.as_arg_parser(ignore=["user_count", "user_name"])
def some_parser(
    user_count: int,
    user_name: str,
    user_address: str,
    is_foreigner: bool = False,
) -> None:
    print(f"you're the {user_count}th user today! welcome, {user_name}")
    print("They say", user_address, "is lovely this time of the year...")


# These 'state-variables' must be passed as keyword args (or through **kwargs)
some_parser.with_state(
    user_count=33,
    user_name="Josh",
).run(["some address..."])

# If you want, you can cache these parser-with-state objects. It sort of
# reminds me of 'functools.partial'
saving_for_later = some_parser.with_state(
    user_count=33,
    user_name="Josh",
)

# Later:
saving_for_later.run([
    "some address...",
    "--is-foreigner",
])
```


## Using custom argument parsers

```python
import argparse
import funparse.api as fp


# First, subclass 'argparse.ArgumentParser'
class MyParser(argparse.ArgumentParser):
    """Just like argparse's, but better!"""


# Then, pass your parser as an argument to 'as_arg_parser'
@fp.as_arg_parser(parser_type=MyParser)
def some_parser(
    user_name: str,
    is_foreigner: bool = False,
) -> None:
    print("Welcome", user_name)
    if is_foreigner:
        print("Nice to have you here")


# Finally, run your parser. It all works as expected!
some_parser.run([
    "johnny",
    "--is-foreigner",
])
```

## Generating per-argument help strings from docstrings

Thanks to [this package](https://github.com/rr-/docstring_parser), `funparse` 
can generate `help` strings for arguments, from the docstring of the function 
in question, like this:

```python
import funparse.api as fp


@fp.as_arg_parser(parse_docstring=fp.DocstringStyle.GOOGLE)
def some_parser(
    name: str,
    is_foreigner: bool = False,
) -> None:
    """My awesome command.

    Long description... Aut reiciendis voluptatem aperiam rerum voluptatem non. 
    Aut sit temporibus in ex ut mollitia. Omnis velit asperiores voluptatem ut 
    molestiae quis et qui.

    Args:
        name: some help information about this arg
        is_foreigner: some other help information
    """
    print("Welcome", name)
    if is_foreigner:
        print("Nice to have you here")


some_parser.print_help()
```

The generated command help should look like this:

```
usage: - [-h] [--is-foreigner] name

Long description... Aut reiciendis voluptatem aperiam rerum voluptatem non.
Aut sit temporibus in ex ut mollitia. Omnis velit asperiores voluptatem ut
molestiae quis et qui.

positional arguments:
  name            some help information about this arg

options:
  -h, --help      show this help message and exit
  --is-foreigner  bool (default=False): some other help information
```


## Generating per-argument help strings type annotations

As of PEP 727, there's a new way to document information for parameters, aside
from docstrings, which is the `Doc(...)` type, supposed to be used with
`typing.Annotated`. This way of documenting is supported by funparse, so that
you can auto-generate help string for each argument, from these annotations,
like the example below shows:

```python
import funparse.api as fp
from typing import Annotated
from typing_extensions import Doc


# You don't need to parse docstrings to have your Doc annotations to work, but
# I'll use this feature here to show how it interacts with Annotated[T, Doc(...)]
@fp.as_arg_parser(parse_docstring=fp.DocstringStyle.GOOGLE)
def some_parser_name(
    param_1: int,
    param_2: int,
    param_3: Annotated[int, Doc("this is only documented here")],
    param_4: Annotated[int, Doc("this is documented here and in the docstring")],
) -> None:
    """Some short description

    Some long description Dolorem ut illum in dolorum eaque maxime dignissimos.
    Tempora provident eum sit. Modi voluptatibus dignissimos occaecati qui
    quisquam minus quis et.

    Args:
        param_2: this is only documented in the docstring
        param_4: this is documented both in the docstring and as an annotation
    """
    print(param_1)
    print(param_2)
    print(param_3)
    print(param_4)


some_parser_name.print_help()
```


## Variadic Positional Arguments

You can use the star notation in a function's signature to specify that the
argument in question should take in one or more parameters. If you want your
function's parameter to allow zero or more items, consider defining, in your
functions signature, a parameter of type `list[T] | None` with a default value
of `None`, as shown in './examples/01_basic_usage.py' or in the above section
titled "Basic Usage".

```python
import funparse.api as fp


@fp.as_arg_parser
def some_parser_name(
    *pet_names: str,  # Here's the aforementioned star notation
    your_name: str = "John",
) -> None:
    print("Hi", your_name)
    for pet_name in pet_names:
        print("send greetings to", pet_name, "for me")


# Run the parser on this set of arguments
some_parser_name.run([
    "Goofy",
    "Larry",
    "Yes",
    "--your-name",
    "Johnny",
])
```


# Extras

Beyond `as_arg_parser`, this module also ships:

- `funparse.Enum`, which is a subclass of `enum.Enum`, but with a `__str__` 
  that better fits your CLI apps
- `funparse.ArgumentParser`, which is a subclass of `argparse.ArgumentParser` 
  that, unlike the latter, does not terminate your app on (most) exceptions

Have fun!

