"""
### **Easy Python Pipelines**
You can build pipelines out of commands in any language with Conducto, but
we have some extra support for python that allows you to easily glue python
functions together into rich and dynamic pipelines.

* Pass a python function to `co.Exec`.
* Lazily define your pipeline at runtime with `co.Lazy`.
* Use Markdown to display rich output in an Exec node.

#### Example: Parallel Word Count
This example does a parallel word count over a randomly generated list of words.
The algorithm is simple but illustrates a common pattern in data science:

1. Get the data.
2. Do parallelized analysis over the data.
3. Aggregate the results.

[Companion tutorial here.](
https://medium.com/conducto/easy-and-powerful-python-pipelines-2de5825375f2)

[Code for this pipeline here.](
https://github.com/conducto/demo/blob/main/data_science/easy_python.py)
"""


import collections, conducto as co, json, math, random
import utils

MAX_SIZE = 6
RESULT_DIR = "conducto/demo_data/results"
WORDLIST_PATH = "conducto/demo_data/wordlist"


def run() -> co.Serial:
    run.__doc__ = __doc__
    with co.Serial(image=utils.IMG, doc=co.util.magic_doc()) as output:
        output["gen_data"] = n = co.Exec(gen_data, WORDLIST_PATH, count=50000)
        n.doc = co.util.magic_doc(func=gen_data)

        output["parallel_word_count"] = n = co.Lazy(
            parallelize, WORDLIST_PATH, RESULT_DIR, top=15, chunksize=1000
        )
        n.doc = co.util.magic_doc(func=parallelize)
        n["Generate"].doc = None

        output["summarize"] = n = co.Exec(summarize, RESULT_DIR, top=15)
        n.doc = co.util.magic_doc(func=summarize)

    return output


def gen_data(path: str, count: int):
    """
    ### **Pass a Python Function to `co.Exec`**
    Conducto can automatically call python functions from the shell so you do
    not have to build your own command-line interface. Instead of calling
    `co.Exec` with a shell command, pass it a function and its arguments.

    In this example, we want to execute this function, `gen_data`, in an Exec
    node. So, we pass the function and its arguments to `co.Exec`.

    ```python
    co.Exec(gen_data, WORDLIST_PATH, count=50000)
    ```

    This auto-generates the shell command below for the Exec node. Note that
    the `conducto` executable is largely just a wrapper for `python`.

    ```
    conducto easy.py gen_data \\
        --path=conducto/demo_data/wordlist --count=50000
    ```

    Easy, right?

    #### Requirements
    Conducto needs to be able to find this function in the image that
    the Exec node runs. Therefore, the Exec node must run with a `co.Image`
    that has `copy_dir`, `copy_url`, or `path_map` set. Also:

    * The image must include the file with the function.
    * The function name cannot start with an underscore (_).
    * The image must install conducto.
    * You must set typical node parameters like `image`, `env`, `doc`, etc.
      outside of the constructor, either in a parent node or by setting the
      fields directly.

    #### Function arguments
    All arguments are serialized to the command line, so only pass parameters
    and paths. Large amounts of data should be passed via a data store like
    `co.data.pipeline` instead.

    Arguments can be basic python types (`int`, `float`, etc.),
    `date`/`time`/`datetime`, or lists thereof. Conducto infers types from the
    default arguments or from type hints, and deserializes accordingly.
    """
    words = _get_words(count)
    text = b"\n".join(words) + b"\n"
    co.data.pipeline.puts(path, text)


def _get_words(count):
    import urllib.request

    url = "https://github.com/dwyl/english-words/raw/master/words.txt"
    text = urllib.request.urlopen(url).read()
    words_raw = text.splitlines()

    words_filtered = [
        w.ljust(MAX_SIZE)
        for w in words_raw
        if w.islower() and w.isalpha() and 3 <= len(w) <= MAX_SIZE
    ]
    subset = random.choices(words_filtered, k=count // 10)
    return random.choices(subset, k=count)


def parallelize(wordlist_path, result_dir, top: int, chunksize: int) -> co.Parallel:
    """
    ### **Lazy Pipeline Definition**
    Data science pipelines often benefit from being able to dynamically
    define the pipeline structure based on the properties of data that only
    become evident as you being analyzing it. For example, you may not know
    the size of your data until you download it, which determines how you
    want to chunk your parallel analysis for maximum efficiency.

    Conducto empowers you to lazily define your pipeline such that new nodes
    can be defined as the pipeline runs. Simply write a function that returns
    a Parallel or Serial node that represents a new subtree to add to the
    pipeline, and call it with `co.Lazy`.

    The node we are currently in defines a pipeline to chunk and analyze the
    input data in parallel. This lazy node is generated by assigning the node
    to the result of `lazy_py`:

    ```python
    output["parallel_word_count"] = co.Lazy(
        parallelize, WORDLIST_PATH, RESULT_DIR, top=15, chunksize=1000
    )
    ```

    `lazy_py` produces two nodes inside the `parallel_word_count` Serial node.
    The first `Generate` node is an Exec node that calls the `parallelize`
    function and prints out the pipeline that it returns. This is the command
    it runs:

    ```
    conducto easy.py parallelize \\
        --wordlist_path=conducto/demo_data/wordlist \\
        --result_dir=conducto/demo_data/results \\
        --top=15 --chunksize=1000
    ```
    
    Once the `Generate` node finishes and returns its new pipeline subtree,
    the subtree is deserialized into an `Execute` node, which then runs.


    #### Requirements
    `co.Lazy` has all the same limitations as `co.Exec(func)` as you saw in
    the `gen_data` node documentation. Additionally, the function must be type
    hinted to return a Parallel or Serial node, as in `def func() -> co.Parallel`.

    #### When to use it
    This pipeline uses `co.Lazy` to dynamically parallelize over some input
    data, but there are many other common uses:

    * **Processing streaming data in batches**: When processing a new batch,
      use `lazy_py` to filter out data that has already been processed, and
      only generate nodes for new data. Use the same logic to backfill data.
    * **Relational mapping**: To join relational data, simply use a for loop.
      When joining datasets `A` and `B`, iterate over `A` at runtime and create
      Exec nodes that run in parallel. Each node looks up the rows in `B` that
      correspond to its `A` value. You have full control over the parallelism
      and can debug any failed or incorrect mappings.
    * **Time-consuming pipeline generation logic**: Sometimes, even figuring
      out the work to do can take a while. Use `lazy_py` to parallelize pipeline
      creation and get it out of the critical path.

    These uses can arise multiple times in the same pipeline. `lazy_py` is
    fully nestable, so you can handle them all and lazily generate as
    sophisticated a pipeline as you need.
    """
    output = co.Parallel()
    data_size = co.data.pipeline.size(wordlist_path)

    num_chunks = math.ceil(data_size / (MAX_SIZE + 1) / chunksize)
    for i in range(num_chunks):
        start = i * (MAX_SIZE + 1) * chunksize
        end = (i + 1) * (MAX_SIZE + 1) * chunksize
        output[f"chunk-{i}"] = co.Exec(
            do_chunk, wordlist_path, result_dir, top=top, start=start, end=end
        )
    return output


def do_chunk(wordlist_path: str, result_dir: str, top: int, start: int, end: int):
    # Read the specified chunk from the wordlist, from `start` to `end`
    text = co.data.pipeline.gets(wordlist_path, byte_range=[start, end]).decode()
    words = [l.strip() for l in text.splitlines()]
    print(f"Got {len(words)} words")

    # Compute `top` most common words
    most = collections.Counter(words).most_common(top)

    # Store result to pipeline-local storage
    result_text = json.dumps(most).encode()
    result_path = f"{result_dir}/{start}"
    co.data.pipeline.puts(result_path, result_text)
    print(f"Wrote to {result_path}")

    # Print out intermediate results for visual inspection
    for rank, (word, count) in enumerate(most):
        print(f"#{rank} -- {word} -- {count}")


def summarize(result_dir, top: int):
    """
    ### Use Markdown for Rich Output
    The goal of data science pipelines is often to produce human-understandable
    results. While you are always free to send data to external visualization
    tools, Conducto supports using Markdown to display tables, links, and
    graphs in your node's output.

    Simply print `<ConductoMarkdown>...</ConductoMarkdown>` in your stdout/stderr,
    and Conducto will render the Markdown between the tags.

    This node summarizes the results of the `parallel_word_count` step using
    a graph and a table.
    """
    result_paths = co.data.pipeline.list(result_dir)
    summary = _get_summary(result_paths)

    filename = "/tmp/plot.png"
    _plot_summary(summary.most_common(top), filename)
    co.data.pipeline.put(name="demo_plot", file=filename)
    url = co.data.pipeline.url(name="demo_plot")

    print("<ConductoMarkdown>")
    print(f"![img]({url})")
    print()
    print("rank | word | count")
    print("-----|------|------")
    for rank, (word, count) in enumerate(summary.most_common(top), 1):
        print(f"#{rank} | {word} | {count}")
    print("</ConductoMarkdown>")


def _get_summary(result_paths):
    output = collections.Counter()
    for i, result_path in enumerate(result_paths):
        # print(f"[{i}/{len(result_paths)}] Reading {result_path}", flush=True)
        result_text = co.data.pipeline.gets(result_path).decode()
        for word, count in json.loads(result_text):
            output[word] += count
    return output


def _plot_summary(summary, filename):
    labels = [label for label, val in summary]
    values = [val for label, val in summary]
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_axes([0.07, 0.17, .9, .8])
    ax.bar(labels, values)
    plt.xticks(rotation=90)
    fig.savefig(filename)


if __name__ == "__main__":
    print(__doc__)
    co.Image.register_directory("CONDUCTO_DEMO", "..")
    co.main(default=run)
