import time


def test():
    print("I like to test things...")
    for i in range(5):
        time.sleep(0.5)
        print(f"Test {i}: OK")


if __name__ == "__main__":
    test()
