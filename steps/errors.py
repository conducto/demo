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
    # helps make your code indentation mimic the structure of the Nodes.
    with do.Serial(image=utils.IMG) as output:
        output["Show source"] = do.lazy_py(utils.print_source, do.relpath(__file__))

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


def test(service_name):
    print(f"Starting test for {service_name}")
    if not os.getenv("AUTH_TOKEN"):
        print("Must specify AUTH_TOKEN in the environment.", file=sys.stderr)
        print("- Select the 'Test' node", file=sys.stderr)
        print("- Click 'Modify' in the toolbar", file=sys.stderr)
        print("- Set 'AUTH_TOKEN' to any value you want", file=sys.stderr)
        print("- Reset errors using the toolbar", file=sys.stderr)
        raise ValueError("Missing AUTH_TOKEN")
    print()
    print(f"Got AUTH_TOKEN of {repr(os.environ['AUTH_TOKEN'])}")
    print()
    print("Good job. You just debugged and fixed an error. May all your errors be this easy to fix.")


if __name__ == "__main__":
    do.main(default=run)
