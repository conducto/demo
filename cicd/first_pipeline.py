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
from utils import magic_doc


def build_and_test() -> co.Serial:
    image = co.Image(image="golang:1.14", copy_dir="./code")
    with co.Serial(image=image, doc=magic_doc()) as pipeline:
        with co.Parallel(name="build"):
            co.Exec("go build -x auth.go", name="auth")
            co.Exec("go build -x app.go", name="app")
        with co.Serial(name="test"):
            co.Exec("go run auth.go --test", name="auth")
            co.Exec("go run app.go --test", name="app")
    return pipeline


if __name__ == "__main__":
    print(__doc__)
    co.main(default=build_and_test)
