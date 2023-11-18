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
    
    # The information from these annotations take precedence over those defined
    # in the docstring, overwriting them.
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
