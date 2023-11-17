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
