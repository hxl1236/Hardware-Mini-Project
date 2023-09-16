"""
Response time - single-threaded
"""

from machine import Pin
import time
import random
import math
import json


led = Pin("LED", Pin.OUT)
button = Pin(14, Pin.IN, Pin.PULL_UP)

N: int = 10
sample_ms = 10.0
on_ms = 500


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

t_good = [x for x in t if x is not None]

# how to print the average, min, max response time?

print(t_good)

sum =  0
for x in t_good:
    sum += x

if misses < N:
    avg = sum / len(t_good)
    min_t = min(t_good)
    max_t = max(t_good)
    print(f"The average response time is {avg}")
    print(f"The minimum response time is {min_t}")
    print(f"The maximum response time is {max_t}")
else:
    avg = "N/A"
    min_t = "N/A"
    max_t = "N/A"

word = str(misses) + "/" + str(N) + " times"

dictionary = {
    "response times" : t_good,
    "average response time" : avg,
    "minimum response time" : min_t,
    "maximum response time" : max_t,
    "score" : word
}

#json_object = json.dump(dictionary, indent=5)

with open("project01.json","w") as outfile:
    #outfile.write(json_object)
    json.dump(dictionary, outfile)
