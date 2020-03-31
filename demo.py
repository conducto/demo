"""
# Welcome to Conducto!

**Topics learned**
- Explore your pipeline and its nodes.
- Run the pipeline.

## Pipeline panel and Node panel
The Pipeline panel on the left interactively shows your pipeline. Expand and collapse
nodes to explore the structure of the pipeline. As the pipeline runs, the state counts
change to show you a high- or low-level view of what is succeeding, failing, or has yet
to run.

The Node panel on the right shows the details of an individual node. Learn more about
the node types in the next step.

## Next: running the pipeline
Look at the first node, "Node types". Read its explanation and see if you can guess
what it will do once you run it.

When you're ready, click ![run](https://github.com/conducto/demo/raw/master/images/run.png)
to run the pipeline. Was your guess correct?

As you go through the rest of the demo, note that the 'Run' button stayed depressed once
you clicked it. The pipeline will keep running nodes as you reset or unskip them. Try it
out, it should feel nice and intuitive.
"""

import conducto as co

try:
    from steps import node_types, errors, utils, data, testing
except ImportError:
    from .steps import node_types, errors, utils, data, testing

RUN_MSG = """
Welcome to the Conducto demo. \033[31;1mIf this is your first time running Conducto, your jobs may
be queued longer than you expect while Docker images download.\033[0m We are working on making
this more transparent. Thanks for your patience!
""".strip()


def run() -> co.Parallel:
    print(RUN_MSG)
    output = co.Parallel(image=utils.IMG, doc=__doc__)
    output["Node types"] = node = node_types.run()
    output["Dealing with errors"] = errors.run()
    output["Use case: parallel data processing"] = node = co.lazy_py(data.run)
    node.doc = data.__doc__
    output["Use case: basic CI+CD pipeline"] = node = co.lazy_py(testing.run)
    node.doc = testing.__doc__

    for name, node in output.children.items():
        if name != "Node types":
            node.skip = True
    return output


if __name__ == "__main__":
    co.main(default=run)
