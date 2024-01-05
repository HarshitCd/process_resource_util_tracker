import concurrent.futures as cf
import time

import psutil
import json


def get_pid(name: str) -> int:
    for proc in psutil.process_iter():
        if name.lower() in proc.name().lower():
            return proc.pid

    return -1


def resource_tracker(pname: str, pid: int, samples: int = 60, interval: int = 0.5) -> dict:
    if pid == -1:
        return {}

    resource_data: dict = dict()
    process = psutil.Process(pid)

    timestamp = list()
    cpu_percent = list()
    rss_usage = list()

    for _ in range(samples):
        timestamp.append(((time.time() * 100) // 1) / 100)
        cpu_percent.append(round(process.cpu_percent(interval=interval), 2))
        rss_usage.append(round(process.memory_percent(memtype="rss"), 2))

    timestamp = [(((val - timestamp[0]) * 100) // 1) / 100
                 for val in timestamp]
    no_of_pids = len(psutil.pids())

    resource_data = {
        "timestamp": timestamp,
        "cpu_percent": {no_of_pids: cpu_percent},
        "rss_usage": {no_of_pids: rss_usage}
    }

    return {pname: resource_data}


def main():
    # process_deets: list[str] = {val.strip(): get_pid(val.strip()) for val in input("Enter the process names: ").split(",")}
    process_names: list[str] = ["python3", "node"]
    process_deets: dict = {val.strip(): get_pid(val.strip())
                           for val in process_names}
    resource_data: dict = dict()

    # print(process_deets)

    with cf.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(resource_tracker, k, v)
                   for k, v in process_deets.items()]

    for future in cf.as_completed(futures):
        resource_data = {**resource_data, **future.result()}

    print(json.dumps(resource_data))


if __name__ == '__main__':
    main()
