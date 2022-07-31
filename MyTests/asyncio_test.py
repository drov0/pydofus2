import time
import asyncio


async def test():
    print("Started!")
    time.sleep(2)
    print("Ok!")


async def main():
    start_time = time.time()

    await asyncio.to_thread(test)

    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == "__main__":
    task = asyncio.run(test())
    print("ok")
    time.sleep(5)