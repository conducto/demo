"""
### **First CI/CD Pipeline**
This is a simple pipeline that uses the following minimal API:

* `co.Exec`, `co.Serial`, and `co.Parallel` node classes
* `co.Image` to specify execution environment
* `co.main()` to make the pipeline executable

It builds two go binaries and tests them.

[Companion tutorial here.](https://medium.com/conducto/your-first-pipeline-32a303b2cc5d)

"""


import conducto as co


def build_and_test() -> co.Serial:
    build_and_test.__doc__ = __doc__
    image = co.Image(image="golang:1.14", copy_dir="./code")
    with co.Serial(image=image, doc=_magic_doc()) as pipeline:
        with co.Parallel(name="build"):
            co.Exec("go build -x auth.go", name="auth")
            co.Exec("go build -x app.go", name="app")
        with co.Serial(name="test"):
            co.Exec("go run auth.go --test", name="auth")
            co.Exec("go run app.go --test", name="app")
    return pipeline


def _magic_doc():
    import inspect, traceback
    from conducto.shared.log import unindent

    st = traceback.extract_stack()
    func = globals()[st[-2].name]
    docstring = func.__doc__
    try:
        code = inspect.getsource(func).split(docstring)[1]
    except:
        code = inspect.getsource(func).split("__doc__ = __doc__")[1]
    pretty_doc = unindent(docstring)
    pretty_code = code
    if pretty_code.startswith('"""'):
        pretty_code = pretty_code.lstrip('"')
    pretty_code = unindent(pretty_code)
    pretty_code = f"\n```python\n{pretty_code}\n```"
    doc = pretty_doc + "\n" + pretty_code
    return doc


if __name__ == "__main__":
    print(__doc__)
    co.main(default=build_and_test)
