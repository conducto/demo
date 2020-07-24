"""
### **Data Stores**
You will need to store artifacts and intermediate results. You cannot
simply write these artifacts to the local filesystem, because each
command runs in a container with its own filesystem that disappears
when the container exits. And, in cloud mode, containers run on different
machines, so there is no shared filesystem to mount. So, Conducto supports
a few different approaches that work in a containerized world.

* Connect to your own data store (for example, redis).
* Use `conducto-data-pipeline` as a pipeline-local key-value store.
* Use `conducto-data-user` as a user-wide key-value store.

[Companion tutorial here.](
https://medium.com/conducto/data-stores-cfb82460cb76)

[Code for this pipeline here.](
https://github.com/conducto/demo/blob/master/cicd/data_stores.py)
"""


import conducto as co
import utils


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
    redis_write_cmd = f"{export_cmd} && python code/redis_example.py --write"
    redis_read_cmd = f"{export_cmd} && python code/redis_example.py --read"

    env = {
        "REDIS_HOST": "override_me",
        "REDIS_PORT": "6379",
    }
    with co.Serial(image=utils.IMG, env=env, doc=co.util.magic_doc()) as redis_store:
        co.Exec(redis_write_cmd, name="redis_write")
        co.Exec(redis_read_cmd, name="redis_read")
    return redis_store


def data_pipeline() -> co.Serial:
    """
    `conducto-data-pipeline` is a pipeline-local key-value store.
    This data is only visible to your pipeline and persists until your
    pipeline is archived. One useful application is storing binaries in a
    build node, and retrieving them in a later test node. We exercise the
    `put` and `get` commands to do this.
    """

    build_cmd = """set -ex
go build -o bin/app ./app.go
conducto-data-pipeline put --name my_app_binary --file bin/app
"""
    test_cmd = """set -ex
conducto-data-pipeline get --name my_app_binary --file /tmp/app
/tmp/app --test
"""

    # Dockerfile installs golang and conducto.
    dockerfile = "./docker/Dockerfile.data"
    image = co.Image(dockerfile=dockerfile, context=".", copy_dir="./code")
    with co.Serial(image=image, doc=co.util.magic_doc()) as build_and_test:
        co.Exec("conducto-data-pipeline --help", name="usage")
        co.Exec(build_cmd, name="build")
        co.Exec(test_cmd, name="test")
    return build_and_test


def data_user() -> co.Exec:
    """
    `co.data.user` is a key-value store like `co.data.pipeline` but scoped to
    your user, persisting beyond the lifetime of your pipeline. You are
    responsible for manually clearing this data.

    One useful application is restoring a python virtual env to avoid repeatedly
    installing it across nodes and pipelines. We exercise the various `cache`
    commands to do this.
    """

    create_and_save_cmd = """set -ex
python -m venv venv
. venv/bin/activate
pip install -r code/requirements.txt
checksum=$(md5sum code/requirements.txt | cut -d" " -f1)
conducto-data-user save-cache \
    --name code_venv --checksum $checksum --save-dir venv
"""

    restore_and_test_cmd = """set -ex
checksum=$(md5sum code/requirements.txt | cut -d" " -f1)
conducto-data-user restore-cache \
    --name code_venv --checksum $checksum --restore-dir restored_venv
. restored_venv/venv/bin/activate
pip list
"""

    clear_cmd = """set -ex
checksum=$(md5sum code/requirements.txt | cut -d" " -f1)
conducto-data-user clear-cache --name code_venv --checksum $checksum
    """

    with co.Serial(image=utils.IMG, doc=co.util.magic_doc()) as venv_test:
        co.Exec("conducto-data-user --help", name="usage")
        co.Exec(create_and_save_cmd, name="create_and_save")
        co.Exec(restore_and_test_cmd, name="restore_and_test")
        co.Exec(clear_cmd, name="clear")
    return venv_test


def examples() -> co.Parallel:
    ex = co.Parallel(doc=__doc__)
    ex["redis_data_store_wrapper"] = _redis_wrapper()
    ex["co.data.pipeline"] = data_pipeline()
    ex["co.data.user"] = data_user()
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
        doc=co.util.magic_doc(doc_only=True),
    ) as wrapper:
        co.Exec(mock_redis_start_cmd, name="mock_redis_start")
        wrapper["redis_data_store"] = redis_data_store()
        co.Exec(mock_redis_stop_cmd, name="mock_redis_stop")
    return wrapper


if __name__ == "__main__":
    print(__doc__)
    co.Image.register_directory("CONDUCTO_DEMO", "..")
    co.main(default=examples)
