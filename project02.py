"""
Dual-threaded dual response time & light measurement
"""

from machine import Pin
import time
import random
import math
import json
import os
import _thread


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

def random_time_interval(tmin: float, tmax: float) -> float:
    """return a random time interval between max and min"""
    return random.uniform(tmin, tmax)

def blinker(N: int) -> None:
    led = machine.Pin("LED", machine.Pin.OUT)
    for _ in range(N):
        led.high()
        time.sleep(0.1)
        led.low()
        time.sleep(0.1)
        
def light_task(params: dict) -> None:
    params = get_params("project02_params.json")
    N = params["N"]
    led = machine.Pin("LED", machine.Pin.OUT)
    adc = machine.ADC(params["photocellPin"])
    pause = params["photocellPause"]
    l: list[int] = []
    #start_time = datetime.now().strftime("%H:%M:%S")
    start_time: tuple[int] = time.localtime() 
    for _ in range(N):
        l.append(adc.read_u16())
        time.sleep(pause) 
    end_time: tuple[int] = time.localtime()
    
    dictionary = {
        "light intensities" : l,
        "start time" : start_time,
        "end time" : end_time,
        "sampling interval (s)" : pause
    }
    
    with open("project02_light.json","w") as outfile:
        json.dump(dictionary, outfile, separators=(',', ':'))
    
    print("light task done")

def button_task(params: dict) -> None:
    #params = get_params("project02_params.json")
    N = params["N"]
    on_ms = params["led_on_ms"]
    buttonPin1 = params["buttonPin1"]
    buttonPin2 = params["buttonPin2"]
    led = Pin("LED", Pin.OUT)
    button1 = Pin(buttonPin1, Pin.IN, Pin.PULL_UP)
    button2 = Pin(buttonPin2, Pin.IN, Pin.PULL_UP)
    onePressed = 0
    twoPressed = 0
    t1: list[float | None] = []
    t2: list[float | None] = []

    blinker(3)

    for i in range(N):
        time.sleep(random_time_interval(0.5, 5.0))
        led.high()
        tic = time.ticks_ms()
        t0 = None
        while time.ticks_diff(time.ticks_ms(), tic) < on_ms:
            if button1.value() == 0 or button2.value() == 0:
                t0 = time.ticks_diff(time.ticks_ms(), tic)
                if button1.value() == 0 and onePressed==0:
                    t1.append(t0)
                    onePressed = 1
                if button2.value() == 0 and twoPressed == 0:
                    t2.append(t0)
                    twoPressed = 1
                if onePressed==1 and twoPressed==1:
                    led.low()
                    break
        if onePressed==0:
            t1.append(None)
        else:
            onePressed = 0
        if twoPressed==0:
            t2.append(None)
        else:
            twoPressed = 0

        led.low()

    blinker(5)

    misses1 = t1.count(None)
    misses2 = t2.count(None)
    print(f"Button 1: You missed the light {misses1} / {N} times")
    print(f"Button 2: You missed the light {misses2} / {N} times")
    
    hits1 = N - misses1
    hits2 = N - misses2

    t1_good = [x for x in t1 if x is not None]
    t2_good = [x for x in t2 if x is not None]
    print(f"Button 1 response times (ms): {t1_good}")
    print(f"Button 2 response times (ms): {t2_good}")

    sum1 =  0
    for x in t1_good:
        sum1 += x 
    sum2 =  0
    for x in t2_good:
        sum2 += x

    if misses1 < N:
        avg1 = sum1 / len(t1_good)
        min_t1 = min(t1_good)
        max_t1 = max(t1_good)
        print(f"Button 1 average response time was {avg1} ms")
        print(f"Button 1 minimum response time was {min_t1} ms")
        print(f"Button 1 maximum response time was {max_t1} ms")
    else:
        avg1 = "N/A"
        min_t1 = "N/A"
        max_t1 = "N/A"
    if misses2 < N:
        avg2 = sum2 / len(t2_good)
        min_t2 = min(t2_good)
        max_t2 = max(t2_good)
        print(f"Button 2 average response time was {avg2} ms")
        print(f"Button 2 minimum response time was {min_t2} ms")
        print(f"Button 2 maximum response time was {max_t2} ms")
    else:
        avg2 = "N/A"
        min_t2 = "N/A"
        max_t2 = "N/A"

    scoreLabel1 = f"Button 1 score (# hit out of {N})"
    scoreLabel2 = f"Button 2 score (# hit out of {N})"

    dictionary = {
        "Button 1 response times (ms)": t1_good,
        "Button 1 average response time (ms)": avg1,
        "Button 1 minimum response time (ms)": min_t1,
        "Button 1 maximum response time (ms)": max_t1,
        scoreLabel1: hits1,
        "Button 2 response times (ms)": t2_good,
        "Button 2 average response time (ms)": avg2,
        "Button 2 minimum response time (ms)": min_t2,
        "Button 2 maximum response time (ms)": max_t2,
        scoreLabel2: hits2
    }

    with open("project02_button.json","w") as outfile:
        json.dump(dictionary, outfile, separators=(',', ':'))
        
    print("button task done")


params = get_params("project02_params.json")
_thread.start_new_thread(button_task,(params,))
light_task(params)

