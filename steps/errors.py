"""
Teach how to debug and fix errors in the app.
"""
import conducto as do
import os, sys

try:
    import utils
except ImportError:
    from . import utils


def run() -> do.Serial:
    # You can use 'with' statement (context manager) to build the pipeline. This
    # helpfully makes your code indentation mimic the structure of the Nodes.
    with do.Serial(image=utils.IMG) as output:
        output["Show source"] = do.lazy_py(
            utils.print_source, do.relpath(os.path.abspath(__file__))
        )

        do.Exec("conducto steps/errors.py build", name="Build")

        # lazy_py() makes it easy to turn a Python method-call into an Exec node. It
        # will serialize/deserialize simple arguments: it reads the method's type hints
        # and defaults, assuming 'str' otherwise.
        with do.Parallel(name="Test") as test_node:
            for service_name in ["app", "backend", "metrics"]:
                test_node[service_name] = do.lazy_py(test, service_name)

        do.Exec("echo 'Make it so.'", name="Deploy")
    return output


def build():
    print("Building.")


ERROR_MSG = """Must specify AUTH_TOKEN in the environment.
- Select the 'Test' node
- Click 'Modify' in the toolbar
- Set 'AUTH_TOKEN' to any value you want
- Reset errors using the toolbar"""

SUCCESS_MSG = """Got AUTH_TOKEN of {}

Good job. You just debugged and fixed an error. May all your errors be this easy to fix."""


def test(service_name):
    print(f"Starting test for {service_name}")
    if not os.getenv("AUTH_TOKEN"):
        print(ERROR_MSG, file=sys.stderr)
        raise ValueError("Missing AUTH_TOKEN")
    print(SUCCESS_MSG.format(repr(os.environ["AUTH_TOKEN"])))


if __name__ == "__main__":
    do.main(default=run)
