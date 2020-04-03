"""
**Topics learned**
- Define the image for your nodes.
- Specify nodes to run in a single container.
- Allow nodes to run Docker commands.
- Implement a try/finally to ensure that cleanup nodes always run.

## CI/CD pipelines
Continuous Integration, Continuous Delivery (CI/CD) pipelines can take many forms, but
typically all include some basic steps: Build, Test, Deploy. Implementing this at a high
level should be familiar if you have seen the previous steps, so this use cases focuses
on a low-level portion of a CI/CD pipeline - testing a microservice.

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

In case you're unfamiliar with the concept, a Docker _image_ is a template for an
execution environment that defines the base OS and file system contents, which often
include programming languages, packages, and user code. A _container_ is a running
instantiation of an _image_. A _container_ is like a Virtual Machine (VM), but more
lightweight and faster to create/destroy than a VM. You can create your own images,
or use one of the many publicly available images from [Docker Hub](https://hub.docker.com)
or another registry. For more information, check out a few of the many intros and
tutorials to Docker and containers online.

Every Exec node needs to have an `image` defined. If unspecified, the default image is
the standard `python` image with the same version as your local python installation.
To override the default, you can specify a [`co.Image`](https://conducto.com/docs/#do-image)
object, to any node like this: `co.Exec("...", image=co.Image(...))`.

- **Easy**  
    `co.Image("python:3.8", copy_dir=".", reqs_py=["numpy"])`
    Start with the Docker image `python:3.8`. Include all the code at `.`, that is,
    in the same directory as this file. Then `pip install numpy`. This is easiest to
    use if you're unfamiliar with Docker.

- **Easy + git**  
    `co.Image("python:3.8", copy_url="...", copy_branch="...")`
    Same behavior as above, but includes a checkout of the branch `copy_branch`
    from the git repo at `copy_url`. This is very useful for CI/CD, as it lets you
    run code from a specific branch. More to come on this topic in a later demo step.

- **Intermediate**
    `co.Image(dockerfile="../Dockerfile", context="..")`
    Specify a custom Dockerfile, which Conducto will build automatically. This is the
    method we use in this node; see "Show dockerfile" for more details. Note that you
    may still specify `copy_dir`, or `copy_url` + `copy_branch` to add local code to
    the image.

    Use `context` to specify the context for the `docker build` command. If unspecified,
    it will be the directory that contains the Dockerfile.

- **Intermediate + `path_map`**
    `co.Image(dockerfile="../Dockerfile", context="..", path_map={"/local/path":"/container/path"})`
    Same as above, but with `path_map` specified to enable live debugging.

- **Do it yourself**  
    `co.Image("my_custom_image")`  
    If you are already fluent in Docker and have your own image built, specify it here.
    Note that you may specify `copy_dir` or `copy_url` + `copy_branch` to add local code
    to the image. You may also specify `path_map` to enable live debugging.

### A note on debugging

You were introduced to the "Debug" and "Rebuild Image" functionality in the earlier
"Dealing with errors" node. In light of the `image` discussion above, here is a further
discussion of those tools.

- Snaphot debugging will work with every flavor of `image` specification.

- Live debugging mounts the copy_dir from your local machine, so local edits are visible
  to the debug container; this will only work when `copy_dir` or `path_map` is
  specified.

- "Rebuild Image" works whenever Conducto is responsible for building a Docker image,
  which it does if `copy_dir`, `copy_url` + `copy_branch`, `reqs_py`, or
  `dockerfile` are specified.

## Docker in Exec nodes

If you need to run a Docker command in an Exec node, you must specify the `requires_docker`
parameter. Select the child node "Setup" for more information.

## Container

Visit "Test" for more information on how Exec nodes use containers.

## Try/finally

Look at "Stop" to learn how to ensure that cleanup steps always run, regardless of
previous errors.
"""
import conducto as co
import subprocess

try:
    import utils
except ImportError:
    from . import utils


DOCKERFILE_DOC = """
## Using `co.Image(dockerfile='...')`
This example uses a single image with both Docker and python. It also must include the
code from this directory as well as the 'conducto' python package.

There are many ways to achieve this goal, and we break it down into two parts:
1. There is no default image on DockerHub that contains both Docker and python, so we
   made this dockerfile that does nothing except for combining them.
2. Use existing `co.Image` functionality to include local files and install python
   libraries.

The image definition is  
`co.Image(dockerfile="Dockerfile-testing", copy_dir=".", reqs_py=["conducto"])`

Conducto runs `docker build` on `Dockerfile-testing`, whose contents are printed below.
It then runs another Docker command that copies the `copy_dir` and installs conducto.

## Alternative: copy manually and use `path_map`
There is no single correct way to do this. We could instead write the `copy` and
`pip install` commands inside this Dockerfile:

```docker
# Install conducto
RUN pip install conducto

# Copy everything from the build context into /path/to/code
COPY . /path/to/code
```

The image would be correct, but both `do.lazy_py` and live debugging would break because
they would not know how to find the code inside the container.

We can tell Conducto how to find it by specifying `path_map`:  
`co.Image(..., path_map={".":"/path/to/code"})`
"""

SETUP_DOC = """
## Docker in Exec nodes
Docker does not trivially support containers-within-containers (also called
Docker-in-Docker). Enabling Exec nodes to run Docker commands incurs additional
overhead so Conducto leaves this feature disabled by default. To enable it, specify
`requires_docker=True`.

In this node we start a containerized Redis server, which requires enabling Docker,
like this: `co.Exec("...", requires_docker=True)`. Easy.
"""

TEST_DOC = """
## Containers

Each Exec node runs in a container, but multiple Exec nodes may share a single
container. Conducto provides a few modes for controlling this behavior.

### Default: each Exec node usually gets its own container
Normally, Conducto runs each Exec node in its own container. For efficiency reasons it
may reuse a container - if one Exec node finishes and another in the queue is compatible
with the now-available container, Conducto will assign one from the queue to the
container.

If you expect each Exec node to run independently and not destructively modify the
state of its container, this is a great default choice.

### Run Exec nodes in a single container
Cases do exist where you want to build up local state over the course of a few nodes.
This test, for example, starts by installing the python redis package into the container,
then uses the newly installed package to read and write data to a redis-server. These steps
must all run in the same container, or else the read & write steps would not be able to
see the redis package.

To instruct Conducto that these nodes must share a container, create a new "same container"
copy_dir: `same_container=co.SameContainer.NEW`. All child nodes below this that have the
default of `same_container=co.SameContainer.INHERIT` will share this container.

```python
with co.Serial(same_container=co.SameContainer.NEW) as test:
    test["Install"] = co.Exec("pip install redis")
    test["Write"] = co.Exec("...")
    test["Read"] = co.Exec("...")
```

Another use of `SameContainer.NEW` is to start a server in one Exec node, and then run a
test against it in the next Exec node. Alternatively, you could put these commands in a
single Exec node, connected with `&&`. But, separating them into multiple Exec nodes
improves clarity by giving you separate outputs for each command, making debugging easier.

Note: you can also use this feature if you simply want to disable container reuse and ensure
that each Exec node gets its own container. 
"""
## TODO: Add doc for SameContainer.ESCAPE
# Exit the same-container context to give Exec nodes their own containers

STOP_DOC = """
## Try/finally
By default, Serial nodes stop upon any of their child nodes failing. Disabling this
behavior can be helpful for ensuring that a cleanup node will always run.

In this example, Teardown will always run, even if Setup or Test fail, similar to
a try/finally block in Python.
```python
with co.Serial(stop_on_error=False) as output:
    with co.Serial(name="Setup and test"):
        output["Setup"] = co.Exec("...")
        output["Test"] = co.Exec("...")
    output["Teardown"] = co.Exec("...")
```
"""


def run() -> co.Serial:
    output = co.Serial(
        image=co.Image(
            dockerfile="Dockerfile-testing", copy_dir=".", reqs_py=["conducto"]
        ),
        stop_on_error=False,
        doc=__doc__,
    )
    output["Show dockerfile"] = node = co.lazy_py(
        utils.print_source, co.relpath("Dockerfile-testing")
    )
    node.doc = DOCKERFILE_DOC

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
