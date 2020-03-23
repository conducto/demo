"""
Testing is a part of CI/CD that may often involve complex setup and teardown
functionality. Conducto has several features that help with this:

- do.Image(dockerfile=...): Use a custom dockerfile for this image that contains both
  Docker and Python
- do.Serial(same_container=do.SameContainer.NEW): force all descendant Exec nodes to run
  in one container, allowing us to deploy a service, test it, then tear it down.
- do.Serial(stop_on_error=False) means we will get to the teardown step no matter what,
  like a try/finally block.
- do.Serial(requires_docker=True) is needed to enable running 'docker' commands in the
  Exec node. By default the docker daemon is unavailable.

"""
import conducto as do
import os

try:
    import utils
except ImportError:
    from . import utils


def run() -> do.Serial:
    output = do.Serial(
        image=do.Image(dockerfile="Dockerfile-testing"),
        same_container=do.SameContainer.NEW,
        stop_on_error=False,
        requires_docker=True,
    )
    output["Show source"] = do.lazy_py(
        utils.print_source, do.relpath(os.path.abspath(__file__))
    )
    output["Show dockerfile"] = do.lazy_py(
        utils.print_source, do.relpath("Dockerfile-testing")
    )

    output["Setup"] = do.Exec(
        "docker run -p 6379:6379 -d --rm --name conducto_demo_redis redis:alpine"
    )
    output["Test"] = do.Serial()
    output["Test/Write"] = do.lazy_py(write, key="hello", value="world")
    output["Test/Read"] = do.lazy_py(read, key="hello", expected="world")
    output["Stop"] = do.Exec("docker kill conducto_demo_redis || true")
    return output


def write(key, value):
    import redis

    r = redis.Redis(host="localhost", port=6379, db=0)
    print(f"Setting {repr(key)}=>{repr(value)}")
    r.set(key, value)
    print(f"Getting {repr(key)}")
    v = r.get(key)
    assert v == value, "Mismatch when setting value"
    print("Passed")


def read(key, expected):
    import redis

    r = redis.Redis(host="localhost", port=6379, db=0)
    print(f"Getting {repr(key)}")
    value = r.get(key)
    print(f"Got {repr(value)}, expected {repr(expected)}")
    assert value == expected, f"Value ({repr(value)} != expected ({repr(expected)})"


if __name__ == "__main__":
    do.main(default=run)
