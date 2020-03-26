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
            test_node["app"] = do.lazy_py(test_app)
            test_node["backend"] = do.lazy_py(test_backend)
            test_node["metrics"] = do.lazy_py(test_metrics)

        do.Exec("echo 'Make it so.'", name="Deploy")
    return output


def build():
    print("Building.")


def test_app():
    """
    An error that can be fixed by setting an environment variable
    """
    if not os.getenv("AUTH_TOKEN"):
        print(
            """Some errors can be fixed by changing the environment or the command.

To fix this one:
- Click 'Modify' in the toolbar")
- Under 'env', set 'AUTH_TOKEN' to any string you want.
- Reset using the toolbar"""
        )
        raise ValueError("Missing AUTH_TOKEN")
    else:
        print(
            f"""Got AUTH_TOKEN of {repr(os.environ["AUTH_TOKEN"])}

Good job. You just debugged and fixed an error by changing the environment.
May all your errors be this easy to fix."""
        )


def test_backend():
    """
    An error that can be fixed by modifying code.
    """
    # FIXME: Change this 'True' to 'False'. Yes, this error is trivial. You're welcome.
    if True:
        print(
            """Code error! Conducto has a few ways to help you fix this.
        
1. Click the 'Debug' icon (to the right of 'Command') to copy a command to your 
clipboard that launches this node in a container on your machine. All the code
and environment is there, ready for you to debug the error interactively.

2. Open this file in an editor, fix the code, and then click the 'Rebuild' icon
(next to 'Debug'). This rebuilds the Docker image for this node, grabbing your
latest code. Reset the error and now it will pass.
"""
        )
        raise Exception("Code error! See stdout for details on how to fix.")
    else:
        print(
            """You just learned 'Debug' and 'Rebuild'. We've loved using them
as we've built and debugged our build/test/deploy pipeline, and we hope you like
them too. Talk to us on Slack and let us know!"""
        )


def test_metrics():
    """
    An error that should be skipped, not fixed.
    """
    msg = "Some errors don't need to be fixed.\nPress 'Skip' in the toolbar to skip this one."
    raise Exception(msg)


if __name__ == "__main__":
    do.main(default=run)
