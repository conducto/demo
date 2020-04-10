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
documentation. Check it out for a friendly explanation of each topic. Or,
check out [*Getting Started With Conducto for CI/CD*](
https://medium.com/conducto/getting-started-with-conducto-for-ci-cd-b6afb626f410).

Click *Run* to get started and learn how to supercharge your CI/CD pipelines!
"""

import conducto as co
import first_pipeline
import execution_env
import env_secrets
import data_stores


def full_demo() -> co.Parallel:
    from conducto.shared.log import unindent

    pretty_doc = unindent(__doc__)
    with co.Parallel(doc=pretty_doc) as full:
        full["first_pipeline"] = first_pipeline.build_and_test()
        full["execution_env"] = execution_env.examples()
        full["env_secrets"] = env_secrets.examples()
        full["data_stores"] = data_stores.examples()
    return full


if __name__ == "__main__":
    print(__doc__)
    co.main(default=full_demo)
