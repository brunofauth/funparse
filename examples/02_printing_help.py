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
