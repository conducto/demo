import conducto as do
try:
    from steps import intro, node_types, errors, utils
except ImportError:
    from .steps import intro, node_types, errors, utils


def walkthrough() -> do.Parallel:
    output = do.Parallel(image=utils.IMG)
    output["Intro"] = do.lazy_py(intro.intro)
    output["Node Types"] = node_types.run()
    output["Error Handling"] = errors.run()

    for name, node in output.children.items():
        if name != "Intro":
            node.skip = True
    return output

if __name__ == "__main__":
    do.main(default=walkthrough)
