"""
# Node types

**Topics learned**
- Exec, Parallel, and Serial nodes
- Node panel
- Attribute inheritance
- Unskip nodes

## `co.Exec`
Exec nodes run a shell command inside a container. This pipeline runs an example build
step. Exec nodes are leaf nodes and have no children.
```python
build_node = co.Exec("<your command here>")
```

### Node panel
The Node panel on the right displays important information about Exec nodes.

The **Timeline** shows the different runs of an Exec node. Click on the different runs
to see their commands, parameters, and outputs.

The **Execution Parameters** display the settings that define this node's
[execution environment](https://conducto.com/docs/#node-methods-and-attributes).

**Stdout** and **stderr* show the output of the command, updating in real-time as it
runs.

## `co.Parallel`
Parallel nodes have children that they run in parallel. This pipeline uses `co.Parallel`
to run example tests in parallel.
```python
test_node = co.Parallel()
for name in ["app", "backend", "metrics"]:
    test_node[name] = co.Exec(f"echo run test for {name}")
```

## `co.Serial`
Serial nodes have children that they run one after another, stopping if any child
errors.
```python
pipeline = co.Serial(image=utils.IMG, doc=__doc__)
pipeline["Build"] = build_node
pipeline["Test"] = test_node
```

### Attribute inheritance
Note that this example's `image` is defined on the Serial node and is inherited by all
descendants of that node. This makes it easy to operate on a whole subtree, whether it
has one node or one million.

# Run it
Click ![run](https://github.com/conducto/demo/raw/master/images/run.png) to run the
pipeline.

# Next step
Select the next node (Dealing with errors) and ![unskip](https://github.com/conducto/demo/raw/master/images/unskip.png) it to continue.
You can also right-click and select "Unskip" from the context menu.
"""
import conducto as co
import os

try:
    import utils
except ImportError:
    from . import utils

BUILD_CMD = """
echo docker build
echo make
echo npm i

echo 'Any stdout produced by your command goes here.'
echo 'Any stderr it produces goes here' >&2
""".strip()


def run() -> co.Serial:
    # Use co.Exec() to run a build step
    build_node = co.Exec(BUILD_CMD)

    # Use co.Parallel() to run tests in parallel.
    test_node = co.Parallel()
    for name in ["app", "backend", "metrics"]:
        test_node[name] = co.Exec(f"echo run test for {name}")

    # Use co.Serial() to build then test. Note that 'image' is inherited by all child
    # nodes.
    pipeline = co.Serial(image=utils.IMG, doc=__doc__)
    pipeline["Build"] = build_node
    pipeline["Test"] = test_node

    return pipeline


if __name__ == "__main__":
    co.main(default=run)
