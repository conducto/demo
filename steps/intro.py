INTRO_MESSAGE = """
<ConductoMarkdown>
## Welcome to Conducto!

Please select the next node (Node Types) and ![unskip](https://github.com/conducto/demo/raw/master/images/unskip.png) it to continue.
You can also right-click and select "Unskip" from the context menu.
</ConductoMarkdown>
"""


def intro():
    print(INTRO_MESSAGE.strip())
    print("An Exec node's stdout and stderr are reported here.")
    print("Check the source to see how to use markdown for clearer output")
