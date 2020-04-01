"""
# Use case: CI+CD testing

**Topics learned**
- Define the image for your nodes.
- Specify nodes to run in a single container.
- Allow nodes to run Docker commands.
- Implement a try/finally to ensure that cleanup nodes run.

## CI/CD pipelines
Continuous Integration, Continuous Delivery (CI/CD) pipelines can take many forms, but
typically all include some basic steps: Build, Test, Deploy. Implementing this at a high
level should be familiar if you have seen the previous steps, so this use cases focuses
on a low-level portion of a CI/CD pipeline, testing a microservice.

This example deploys and tests a containerized Redis server in three steps:
- 'Setup' starts the container.
- 'Test' runs a few tests against it.
- 'Stop' stops the container.

Simple enough. Let's learn some features of Conducto that help with this.

## Images
Until now all Exec nodes have been simple shell commands or Python calls, but there is
much more to the world than just Python and Bash. Conducto lets you specify the Docker
image for your Exec nodes in a variety of ways, making it easy to run any command you
need.

In case you're unfamiliar with the concept, a Docker image is a template for an
execution environment that defines the base OS and file system contents, which often
include programming languages, packages, and user code. A Docker container is a running
instantiation of a Docker image. It is like a Virtual Machine, but a container is more
lightweight and faster to create/destroy then a VM.

Every Exec node needs to have an `image` defined. The default image is Docker's standard
`python` of the same version you're using.
[`co.Image`](https://conducto.com/docs/#do-image) provides a few common ways to
customize it by setting `co.Exec("...", image=co.Image(...))`.
- **Novice** `co.Image("python:3.8", context=".", reqs_py=["numpy"])`: Start with the Docker image
  `python:3.8`. Include all the code at `.`, that is, in the same directory as this
  file. Then `pip install numpy`. This is easiest to use if you're unfamiliar with
  Docker.
  - `co.Image("python:3.8", context_url="...", context_branch="..."): Same behavior as
    above, but includes code from the git repo at `context_url`. This is very useful for
    CI/CD, as it lets you run code from a specific commit. More to come on this topic in a
    later demo step.
- **Intermediate** `co.Image(dockerfile="../Dockerfile"): Specify a custom Dockerfile,
  which Conducto will build automatically. This method is used by this node; see "Show
  dockerfile" for more details.
- **Advanced** `co.Image("my_custom_image")`: If you are already a Docker expert and
  already have your own images built, specify it here.

All but the last one support the "Rebuild Image" debugging functionality. Only the first
one supports the "Conducto debug (live)" functionality.

## Docker from Exec nodes
Select this node's child named "Setup" for more information on running Docker from Exec
nodes.

## Container
Visit "Test" for more information on how Exec nodes use Containers.

## Try/finally
Look at "Stop" to learn how to ensure that cleanup steps shall always run, regardless of
previous errors.
"""
import conducto as co
import os
import subprocess

try:
    import utils
except ImportError:
    from . import utils


SETUP_DOC = """
# Docker from Exec nodes
Docker is not recursive and does not support containers-within-containers. Enabling Exec
nodes to run Docker commands incurs additional overhead so Conducto leaves this feature
disabled by default.

In this setup step we start a containerized Redis server. To enable this, we run
`co.Exec("...", requires_docker=True)`. Easy.
"""

TEST_DOC = """
# Containers

Each Exec node runs in a container, but sometimes multiple Exec nodes may share a single
container. Conducto provides a few modes for controlling this behavior.

## Default: each Exec node usually gets its own container
Normally, Conducto runs each Exec node in its own container. For efficiency reasons it
may reuse a container - if one Exec node finishes and another in the queue is compatible
with the now-available container, Conducto will assign one from the queue to the
container.

If you expect all your Exec nodes to run independently and not to destructive modify the
state of their container, this is a great default choice.

## Run Exec nodes in a single container
Cases do exist where you want to build up local state over the course of a few nodes.
This test, for example, starts by installing redis for Python into the container, then
uses the newly installed package to read and write data to a redis-server. These steps
must all run in the same container, or else the read & write steps will not have the
redis package installed.

To instruct Conducto that these nodes must share a container, set 
`same_container=co.SameContainer.NEW` - create a new "same container" context. All
child nodes below this that have the default of `co.SameContainer.INHERIT` will share
this container.

```python
with co.Serial(same_container=co.SameContainer.NEW) as test:
    test["Install"] = co.Exec("pip install redis")
    test["Write"] = co.Exec("...")
    test["Read"] = co.Exec("...")
```

Another use of `SameContainer.NEW` is to start a server inside the Exec node's container
in one Exec node, and then run a test against it from the next Exec node. You could
instead put these commands in a single Exec node, connected with `&&`. However,
separating them into multiple Exec nodes improves clarity by giving you separate outputs
for each command, making debugging easier.

Note: you can also use this if you just want to disable container reuse and ensure that
each Exec node gets its own container. 
"""
## TODO: Add doc for SameContainer.ESCAPE
# Exit the same-container context to give Exec nodes their own containers

STOP_DOC = """
# Try/finally
By default, Serial nodes stop upon any of their child nodes failing. Disabling this
behavior can be helpful for ensuring that a cleanup node will always run.

In this example, Teardown will always run, even if Setup or Test fail, similar to
Python's try/finally blocks.
```python
with co.Serial(stop_on_error=False) as output:
    with co.Serial(name="Setup and test"):
        output["Setup"] = co.Exec("...")
        output["Test"] = co.Exec("...")
    output["Teardown"] = co.Exec("...")
```
"""


def run() -> co.Serial:
    print(f"<ConductoMarkdown>{__doc__}</" "ConductoMarkdown>")
    output = co.Serial(
        image=co.Image(dockerfile="Dockerfile-testing"),
        stop_on_error=False,
        doc=__doc__,
    )
    output["Show dockerfile"] = co.lazy_py(
        utils.print_source, co.relpath("Dockerfile-testing")
    )

    output["Setup"] = co.Exec(
        "docker run -p 6379:6379 -d --rm --name conducto_demo_redis redis:alpine",
        requires_docker=True,
        doc=SETUP_DOC,
    )
    output["Test"] = co.Serial(same_container=co.SameContainer.NEW, doc=TEST_DOC)
    output["Test/Install"] = co.Exec("pip install redis")
    output["Test/Write"] = co.lazy_py(write, key="hello", value=b"world")
    output["Test/Read"] = co.lazy_py(read, key="hello", expected=b"world")
    output["Stop"] = co.Exec(
        "docker kill conducto_demo_redis || true", requires_docker=True, doc=STOP_DOC
    )
    return output


def write(key, value: bytes):
    import redis

    r = redis.Redis(host=get_internal_host(), port=6379, db=0)
    print(f"Setting {repr(key)}=>{repr(value)}")
    r.set(key, value)
    print(f"Getting {repr(key)}")
    v = r.get(key)
    assert (
        v == value
    ), f"Mismatch when getting just-set value. Expected {repr(value)} but got {repr(v)}"
    print("Passed")


def read(key, expected: bytes):
    import redis

    r = redis.Redis(host=get_internal_host(), port=6379, db=0)
    print(f"Getting {repr(key)}")
    value = r.get(key)
    print(f"Got {repr(value)}, expected {repr(expected)}")
    assert value == expected, f"Value ({repr(value)} != expected ({repr(expected)})"


def get_internal_host():
    p = subprocess.run(
        "ip route show default | awk '/default/{print $3}'",
        shell=True,
        capture_output=True,
    )
    return p.stdout.decode("utf-8").strip()


if __name__ == "__main__":
    co.main(default=run)
