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
https://medium.com/conducto/execution-environment-3bb663549a0c)
"""

import conducto as co


numpy_script = """
import numpy as np
arr = np.arange(15).reshape(3,5)
print(arr)
"""


def existing_image() -> co.Exec:
    """Specify any existing image from Dockerhub or another image registry."""
    image = co.Image("r-base:3.5.0")
    return co.Exec("Rscript --help", image=image, doc=co.util.magic_doc())


def python_image_with_reqs_py() -> co.Exec:
    """Specify a python image and list requirements with `reqs_py`."""
    image = co.Image("python:3.8-slim", reqs_py=["numpy"])
    return co.Exec(
        f"python -c '{numpy_script}'", image=image, doc=co.util.magic_doc()
    )


def dockerfile() -> co.Exec:
    """Specify a dockerfile for full flexibility in defining your image."""
    image = co.Image(dockerfile="./docker/Dockerfile.simple")
    return co.Exec(
        f"python -c '{numpy_script}'", image=image, doc=co.util.magic_doc()
    )


def copy_local_code() -> co.Exec:
    """Copy local code into your image with `copy_dir`."""
    image = co.Image("r-base:3.5.0", copy_dir="./code")
    return co.Exec("Rscript simple.R", image=image, doc=co.util.magic_doc())


def clone_from_git() -> co.Exec:
    """
    Clone a git branch into your image with `copy_url` and `copy_branch`.
    Your image or dockerfile must have git installed for this to work.
    """
    git_url = "https://github.com/conducto/demo.git"
    dockerfile = "./docker/Dockerfile.git"
    image = co.Image(
        dockerfile=dockerfile, copy_url=git_url, copy_branch="master",
    )
    return co.Exec("Rscript data_science/code/simple.R", image=image, doc=co.util.magic_doc())


def dockerfile_with_copy() -> co.Exec:
    """
    You can COPY or ADD files directly in your dockerfile.
    """
    image = co.Image(dockerfile="./docker/Dockerfile.copy", context=".")
    return co.Exec("Rscript /root/code/simple.R", image=image, doc=co.util.magic_doc())


def clone_from_git_with_path_map() -> co.Exec:
    """
    Enable livedebug by specifying `path_map`, mapping a local directory
    to a directory in your checkout. A relative path in the key is relative
    to the location of this script. A relative path in the value is relative
    to the root directory of the git repo.
    """
    git_url = "https://github.com/conducto/demo.git"
    path_map = {".": "data_science"}
    image = co.Image(
        dockerfile="./docker/Dockerfile.git",
        copy_url=git_url,
        copy_branch="master",
        path_map=path_map,
    )
    return co.Exec("Rscript data_science/code/simple.R", image=image, doc=co.util.magic_doc())


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
    return co.Exec("Rscript /root/code/simple.R", image=image, doc=co.util.magic_doc())


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
    co.main(default=examples)
