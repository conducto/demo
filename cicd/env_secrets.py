"""
### **Data Stores**
Examples of how to specify:
* environment variables
* user secrets

[Companion tutorial here.](
https://medium.com/conducto/environment-variables-and-secrets-12256150e94d)
"""


import conducto as co
import utils

def env_variables() -> co.Exec:
    """
    Specify environment variables, supply the env argument to any node.
    Assign a dictionary of key value pairs where both keys and values
    must be strings.
    """
    env = {
        "NUM_THREADS": "4",
        "TEST_URL": "http://localhost:8080",
    }
    command = "env | grep -e NUM_THREADS -e TEST_URL"
    return co.Exec(command, env=env, image=utils.IMG, doc=co.util.magic_doc())


def user_secrets() -> co.Exec:
    """
    Supply sensitive environment via secrets. You can specify user-level or
    org-level secrets (if you are an admin), which will be injected into
    each running exec node. You should never have secrets hardcoded into any
    scripts, as they are here. You can also specify secrets in our web UI.
    """
    user_secrets = {
        "DEMO_PASSWORD": "ReallyGoodPassword",
        "DEMO_SSN": "Never in code",
    }

    token = co.api.Auth().get_token_from_shell()
    secrets = co.api.Secrets()
    secrets.put_user_secrets(token, user_secrets, replace=False)

    command = "env | grep -e DEMO_PASSWORD -e DEMO_SSN"
    return co.Exec(command, image=utils.IMG, doc=co.util.magic_doc())


def examples() -> co.Parallel:
    ex = co.Parallel(doc=__doc__)
    ex["env_variables"] = env_variables()
    ex["user_secrets"] = user_secrets()
    return ex


if __name__ == "__main__":
    print(__doc__)
    co.main(default=examples)
