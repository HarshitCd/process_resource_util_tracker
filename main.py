import concurrent.futures as cf
from subprocess import check_output, CalledProcessError
import time

import psutil
import json

def get_pid(name: str) ->int:
    try:
        return int(check_output(["pidof",name]).decode("utf-8").split(" ")[-1].strip())
    except CalledProcessError as e:
        return -1

def resource_tracker(pname:str, pid: int, samples: int = 30, interval: int = 0.5) -> dict:
    if pid == -1:
        return {}
    
    resource_data: dict = dict()
    process = psutil.Process(pid)

    timestamp = list()
    cpu_precent = list()
    rss_usage = list()
    
    for _ in range(samples):
        timestamp.append(time.time())
        cpu_precent.append(round(process.cpu_percent(interval=interval), 2))
        rss_usage.append(round(process.memory_percent(memtype="rss"), 2))

    resource_data = {
        "timestamp": timestamp,
        "cpu_precent": cpu_precent,
        "rss_usage": rss_usage
    }
    
    return {pname: resource_data}

def main():
    process_deets: list[str] = {val.strip(): get_pid(val.strip()) for val in input("Enter the process names: ").split(",")}
    resource_data: dict = dict()

    with cf.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(resource_tracker, k, v) for k, v in process_deets.items()]

    for future in cf.as_completed(futures):
        resource_data = {**resource_data, **future.result()}

    print(json.dumps(resource_data))
    

if __name__ == '__main__':
    main()