import conducto as do

IMG = do.Image("python:3.8-alpine", context="..", reqs_py=["conducto"])


def print_source(file):
    """
    Print the contents of the given file.
    """
    with open(file) as f:
        print(f.read())
