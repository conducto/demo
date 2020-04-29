import conducto as co

IMG = co.Image("python:3.8", copy_dir=".", reqs_py=[
    "conducto", "matplotlib", "blockchain", "click", "pandas", "tabulate",
])