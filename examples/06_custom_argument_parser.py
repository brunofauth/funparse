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
