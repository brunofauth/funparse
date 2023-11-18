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
