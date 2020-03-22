"""
Show usage of the different node types, Parallel, Serial, and Exec.
"""
import conducto as do
import os

try:
    import utils
except ImportError:
    from . import utils


def run() -> do.Serial:
    # Use do.Exec() to run a build step
    build_node = do.Exec("echo docker build, make, npm i, etc.")

    # Use do.Parallel() to run tests in parallel.
    test_node = do.Parallel()
    for name in ["app", "backend", "metrics"]:
        test_node[name] = do.Exec(f"echo run test for {name}")

    # Use do.Serial() to build then test.
    pipeline = do.Serial(image=utils.IMG)
    pipeline["Show source"] = do.lazy_py(utils.print_source, do.relpath(os.path.abspath(__file__)))
    pipeline["Build"] = build_node
    pipeline["Test"] = test_node

    return pipeline


if __name__ == "__main__":
    do.main(default=run)
