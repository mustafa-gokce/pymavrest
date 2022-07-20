import time
import multiprocessing
import requests


def hammer():
    print("Spawned a hammer")
    time_max = 0
    while True:
        time_initial = time.monotonic()
        data = requests.get("http://127.0.0.1:2609/get/message/all").json()
        time_final = time.monotonic()
        time_delta = time_final - time_initial
        if time_delta > time_max:
            time_max = time_delta
            print("Max time increased to ", time_max, "seconds")


processes = []
for _ in range(8):
    processes.append(multiprocessing.Process(target=hammer))
for process in processes:
    process.start()
for process in processes:
    process.join()
