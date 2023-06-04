import os
import random
import time


def fake_pause(min_gap=None, max_gap=None):
    min_gap = env_or(min_gap, "FAKE_PAUSE_MIN_GAP", 0.5)
    max_gap = env_or(max_gap, "FAKE_PAUSE_MAX_GAP", 3.0)
    time.sleep(random.random() * (max_gap - min_gap) + min_gap)


def env_or(val, key, default):
    if val is not None:
        return val

    return os.environ.get(key, default)
