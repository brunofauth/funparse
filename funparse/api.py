from __future__ import annotations

import contextlib
from collections.abc import Callable, Sequence, Iterable
from inspect import Parameter
from types import GenericAlias, UnionType
from typing import ParamSpec, TypeVar, Self, Generic, Any, Annotated
import enum
import argparse as ap
import functools
import inspect
import builtins
import typing
import sys

try:
    from typing import Doc
except ImportError:
    from typing_extensions import Doc

with contextlib.suppress(ImportError):
    import docstring_parser as dp   # type: ignore

P = ParamSpec("P")
T = TypeVar("T")
U = TypeVar("U")
Constructor = Callable[[T], U]

__all__ = [
    "ArgumentParser",
    "as_arg_parser",
    "Command",
    "Enum",
    "DocstringStyle",
]


class ArgumentParser(ap.ArgumentParser):
    """Wrapper around 'argparse.ArgumentParser' in which 'self.error' \
       doesn't call 'sys.exit'"""

    def error(self, message: str):
        """error(message: string)

        Prints a usage message incorporating the message to stderr and
        exits.

        If you override this in a subclass, it should not return -- it
        should either exit or raise an exception.
        """
        raise RuntimeError(f'{self.prog}: error: {message}')


def _is_documentation_annotation(obj: object) -> bool:
    return obj.__class__.__name__ == "Doc"


def _first(iterable: Iterable[T], pred: Callable[[T], bool]) -> T | None:
    """Returns either None or the first item for which pred(item) is true."""
    return next(filter(pred, iterable), None)   # type: ignore


def make_argument_name(base_name: str, optional: bool) -> str:
    if optional:
        return "--" + base_name.replace("_", '-')
    return base_name


def johnny_simple(
    in_type: type,
    default_val: Any,
) -> tuple[str, Constructor, list[str] | None]:
    match (in_type, default_val):
        case (builtins.bool, True):
            return "store_false", bool, None
        case (builtins.bool, False):
            return "store_true", bool, None
        case (builtins.bool, Parameter.empty):
            return "store", _bool_from_str, None
        case (enum.EnumType() as enum_type, _):
            return (
                "store",
                functools.partial(_enum_from_str, enum_type),
                list(enum_type),
            )
        case (some_type, _) if some_type in (int, float, str):
            return "store", some_type, None
        case _:
            raise RuntimeError(f"unsupported type: {in_type!r}")
    return ()   # type: ignore


def johnny_generic(
    in_type: GenericAlias,
    default_val: Any,
) -> tuple[str, type, list[str] | None]:
    match (typing.get_origin(in_type), typing.get_args(in_type), default_val):
        case (seq, [single_type], _) if issubclass(seq, Sequence):
            return "append", single_type, None
        case _:
            raise RuntimeError(f"unsupported generic type: {in_type!r}")
    return ()   # type: ignore


def _bool_from_str(word: str) -> bool:
    match word.lower():
        case "y" | "yes" | "true" | "1":
            return True
        case "n" | "no" | "false" | "0":
            return False
        case _:
            raise ValueError(f"invalid value for boolean: {word!r}")


def _enum_from_str(enum_type: type[enum.Enum], word: str) -> enum.Enum:
    with contextlib.suppress(KeyError):
        return enum_type[word]
    with contextlib.suppress(KeyError):
        return enum_type[word.upper()]
    raise ValueError(f"no name {word!r} in {enum_type!r}")


def _is_optional_type(raw_type: UnionType) -> bool:
    return len(raw_type.__args__) == 2 and type(None) in raw_type.__args__


def _unwrap_optional_type(opt: UnionType) -> type:
    return opt.__args__[opt.__args__.index(type(None)) - 1]


def _make_parser(
    fn: Callable[P, T],
    ignore: Sequence[str] | None,
    parser_type: type[ap.ArgumentParser],
    parse_docstring: DocstringStyle | None,
) -> tuple[ap.ArgumentParser, str | None]:
    if parse_docstring is None:
        description = fn.__doc__
        arg_help = {}
    elif "docstring_parser" not in sys.modules:
        raise ModuleNotFoundError("docstring_parser")
    else:
        docstring = dp.parse(fn.__doc__, parse_docstring._to_dp())
        description = docstring.long_description or docstring.short_description
        arg_help = {p.arg_name: p.description for p in docstring.params}

    parser = parser_type(description=description, exit_on_error=False)
    signature = inspect.signature(fn)
    vararg_name = None

    for name, body in signature.parameters.items():
        if ignore is not None and name in ignore:
            continue
        raw_type = body.annotation
        default = body.default

        if isinstance(raw_type, UnionType):
            if not _is_optional_type(raw_type):
                raise TypeError(f"unsupported union: {raw_type!r}")
            raw_type = _unwrap_optional_type(raw_type)
            if default is Parameter.empty:
                default = None

        match raw_type:
            case Parameter.empty:
                raise SyntaxError(f"untyped parameters are not supported: {name!r}")
            case type():
                action, _type, choices = johnny_simple(raw_type, default)
            case alias if typing.get_origin(alias) is Annotated:
                inner_type, *other_type_args = typing.get_args(alias)
                action, _type, choices = johnny_simple(inner_type, default)
                doc_annotation = _first(other_type_args, _is_documentation_annotation)
                if doc_annotation is not None:
                    arg_help[name] = doc_annotation.documentation
                raw_type = inner_type   # for help message generation
            case GenericAlias():
                action, _type, choices = johnny_generic(raw_type, default)

        add_arg_params = {}
        if default is not Parameter.empty:
            add_arg_params["default"] = default

        match action:
            case "append":
                add_arg_params["choices"] = choices
                add_arg_params["type"] = _type
            case "store":
                add_arg_params["choices"] = choices
                add_arg_params["type"] = _type
            case "store_true" | "store_false":
                pass
            case other:
                raise ValueError(f"unsupported action: {other!r}")

        if body.kind == Parameter.VAR_POSITIONAL:
            add_arg_params["nargs"] = "+"
            vararg_name = name

        type_name = raw_type.__name__
        help_type = f"{type_name}[{_type}]" if isinstance(raw_type, GenericAlias) else type_name
        match (arg_help.get(name, None), default):
            case (None, Parameter.empty):
                add_arg_params["help"] = f"{help_type}"
            case (None, default_value):
                add_arg_params["help"] = f"{help_type} (default={default_value})"
            case (help_str, Parameter.empty):
                add_arg_params["help"] = f"{help_type}: {help_str}"
            case (help_str, default_value):
                add_arg_params["help"] = f"{help_type} (default={default_value}): {help_str}"

        added_arg = parser.add_argument(
            make_argument_name(name, default is not Parameter.empty),
            action=action,
            **add_arg_params,
        )

    return parser, vararg_name


@typing.overload
def as_arg_parser(
    fn: Callable[P, T],
    ignore: Sequence[str] | None = None,
    parser_type: type[ap.ArgumentParser] = ap.ArgumentParser,
    parse_docstring: DocstringStyle | None = None,
) -> Command[P, T]:
    ...


@typing.overload
def as_arg_parser(
    fn: None = None,
    ignore: Sequence[str] | None = None,
    parser_type: type[ap.ArgumentParser] = ap.ArgumentParser,
    parse_docstring: DocstringStyle | None = None,
) -> Callable[[Callable[P, T]], Command[P, T]]:
    ...


def as_arg_parser(
    fn: Callable[P, T] | None = None,
    ignore: Sequence[str] | None = None,
    parser_type: type[ap.ArgumentParser] = ArgumentParser,
    parse_docstring: DocstringStyle | None = None,
) -> Command[P, T] | Callable[[Callable[P, T]], Command[P, T]]:
    if fn is not None:
        return as_arg_parser_inner(
            fn=fn,
            ignore=ignore,
            parser_type=parser_type,
            parse_docstring=parse_docstring,
        )

    return functools.partial(
        typing.cast(Callable[..., Command[P, T]], as_arg_parser_inner),
        ignore=ignore,
        parser_type=parser_type,
        parse_docstring=parse_docstring,
    )


def as_arg_parser_inner(
    fn: Callable[P, T],
    ignore: Sequence[str] | None,
    parser_type: type[ap.ArgumentParser],
    parse_docstring: DocstringStyle | None,
) -> Command[P, T]:
    parser, vararg_name = _make_parser(
        fn=fn,
        ignore=ignore,
        parser_type=parser_type,
        parse_docstring=parse_docstring,
    )
    return Command(
        fn=fn,
        parser=parser,
        vararg_name=vararg_name,
    )


class Command(Generic[P, T]):
    __slots__ = [
        "_state",
        "_fn",
        "_parser",
        "_vararg_name",
        "print_usage",
        "print_help",
        "format_usage",
        "format_help",
    ]

    def __init__(
        self,
        fn: Callable[P, T],
        parser: ap.ArgumentParser,
        vararg_name: str | None = None,
        state: dict[str, Any] | None = None,
    ) -> None:
        self._fn = fn
        self._parser = parser
        self._vararg_name = vararg_name
        self._state = state or {}
        self.print_usage = parser.print_usage
        self.print_help = parser.print_help
        self.format_usage = parser.format_usage
        self.format_help = parser.format_help

    def with_state(self: Self, **kwargs) -> Command[P, T]:
        self._state = kwargs
        return Command(
            fn=self._fn,
            parser=self._parser,
            state=kwargs,
            vararg_name=self._vararg_name,
        )

    def run(self: Self, cmd_args: list[str]) -> T:
        parsed_args = vars(self._parser.parse_args(cmd_args))
        if self._vararg_name is not None:
            varargs = parsed_args.pop(self._vararg_name)
        else:
            varargs = ()

        return self._fn(
            *varargs,
            **self._state,
            **parsed_args,
        )

    def show_help(self) -> None:
        self.run(["--help"])


class Enum(enum.Enum):
    """Subclass of 'enum.Enum' with a CLI-friendly '__str__'"""

    def __str__(self) -> str:
        return self.name


class DocstringStyle(Enum):
    AUTO = enum.auto()
    REST = enum.auto()
    GOOGLE = enum.auto()
    NUMPYDOC = enum.auto()
    EPYDOC = enum.auto()

    def _to_dp(self):

        match self:
            case DocstringStyle.AUTO:
                return dp.DocstringStyle.AUTO
            case DocstringStyle.REST:
                return dp.DocstringStyle.REST
            case DocstringStyle.GOOGLE:
                return dp.DocstringStyle.GOOGLE
            case DocstringStyle.NUMPYDOC:
                return dp.DocstringStyle.NUMPYDOC
            case DocstringStyle.EPYDOC:
                return dp.DocstringStyle.EPYDOC
            case _:
                raise NotImplementedError("Can't convert DocstringStyle")
