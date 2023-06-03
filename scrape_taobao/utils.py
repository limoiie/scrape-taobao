import random
import time


def fake_pause(min_gap=0.5, max_gap=3.0):
    time.sleep(random.random() * (max_gap - min_gap) + min_gap)
