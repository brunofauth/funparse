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
