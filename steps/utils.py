import conducto as do

IMG = do.Image(context="..")


def print_source(file):
    """
    Print the contents of the given file.
    """
    with open(file) as f:
        print(f.read())
