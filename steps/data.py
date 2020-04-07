"""
**Topics learned**
- [`co.temp_data` and `co.perm_data`](https://conducto.com/docs/#temp-data-and-perm_data)
  are key/value data stores. `temp_data` is scoped to the current pipeline, and
  `perm_data` persists outside of it.
- Lazily generate parts of the pipeline using [`co.lazy_py`](https://conducto.com/docs/#lazy-pipeline-creation)
  to parallelize over newly-generated data.

## Pipeline
This is a sample pipeline to do a distributed word count in a map/reduce style. While
other purpose-built tools can solve this common example more succinctly, it illustrates
how elegant Conducto's general approach can be. It encourages you to break the problem
down into simple components that are easily coded, understood, visualized, and debugged.

1. **Generate data**: This step ensures that a wordlist is contained in perm_data. If
  perm_data already has the wordlist, exit quickly. Otherwise download a dictionary,
  sample 5M random words, and save it to perm_data.
2. **Parallelize (aka "map")**: Analyze the contents of perm_data and divide it into
  chunks, generating an Exec node to handle each chunk. This subtree cannot be created
  until the data has been generated, so it uses **do.lazy_py** to lazily create these
  nodes. More detail on this below.
3. **Process chunks in parallel**: The word count problem is easily parallelizable, so
  each Exec node reads in a specified chunk of data from the perm_data, aggregates it,
  and stores the results to temp_data.
4. **Summarize (aka "reduce")**: Look in temp_data for all the chunk-by-chunk summaries.
Load and combine all of them to find aggregate statistics on the whole dataset.

## temp_data and perm_data
There are many, many ways to store data: databases, file systems, in-memory caches, or
key/value stores, just to name a few. If you already have data in one of these systems,
in Conducto you are free to import your own libraries and write your own connective
code.

If you don't have a storage system yet, Conducto provides a simple key/value store. In
local mode it is backed by your local disk, and in cloud mode it uses Amazon S3 for
unlimited scalability.

Objects in `co.perm_data` persist across pipelines, while those in `co.temp_data` are only
visible to the current pipeline, and are deleted when the logs are.

There are several uses of temp_data and perm_data in this example:
- **Generate data** calls `co.perm_data.exists` to avoid regenerating the wordlist, and
 `co.perm_data.puts` to save the wordlist if it generated one.
- **Parallelize** calls `co.perm_data.size` to calculate how partition the wordlist.
- **Process chunks** calls `co.perm_data.gets` to read a chunk of the wordlist, and
  passes a byte range to only read the selected portion. It then calls
  `co.temp_data.puts` to store its aggregated statistics.
- **Summarize** calls `co.temp_data.list` to find all the intermediate results, and
  `co.temp_data.gets` to read them. Note, by using `list` to only analyze the objects
  that exist, Summarize is not dependent on every Process Chunk step completing
  successfully. If any chunks have errors, we can skip them and Summarize will work
  correctly.

See the [Conducto docs](https://conducto.com/docs/#temp-data-and-perm_data) for full
details on all available methods.

## co.lazy_py
The [`lazy_py`](https://conducto.com/docs/#lazy-pipeline-creation) function takes any
function call and packages it as a node.
- For most functions that means an Exec node that runs it. For example, see "Generate
  Data" in this node.
- For functions whose return value is type-hinted to be a Serial or Parallel node,
  it returns a pair of nodes. The first node, 'Generate', runs the function and serializes the
  returned node. That node is deserialized into the second node, 'Execute', which then runs
  it. For example, see "Parallel word count" in this node, or see how the example node
  below is lazily generated.


```python
def gen_data(count: int, path: str):
    ...

def parallelize(input_path, temp_dir, top: int, chunksize: int) -> co.Parallel:
    ...

def summarize(temp_dir, top: int):
    ...

with co.Serial(image=utils.IMG, doc=__doc__) as output:
    input_path = "conducto/demo_data"
    temp_dir = "conducto/demo_data"

    # Generate 5M random words. Returns an Exec node.
    output["Generate data"] = co.lazy_py(
        gen_data, count=5000000, path=input_path
    )

    # Parallelize over the input. Returns a Generate/Execute pair.
    output["Parallel word count"] = co.lazy_py(
        parallelize, input_path, temp_dir, top=15, chunksize=50 * 1000
    )

    # Aggregate the intermediate results. Returns an Exec node.
    output["Summarize"] = co.lazy_py(summarize, temp_dir, top=15)
```

Look at how arguments are passed to each step. Methods take simple parameters, like
`str`s or `int`s, which are serialized/deserialized according to their type hints. Note
that instead of passing large amounts of data through Conducto, the data is saved to
temp_data/perm_data and paths to it are passed around.

"""
import conducto as co
import collections, json, math, os, random

try:
    import utils
except ImportError:
    from . import utils

MAX_SIZE = 6


def run() -> co.Serial:
    # You can use 'with' statement (context manager) to build the pipeline. This
    # helps make your code indentation mimic the structure of the Nodes.
    with co.Serial(image=utils.IMG, doc=__doc__) as output:
        input_path = "conducto/demo_data"
        temp_dir = "conducto/demo_data"

        # Generate 5M random words.
        output["Generate data"] = co.lazy_py(
            gen_data, count=5000 * 1000, path=input_path
        )

        # Parallelize over the input
        output["Parallel word count"] = co.lazy_py(
            parallelize, input_path, temp_dir, top=15, chunksize=50 * 1000
        )
        output["Summarize"] = co.lazy_py(summarize, temp_dir, top=15)
    return output


def gen_data(count: int, path: str, force=co.env_bool("FORCE")):
    """
    Generate `count` random English words and save them to `path`. Skip if the data
    already exists, unless `force` is specified. Set the environment variable FORCE
    to force regeneration.
    """
    import urllib.request

    print(f"Generating {count} words and storing them to perm_data:{path}.")
    if co.perm_data.exists(path):
        if force:
            print("perm_data already populated, but 'force' is set. Regenerating.")
        else:
            print("perm_data already populated. Skipping.")
            print("To force regeneration, set environment variable FORCE=true.")
            return

    url = "https://github.com/dwyl/english-words/raw/master/words.txt"
    text = urllib.request.urlopen(url).read()
    words_raw = text.splitlines()
    print(f"Downloaded {len(words_raw)} words ({len(text)} bytes) from {url}")

    words_filtered = [
        w.ljust(MAX_SIZE)
        for w in words_raw
        if w.islower() and w.isalpha() and 3 <= len(w) <= MAX_SIZE
    ]
    print(
        f"Filtered to only lowercase words, 3 to {MAX_SIZE} characters. {len(words_filtered)} remain."
    )

    words = random.choices(words_filtered, k=count)
    text = b"\n".join(words) + b"\n"
    co.perm_data.puts(path, text)
    print(f"Saved {count} words to perm_data:{path}")


def parallelize(input_path, temp_dir, top: int, chunksize: int) -> co.Parallel:
    """
    Parallelize over the data at `input_path`, generating a "process_chunk(top)" command for
    each `chunksize` words. Store the temporary output in `temp_dir`.
    """
    output = co.Parallel()
    data_size = co.perm_data.size(input_path)
    # Each line is a word padded to MAX_SIZE characters, plus a "\n"
    num_chunks = math.ceil(data_size / (MAX_SIZE + 1) / chunksize)
    for i in range(num_chunks):
        start = i * (MAX_SIZE + 1) * chunksize
        end = (i + 1) * (MAX_SIZE + 1) * chunksize
        output[f"Chunk-{i}"] = co.lazy_py(
            process_chunk, input_path, temp_dir, top=top, start=start, end=end
        )
    return output


def process_chunk(input_path, temp_dir, top: int, start: int, end: int):
    """
    Count the `top` words from the assigned chunk of `input_path`, saving the data in
    `temp_dir`.
    """
    text = co.perm_data.gets(input_path, byte_range=[start, end]).decode()
    words = [l.strip() for l in text.splitlines()]
    print(f"Got {len(words)} words")
    most = collections.Counter(words).most_common(top)
    text = json.dumps(most).encode()
    path = f"{temp_dir}/{start}"
    co.temp_data.puts(path, text)
    print(f"Wrote to {path}")
    for rank, (word, count) in enumerate(most):
        print(f"#{rank} -- {word} -- {count}")


def summarize(temp_dir, top: int):
    """
    Summarize all the files in `temp_dir` and return the `top` most common words.
    """
    objs = co.temp_data.list(temp_dir)
    summary = collections.Counter()
    for i, obj in enumerate(objs):
        print(f"[{i}/{len(objs)}] Reading {obj}", flush=True)
        text = co.temp_data.gets(obj).decode()
        for word, count in json.loads(text):
            summary[word] += count

    print()
    print("<ConductoMarkdown>")
    print("rank | word | count")
    print("-----|------|------")
    for rank, (word, count) in enumerate(summary.most_common(top), 1):
        print(f"#{rank} | {word} | {count}")
    print("</ConductoMarkdown>")


if __name__ == "__main__":
    co.main(default=run)
