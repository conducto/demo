import conducto as co

IMG = co.Image(
    dockerfile="docker/Dockerfile.util",
    context=".",
    copy_dir=".",
    reqs_py=["conducto", "matplotlib", "numpy", "Click", "PTable"]
)
