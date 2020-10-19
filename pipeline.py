# Define your CI/CD pipeline in a Python script.

import conducto as co


# `pr()` creates and returns a CI/CD pipeline for a Pull Request. Run from the command
# line with `python pipeline.py pr --branch=<branch>`.
def pr(branch) -> co.Parallel:
    # Make a Docker image, based on python:alpine, with the whole repo and the contents
    # of the given branch.
    image = co.Image("python:alpine", copy_repo=True, copy_branch=branch)

    # Using that Docker image, run three commands in parallel to interact with the
    # repo's files.
    with co.Parallel(image=image) as root:
        co.Exec(f"echo {branch}", name="print branch")
        co.Exec("pwd", name="print working directory")
        co.Exec("ls -la", name="list files")

    co.git.apply_status_all(root)

    return root


if __name__ == "__main__":
    co.main()
