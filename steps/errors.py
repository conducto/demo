"""
Teach how to debug and fix errors in the app.
"""
import conducto as do
import os, sys

try:
    import utils
except ImportError:
    from . import utils

ENV_ERROR_MESSAGE = """<ConductoMarkdown>Some errors can be fixed by changing the environment or the command.
To fix this one:

- Click ![Modify](https://github.com/conducto/demo/raw/master/images/modify.png) in the toolbar.
- Under 'Env', set AUTH_TOKEN like this: `{"AUTH_TOKEN":"any_string_you_want"}`.
- Click ![Reset](https://github.com/conducto/demo/raw/master/images/reset.png) in the toolbar.</ConductoMarkdown>"""

ENV_SUCCESS_MESSAGE = """Got AUTH_TOKEN of {}

Good job. You just debugged and fixed an error by changing the environment.
May all your errors be this easy to fix."""

CODE_ERROR_MESSAGE = """<ConductoMarkdown>Code error!

To dig in further:
- Click ![Debug](https://github.com/conducto/demo/raw/master/images/debug.png) to copy a command to your clipboard.
- Paste and run in a shell to drop into a container with all the code and
  environment for this node, ready for you to debug the error interactively.
- Follow the instructions to install your favorite editor.
- Open `steps/errors.py` in your editor.
- Search for `FIXME` and fix the bug.
- Run `./conducto.cmd` and follow the instructions.</ConductoMarkdown>"""

DEBUG_SUCCESS_MESSAGE = """<ConductoMarkdown>
Great job using 'Debug'. Now quit this container and in an editor open this file
(`demo/steps/error.py`). Make the same fix and then click the 'Rebuild' icon (next
to 'Debug'). This rebuilds the Docker image for this node, grabbing your
latest code. Reset the error and now it will pass.

Once you're done, you'll have learned 'Debug' and 'Rebuild'. We've loved using
them as we've built and debugged our build/test/deploy pipeline, and we hope you
like them too. Talk to us on [Slack](https://conductohq.slack.com) and let us know!
</ConductoMarkdown>"""

SKIP_MESSAGE = """<ConductoMarkdown>
Some errors don't need to be fixed.

Press ![Skip](https://github.com/conducto/demo/raw/master/images/skip.png) to skip this one.
</ConductoMarkdown>"""

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
        print(ENV_ERROR_MESSAGE)
        raise ValueError("Missing AUTH_TOKEN")
    else:
        print(ENV_SUCCESS_MESSAGE.format(os.environ["AUTH_TOKEN"]))


def test_backend():
    """
    An error that can be fixed by modifying code.
    """
    # FIXME: Change this 'True' to 'False'. Yes, this error is trivial. You're welcome.
    if True:
        print(CODE_ERROR_MESSAGE)
        raise Exception("Code error! See stdout for details on how to fix.")
    else:
        print(DEBUG_SUCCESS_MESSAGE)


def test_metrics():
    """
    An error that should be skipped, not fixed.
    """
    raise Exception(SKIP_MESSAGE)


if __name__ == "__main__":
    do.main(default=run)
