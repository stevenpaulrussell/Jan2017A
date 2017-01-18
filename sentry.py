import os
import time
import json

import file_utilities

file_stats = dict(default='should not be seen')

def get_file_stats(apath):
    paths, dirs, files = os.walk(apath).__next__()
    return dirs, files


def load_json_from_dot_sentry(apath):
    global file_stats
    apath = os.path.join(apath, '.sentry')
    try:
        with open(apath, 'r') as fp:
            file_stats = json.load(fp)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        file_stats = {}


def dump_json_to_dot_sentry():
    with open(apath, 'w') as fp:
        json.dump(file_stats, fp)
