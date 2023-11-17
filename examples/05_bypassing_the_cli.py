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
