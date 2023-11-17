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
