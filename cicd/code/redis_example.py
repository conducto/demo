import redis
import click
import os


def print_key_value_pairs(r):
    for key in r.scan_iter():
        value = r.get(key).decode("utf-8")
        print(f"{key} => {value}")


@click.command()
@click.option("--write", is_flag=True, help="write test data to redis")
@click.option("--read", is_flag=True, help="read test data from redis")
def main(write, read):
    r = redis.Redis(
        host=os.environ.get("REDIS_HOST"), port=os.environ.get("REDIS_PORT"), db=0
    )
    if write:
        r.set("first_pipeline", "easy")
        r.set("execution_env", "medium")
        r.set("env_secrets", "easy")
        r.set("data_stores", "medium")
        print("Wrote these key-value pairs:")
        print_key_value_pairs(r)
    elif read:
        print("Read these key-value pairs:")
        print_key_value_pairs(r)


if __name__ == "__main__":
    main()
