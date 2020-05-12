"""
### **Conducto CI/CD Demo**
Welcome to our full CI/CD demo. Each top level node is a separate topic
and can be run as a standalone demo like this:

```
python {name}.py --local
```

Look for the *doc* icon to the right of each node name. If present, you
will find helpful documentation when you click on that node.

And finally, each top level node has a companion tutorial linked in its
documentation. Check it out for a friendly explanation of the topic. Or,
find a full list of tutorials in [Conducto for CI/CD](
https://medium.com/conducto/getting-started-with-conducto-for-ci-cd-b6afb626f410).

Click *Run* to get started and learn how to supercharge your CI/CD pipelines!

[Code for this pipeline here.](
https://github.com/conducto/demo/blob/master/cicd/full_demo.py)
"""

import conducto as co
import first_pipeline, execution_env, env_secrets, data_stores
import node_params, error_resolution, extras


def cicd() -> co.Parallel:
    from conducto.shared.log import unindent

    pretty_doc = unindent(__doc__)
    with co.Serial(doc=pretty_doc, stop_on_error=False, tags=["demo_cicd"]) as full:
        full["first_pipeline"] = first_pipeline.build_and_test()
        full["execution_env"] = execution_env.examples()
        full["env_secrets"] = env_secrets.examples()
        full["data_stores"] = data_stores.examples()
        full["node_params"] = node_params.examples()
        full["error_resolution"] = error_resolution.examples()
        full["extras"] = extras.examples()
    return full


if __name__ == "__main__":
    print(__doc__)
    co.main(default=cicd)
