"""
### **Execution Environment**
Working examples of all flavors of image specification.

An image can be:
* an existing image from Dockerhub or another image registry
* a python image with python requirements
* a dockerfile for full flexibility

Code can be added to an image:
* copy local code
* clone from git
* use COPY or ADD in a dockerfile

Live debug can be enabled with path_map:
* clone from git with a path_map
* use dockerfile with a path_map

[Companion tutorial here.](
https://medium.com/conducto/execution-environment-5a66ff0a10bc)

[Code for this pipeline here.](
https://github.com/conducto/demo/blob/main/cicd/execution_env.py)
"""

import conducto as co


pretty_table_script = """
from prettytable import PrettyTable
table = PrettyTable(field_names=["test", "result"])
table.add_row(["auth", "OK"])
table.add_row(["app", "FAILED"])
print(table)
"""


def existing_image() -> co.Exec:
    """Specify any existing image from Dockerhub or another image registry."""
    image = co.Image("node:lts-alpine")
    return co.Exec("npm help", image=image, doc=co.util.magic_doc())


def python_image_with_reqs_py() -> co.Exec:
    """Specify a python image and list requirements with `reqs_py`."""
    image = co.Image("python:3.8-alpine", reqs_py=["PTable"])
    return co.Exec(
        f"python -c '{pretty_table_script}'", image=image, doc=co.util.magic_doc()
    )


def dockerfile() -> co.Exec:
    """Specify a dockerfile for full flexibility in defining your image."""
    image = co.Image(dockerfile="./docker/Dockerfile.simple")
    return co.Exec(
        f"python -c '{pretty_table_script}'", image=image, doc=co.util.magic_doc()
    )


def copy_local_code() -> co.Exec:
    """Copy local code into your image with `copy_dir`."""
    image = co.Image("python:3.8-alpine", copy_dir="./code")
    return co.Exec("python test.py", image=image, doc=co.util.magic_doc())


def clone_from_git() -> co.Exec:
    """
    Clone a git branch into your image with `copy_url` and `copy_branch`.
    Your image or dockerfile must have git installed for this to work.
    """
    git_url = "https://github.com/conducto/demo.git"
    image = co.Image(
        dockerfile="./docker/Dockerfile.git", copy_url=git_url, copy_branch="main",
    )
    return co.Exec("python cicd/code/test.py", image=image, doc=co.util.magic_doc())


def dockerfile_with_copy() -> co.Exec:
    """
    You can COPY or ADD files directly in your dockerfile.
    """
    image = co.Image(dockerfile="./docker/Dockerfile.copy", context=".")
    return co.Exec("python /root/code/test.py", image=image, doc=co.util.magic_doc())


def clone_from_git_with_path_map() -> co.Exec:
    """
    Enable livedebug by specifying `path_map`, mapping a local directory
    to a directory in your checkout. A relative path in the key is relative
    to the location of this script. A relative path in the value is relative
    to the root directory of the git repo.
    """
    git_url = "https://github.com/conducto/demo.git"
    path_map = {".": "cicd"}
    image = co.Image(
        dockerfile="./docker/Dockerfile.git",
        copy_url=git_url,
        copy_branch="main",
        path_map=path_map,
    )
    return co.Exec("python cicd/code/test.py", image=image, doc=co.util.magic_doc())


def dockerfile_with_path_map() -> co.Exec:
    """
    Enable livedebug by specifying `path_map`, mapping a local directory
    to a directory in the container. A relative path in the key is relative
    to the location of this script. The value must be an absolute path.
    """
    path_map = {"./code": "/root/code"}
    image = co.Image(
        dockerfile="./docker/Dockerfile.copy", context=".", path_map=path_map
    )
    return co.Exec("python /root/code/test.py", image=image, doc=co.util.magic_doc())


def examples() -> co.Parallel:
    ex = co.Parallel(doc=__doc__)
    ex["existing_image"] = existing_image()
    ex["python_image_with_reqs_py"] = python_image_with_reqs_py()
    ex["dockerfile"] = dockerfile()
    ex["copy_local_code"] = copy_local_code()
    ex["clone_from_git"] = clone_from_git()
    ex["dockerfile_with_copy"] = dockerfile_with_copy()
    ex["clone_from_git_with_path_map"] = clone_from_git_with_path_map()
    ex["dockerfile_with_path_map"] = dockerfile_with_path_map()
    return ex


if __name__ == "__main__":
    print(__doc__)
    co.Image.register_directory("CONDUCTO_DEMO", "..")
    co.main(default=examples)
