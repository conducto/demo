"""
# Dealing with errors

**Topics learned**
- Find errors in the Pipeline panel, and examine them in the Node panel.
- Interactively debug nodes using **conducto debug** (this is really cool!)
- Modify execution parameters to fix errors.
- Skip nodes to ignore errors.

## Motivation
Debugging errors in big pipelines is usually a terrible experience. You might get an
email that a failure happened, with an error summary that is devoid of context. Then you
have to scan through many dispersed logs to figure out what happened. There is always a
struggle to reproduce the error. Testing your fix is never easy. Lastly you restart the
pipeline and wait, hoping you don't get another error email.

We know your pain. We've been there too. Conducto was specifically designed to make
debugging easy so that you can create sophisticated pipelines that just work.

## Fast and easy debugging
Run this node and you will see three different errors in the Pipeline panel. Navigate to
them using your mouse or keyboard to expand the tree, or jump straight to it by clicking "Next Error" 
![Next Error](https://github.com/conducto/demo/raw/master/images/next_error-24px.svg?sanitize=true).

Each of the three errors illustrates a common problem. Select them one at a time and
follow their instructions to solve them.

After each one, look in the Timeline to compare the failed run with the successful one.
"""
import conducto as co
import os, sys

try:
    import utils
except ImportError:
    from . import utils


def run() -> co.Serial:
    # You can use 'with' statement (context manager) to build the pipeline. This
    # helpfully makes your code indentation mimic the structure of the Nodes.
    with co.Serial(image=utils.IMG, doc=__doc__) as output:
        co.Exec("conducto steps/errors.py build", name="Build")

        # lazy_py() makes it easy to turn a Python method-call into an Exec node. It
        # will serialize/deserialize simple arguments: it reads the method's type hints
        # and defaults, assuming 'str' otherwise.
        with co.Parallel(name="Test") as test_node:
            test_node["app"] = co.lazy_py(test_app)
            test_node["backend"] = co.lazy_py(test_backend)
            test_node["metrics"] = co.lazy_py(test_metrics)

        co.Exec("echo 'Make it so.'", name="Deploy")
    return output


def build():
    print("Building.")


def test_app():
    """
# Error #1: Bug that needs a code fix.

**Topics learned**
- Conducto debug.
- Rebuild image.

## Conducto debug
Run this node, and you'll see that the stderr shows a mysterious exception. When you
see errors like this in the real world, your first step will often be to reproduce
them in a debug environment. Conducto makes this easy. Click "Copy Debug Command" 
![Copy Debug Command](https://github.com/conducto/demo/raw/master/images/bug_report-24px.svg?sanitize=true) to copy a
command to your clipboard.

Run the command, and Conducto drops you into a container with all the code and
environment for this node, ready for you to debug the error interactively.

Think about that for a second. Exec nodes run in containers, so you now have the
*exact environment* of your command, but in an interactive shell. If you fix it here
then you can be very confident that it will work in the full pipeline.

But wait, there's more. The code on your local machine is mounted read-only into
this debug container. Make changes outside the container in your favorite editor
and your edits will automatically be visible within the container.

To fix the bug:
- Open `demo/steps/errors.py` in your editor.
- Search for `FIXME` and fix the bug.
- Run `./conducto.cmd` and follow the instructions.

### Debug - live vs snapshot
There are two modes of `conducto debug`. **Live** mode will mount your local code
read-only into the container. As you saw above this allows you to use your own
editor in your own codebase outside of the container to insert print statements and
breakpoints, or to test fixes. This will probably be your preferred mode.

Live mode requires that Conducto knows how to map a path on your local host to a path
inside the container. This is possible with any `do.Image` that specifies `context`
or `context_map`. A `context` literally specifies a path on your local host that is
copied into the image. A `context_map` explicitly maps a host path to a container path.

**Snapshot** mode uses the exact code that is in the Node's Docker image. This is possible
with any flavor of `do.Image`. You will most often use this when your `do.Image` is not 
compatible with live mode.
    """
    # FIXME: Change this 'True' to 'False'. Yes, this error is trivial. You're welcome.
    if True:
        raise Exception("Code error!")
    else:
        print(
            """
    Great job using Debug (live). You fixed the code, now you must get your fix into the
    pipeline. Click the 'Rebuild Image' button in the Node panel to rebuild the Docker image
    for this node with your latest code. Reset the error and now it will pass.""".strip()
        )


def test_backend():
    """
# Error #2: Bug that requires changing the environment or command.

Nodes often fail in ways that can be fixed by changing execution params. Maybe it didn't
get enough memory. Maybe there was in a typo in a command. In this specific case, the
command is expecting an environment variable to be specified.

To fix it:
- Click "Modify Params" ![Modify Params](https://github.com/conducto/demo/raw/master/images/tune-24px.svg?sanitize=true) in the toolbar.
- Set `env` to be `{"AUTH_TOKEN":"abc123"}` (any string will do).
- Click "Reset Selected" ![Reset Selected](https://github.com/conducto/demo/raw/master/images/settings_backup_restore-24px.svg?sanitize=true) in the toolbar.

### Sidebar: Design pattern to manually approve config changes
DevOps can often involve automated application of configurations. Very important
deployments can require having a human in the loop for certain changes.

A common Conducto pattern is to error if an important config does not match, and
to commit the change when an environment variable is set. For example:

```python
def deploy(commit=do.envbool("COMMIT")):
    if config_is_different():
        print(diff_summary())
        if commit:
            commit_changes()
        else:
            raise Exception()
    else:
        print("No changes.")
```

The Pipeline panel makes it easy to cycle through these errors, and the Node panel
lets you quickly scan the differences and commit the ones that are okay by setting
the environment variable `COMMIT=True`.
    """
    if not os.getenv("AUTH_TOKEN"):
        raise ValueError("Missing AUTH_TOKEN")
    else:
        print(
            f"""Got AUTH_TOKEN of {repr(os.environ["AUTH_TOKEN"])}

    Good job. You just debugged and fixed an error by changing the environment.
    May all your errors be this easy to fix."""
        )


def test_metrics():
    """
# Error #3: An error that should be skipped, not fixed.

Many errors are insignificant and you can skip them without bothering to fix them. For
example:
- In a CI/CD pipeline, you have a transient failure in a unit test for code that you
  didn't touch. Long term you should really fix that, but right now you just want to run
  your tests, so skip the failure to move along.
- In a machine learning pipeline, you have 10,000 nodes that compute features on
  different input data. 9950 of them succeed, with 50 weird failures. Some of the
  failures should be fixed, but others represent bad data that should be excluded from
  the dataset. Either way, you have enough features to build a good model, so skip
  the errors to move on to the next step in the pipeline.

Press "Skip" ![Skip](https://github.com/conducto/demo/raw/master/images/skip_next-24px.svg?sanitize=true) to skip this one.

Need to skip many errors at once? Expand the dropdown under Skip/Unskip and select
Skip Errors to skip all errored nodes underneath the selected one(s).
"""
    raise Exception("Error, missing data.")


if __name__ == "__main__":
    co.main(default=run)
