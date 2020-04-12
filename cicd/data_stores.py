"""
### **Data Stores**
How to store artifacts and intermediate results:
* connect to your own data store (for example, redis)
* use conducto-temp-data as a pipeline-local key-value store
* use conducto-perm-data as a global persistent key-value store

[Companion tutorial here.](https://medium.com/conducto/data-stores-cfb82460cb76)
"""


import conducto as co
from utils import magic_doc


def redis_data_store() -> co.Exec:
    """
    There are many standard ways to store persistent data: databases,
    AWS S3, and in-memory caches like redis. An exec node can run any
    shell command, so it is easy to use any of these approaches. Here
    we populate environment variables pointing to our redis service,
    allowing us to write to and read from redis in a python script.
    """

    # export_cmd is just a hack to set REDIS_HOST to our mock instance
    export_cmd = (
        "export REDIS_HOST=$(ip route show default | awk '/default/{print $3}')"
    )
    redis_write_cmd = f"{export_cmd} && python redis_example.py --write"
    redis_read_cmd = f"{export_cmd} && python redis_example.py --read"

    env = {
        "REDIS_HOST": "override_me",
        "REDIS_PORT": "6379",
    }
    image = co.Image("python:3.8-alpine", copy_dir="./code", reqs_py=["redis", "Click"])
    with co.Serial(image=image, env=env, doc=magic_doc()) as redis_store:
        co.Exec(redis_write_cmd, name="redis_write")
        co.Exec(redis_read_cmd, name="redis_read")
    return redis_store


def conducto_temp_data() -> co.Serial:
    """
    `conducto-temp-data` is a pipeline-local key-value store.
    This data is only visible to your pipeline and persists until your
    pipeline is archived. One useful application is storing binaries in a
    build node, and retrieving them in a later test node. We exercise the
    `put` and `get` commands to do this.
    to temporarily store and retrieve a binary.
    """

    build_cmd = """set -ex
go build -o bin/app ./app.go
conducto-temp-data put --name my_app_binary --file bin/app
"""
    test_cmd = """set -ex
conducto-temp-data get --name my_app_binary --file /tmp/app
/tmp/app --test
"""

    # Dockerfile installs golang and conducto.
    dockerfile = "./docker/Dockerfile.temp_data"
    image = co.Image(dockerfile=dockerfile, context=".", copy_dir="./code")
    with co.Serial(image=image, doc=magic_doc()) as build_and_test:
        co.Exec("conducto-temp-data --help", name="usage")
        co.Exec(build_cmd, name="build")
        co.Exec(test_cmd, name="test")
    return build_and_test


def conducto_perm_data() -> co.Exec:
    """
    `conducto-perm-data` is a global persistent key-value store.
    This is just like conducto-temp-data, but data is visible in all
    pipelines and persists beyond the lifetime of your pipeline. You
    are responsible for manually clearing your data. One useful application
    is restoring a python virtual env to avoid repeatedly installing it
    across nodes and pipelines. We exercise the various `cache` commands
    to do this.
    """

    create_and_save_cmd = """set -ex
python -m venv venv
. venv/bin/activate
pip install -r requirements.txt
checksum=$(md5sum requirements.txt | cut -d" " -f1)
conducto-perm-data save-cache \
    --name code_venv --checksum $checksum --save-dir venv
"""

    restore_and_test_cmd = """set -ex
checksum=$(md5sum requirements.txt | cut -d" " -f1)
conducto-perm-data restore-cache \
    --name code_venv --checksum $checksum --restore-dir restored_venv
. restored_venv/venv/bin/activate
pip list
"""

    clear_cmd = """set -ex
checksum=$(md5sum requirements.txt | cut -d" " -f1)
conducto-perm-data clear-cache --name code_venv --checksum $checksum
    """

    image = co.Image("python:3.8-alpine", copy_dir="./code", reqs_py=["conducto"])
    with co.Serial(image=image, doc=magic_doc()) as venv_test:
        co.Exec("conducto-perm-data --help", name="usage")
        co.Exec(create_and_save_cmd, name="create_and_save")
        co.Exec(restore_and_test_cmd, name="restore_and_test")
        co.Exec(clear_cmd, name="clear")
    return venv_test


def examples() -> co.Parallel:
    ex = co.Parallel(doc=__doc__)
    ex["redis_data_store_wrapper"] = _redis_wrapper()
    ex["conducto_temp_data"] = conducto_temp_data()
    ex["conducto_perm_data"] = conducto_perm_data()
    return ex


def _redis_wrapper() -> co.Serial:
    """
    This is a simple wrapper that starts and stops a local redis instance
    around our *redis_data_store* example. This is just to mock a real
    redis service you might have running externally. The details of how
    this works are not critical right now. We use Conducto features
    `stop_on_error` and `requires_docker` that are discussed in a later
    tutorial. **Focus on the *redis_data_store* node for now.**
    """

    name = "conducto_demo_redis"
    mock_redis_start_cmd = f"""set -ex
docker run -p 6379:6379 -d --rm --name {name} redis:5.0-alpine
sleep 1 # wait for redis to start up
docker logs --details {name}
# error if redis container not running
docker inspect {name} --format="{{{{.State.Running}}}}"
"""
    mock_redis_stop_cmd = f"docker stop {name} || true"

    with co.Serial(
        image="docker:19.03",
        stop_on_error=False,
        requires_docker=True,
        doc=magic_doc(doc_only=True),
    ) as wrapper:
        co.Exec(mock_redis_start_cmd, name="mock_redis_start")
        wrapper["redis_data_store"] = redis_data_store()
        co.Exec(mock_redis_stop_cmd, name="mock_redis_stop")
    return wrapper


if __name__ == "__main__":
    print(__doc__)
    co.main(default=examples)
