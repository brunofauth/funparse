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

# You can also use args from the shell's command line, like this (it's
# equivalent to passing sys.argv[1:] as argument)
some_parser_name.run()
