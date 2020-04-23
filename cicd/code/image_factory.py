"""
Convenience factory for images. Assumes that the pipeline script calling
this is in a git repo, and that you are running that script from a local
checkout. It has two modes:

1. If you init with no arguments, it configures an image with a copy of
   your local checkout (even changes that are not checked in yet).

2. If you init with a `branch` argument, it configures an image that does
   a `git clone` of that branch from github.

In both cases, livedebug is enabled and configured to mount your local
checkout. When you `get()` an image, you can specify an image (like
"python:3.8-alpine") or a dockerfile.
"""

import os, subprocess, traceback
import conducto as co


_USER = "tester"
_REPO = "conducto/demo"


class ImageFactory(object):
    @classmethod
    def init(cls, branch=None):
        # Set the context to the local root of the git checkout of the function that
        # called this one.
        stack = traceback.extract_stack(limit=2)
        from_file = stack[-2].filename
        from_dir = os.path.dirname(from_file) or "."
        cls.context = cls._shell(f"git -C {from_dir} rev-parse --show-toplevel")
        if branch is None:
            cls._init_local()
        else:
            cls._init_git(branch)

    @classmethod
    def _init_local(cls):
        """
        Init from local git checkout, copy local code into image.
        Just set `copy_dir` to the local root of this git checkout.
        Livedebug is automatically enabled because we use `copy_dir`.
        """
        cls.copy_dir = cls.context
        cls.copy_url = None
        cls.copy_branch = None
        cls.path_map = None
        cls.git_env = {
            "GIT_SHA1": os.environ.get("GIT_SHA1") or \
                cls._shell("git rev-parse HEAD"),
            "GIT_BRANCH": os.environ.get("GIT_BRANCH") or \
                cls._shell("git rev-parse --abbrev-ref HEAD"),
        }

    @classmethod
    def _init_git(cls, branch):
        """
        Init from github with specified branch, clone code into image.
        Set `copy_url` and `copy_branch` for github repo. Livedebug  is
        enabled by setting `path_map` to map the root of this local git
        checkout to ".", the root of the git checkout in the image.
        """
        cls.copy_dir = None
        # Uncomment these lines for a private repo. Populate GITHUB_TOKEN
        # secret, _USER, and _REPO appropriately.
        # cls.github_token = cls._get_github_token()
        # cls.copy_url = f"https://{_USER}:{cls.github_token}@github.com/{_REPO}.git"
        cls.copy_url = f"https://github.com/{_REPO}.git"
        cls.copy_branch = branch
        cls.path_map = {cls.context: "."}
        cmd = cls._shell(f"git ls-remote {cls.copy_url} refs/heads/{cls.copy_branch}")
        cls.git_env = {
            "GIT_SHA1": remote.strip().split('\t')[0],
            "GIT_BRANCH": cls.copy_branch,
        }
        if not cls.git_env["GIT_SHA1"]:
            raise ValueError(
                f"{_REPO} on github.com does not have a branch named {branch}"
            )

    @staticmethod
    def _shell(cmd):
        stdout = subprocess.check_output(cmd, shell=True)
        return stdout.decode("utf-8").strip()

    @staticmethod
    def _get_github_token():
        """GITHUB_TOKEN stored as an org-level secret."""
        auth_token = co.api.Auth().get_token_from_shell()
        return co.api.Secrets().get_org_secrets(auth_token)["GITHUB_TOKEN"]

    @classmethod
    def get(cls, image=None, dockerfile=None, reqs_py=None, name=None):
        assert image is not None or dockerfile is not None
        return co.Image(
            image=image,
            dockerfile=dockerfile,
            context=cls.context,
            reqs_py=reqs_py,
            copy_dir=cls.copy_dir,
            copy_url=cls.copy_url,
            copy_branch=cls.copy_branch,
            path_map=cls.path_map,
            name=name,
        )
