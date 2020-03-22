"""
Use TempData, PermData, and do.lazy_py to crunch data in parallel
"""
import conducto as do
import collections, json, math, os, random

try:
    import utils
except ImportError:
    from . import utils

MAX_SIZE = 6


def run() -> do.Serial:
    # You can use 'with' statement (context manager) to build the pipeline. This
    # helps make your code indentation mimic the structure of the Nodes.
    with do.Serial(image=utils.IMG) as output:
        output["Show source"] = do.lazy_py(utils.print_source, do.relpath(os.path.abspath(__file__)))

        input_path = "conducto/demo_data"
        temp_dir = "conducto/demo_data"

        # Generate 5M random words.
        output["Generate data"] = do.lazy_py(gen_data, count=5000 * 1000, path=input_path)

        # Parallelize over the input
        output["Parallel word count"] = do.lazy_py(parallelize, input_path, temp_dir, top=15, chunksize=50 * 1000)
        output["Summarize"] = do.lazy_py(summarize, temp_dir, top=15)
    return output


def gen_data(count: int, path: str, force=do.env_bool("FORCE")):
    """
    Generate `count` random English words and save them to `path`. Skip if the data
    already exists, unless `force` is specified. Set the environment variable FORCE
    to force regeneration.
    """
    import urllib.request
    print(f"Generating {count} words and storing them to PermData:{path}.")
    if do.PermData.exists(path):
        if force:
            print("PermData already populated, but 'force' is set. Regenerating.")
        else:
            print("PermData already populated. Skipping.")
            print("To force regeneration, set environment variable FORCE=true.")
            return

    url = "https://github.com/dwyl/english-words/raw/master/words.txt"
    text = urllib.request.urlopen(url).read()
    words_raw = text.splitlines()
    print(f"Downloaded {len(words_raw)} words ({len(text)} bytes) from {url}")

    words_filtered = [w.ljust(MAX_SIZE) for w in words_raw if w.islower() and w.isalpha() and 3 <= len(w) <= MAX_SIZE]
    print(f"Filtered to only lowercase words, 3 to {MAX_SIZE} characters. {len(words_filtered)} remain.")

    words = random.choices(words_filtered, k=count)
    text = b"\n".join(words) + b"\n"
    do.PermData.puts(path, text)
    print(f"Saved {count} words to PermData:{path}")


def parallelize(input_path, temp_dir, top: int, chunksize: int) -> do.Parallel:
    """
    Parallelize over the data at `input_path`, generating a "do_chunk(top)" command for
    each `chunksize` words. Store the temporary output in `temp_dir`.
    """
    output = do.Parallel()
    data_size = do.PermData.size(input_path)
    # Each line is a word padded to MAX_SIZE characters, plus a "\n"
    num_chunks = math.ceil(data_size / (MAX_SIZE + 1) / chunksize)
    for i in range(num_chunks):
        start = i * (MAX_SIZE + 1) * chunksize
        end = (i + 1) * (MAX_SIZE + 1) * chunksize
        output[f"Chunk-{i}"] = do.lazy_py(
            do_chunk, input_path, temp_dir, top=top, start=start, end=end)
    return output


def do_chunk(input_path, temp_dir, top: int, start: int, end: int):
    """
    Count the `top` words from the assigned chunk of `input_path`, saving the data in
    `temp_dir`.
    """
    text = do.PermData.gets(input_path, byte_range=[start, end])
    words = [l.strip() for l in text.splitlines()]
    print(f"Got {len(words)} words")
    most = collections.Counter(words).most_common(top)
    text = json.dumps(most)
    path = f"{temp_dir}/{start}"
    do.TempData.puts(path, text)
    print(f"Wrote to {path}")
    for rank, (word, count) in enumerate(most):
        print(f"#{rank} -- {word} -- {count}")


def summarize(temp_dir, top: int):
    """
    Summarize all the files in `temp_dir` and return the `top` most common words.
    """
    objs = do.TempData.list(temp_dir)
    summary = collections.Counter()
    for i, obj in enumerate(objs):
        print(f"[{i}/{len(objs)}] Reading {obj}", flush=True)
        text = do.TempData.gets(obj)
        for word, count in json.loads(text):
            summary[word] += count

    for rank, (word, count) in enumerate(summary.most_common(top)):
        print(f"#{rank} -- {word} -- {count}")


if __name__ == "__main__":
    do.main(default=run)
