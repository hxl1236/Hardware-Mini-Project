"""
Response time - single-threaded
"""

from machine import Pin
import time
import random
import math
import json
import os


def get_params(param_file: str) -> dict:
    if not is_regular_file(param_file):
        raise OSError(f"File {param_file} not found")
    with open(param_file) as f:
        params = json.load(f)
    return params
def is_regular_file(path: str) -> bool:
    S_IFREG = 0x8000
    try:
        return os.stat(path)[0] & S_IFREG != 0
    except OSError:
        return False
    
params = get_params("project01_params.json")
N = params["N"]
on_ms = params["on_ms"]
buttonPin = params["buttonPin"]

led = Pin("LED", Pin.OUT)
button = Pin(buttonPin, Pin.IN, Pin.PULL_UP)


def random_time_interval(tmin: float, tmax: float) -> float:
    """return a random time interval between max and min"""
    return random.uniform(tmin, tmax)


def blinker(N: int) -> None:
    # %% let user know game started / is over

    for _ in range(N):
        led.high()
        time.sleep(0.1)
        led.low()
        time.sleep(0.1)


t: list[float | None] = []

blinker(3)

for i in range(N):
    time.sleep(random_time_interval(0.5, 5.0))

    led.high()

    tic = time.ticks_ms()
    t0 = None
    while time.ticks_diff(time.ticks_ms(), tic) < on_ms:
        if button.value() == 0:
            t0 = time.ticks_diff(time.ticks_ms(), tic)
            led.low()
            break
    t.append(t0)

    led.low()

blinker(5)

# %% collate results
misses = t.count(None)
print(f"You missed the light {misses} / {N} times")

hits = N - misses

t_good = [x for x in t if x is not None]

# how to print the average, min, max response time?

print(f"response times (ms): {t_good}")

sum =  0
for x in t_good:
    sum += x

if misses < N:
    avg = sum / len(t_good)
    min_t = min(t_good)
    max_t = max(t_good)
    print(f"The average response time was {avg} ms")
    print(f"The minimum response time was {min_t} ms")
    print(f"The maximum response time was {max_t} ms")
else:
    avg = "N/A"
    min_t = "N/A"
    max_t = "N/A"

#scoreStr = str(misses) + "/" + str(N) + " missed"
scoreLabel = f"score (# hit out of {N})"


dictionary = {
    "response times (ms)": t_good,
    "average response time (ms)": avg,
    "minimum response time (ms)": min_t,
    "maximum response time (ms)": max_t,
    scoreLabel: hits
}

#json_object = json.dumps(dictionary, indent=4)

with open("project01.json","w") as outfile:
    #outfile.write(json_object)
    json.dump(dictionary, outfile, separators=(',', ':'))