import conducto as co

IMG = co.Image("python:3.8-alpine", context="..", reqs_py=["conducto"])


def print_source(file):
    """
    Print the contents of the given file.
    """
    if file.endswith(".py"):
        lang = "python"
    elif "Dockerfile" in file:
        lang = "docker"
    else:
        lang = ""
    print("<ConductoMarkdown>")
    print(f"```{lang}")
    with open(file) as f:
        print(f.read())
    print("```")
    print("</ConductoMarkdown>")
