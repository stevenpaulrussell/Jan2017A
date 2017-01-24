import os
import time
import json

sentry_file_name = '.sentry'


def take_roll_of_new_changes_and_missing(apath):
    global previous_file_data, current_file_data
    previous_file_names = set(previous_file_data.keys())
    current_file_data = get_current_file_stats(apath)
    current_file_names = set(current_file_data.keys())
    new = current_file_names - previous_file_names
    missing = previous_file_names - current_file_names
    persisted = current_file_names.intersection(previous_file_names)
    changed = set()
    for file_name in persisted:
        if current_file_data[file_name] != previous_file_data[file_name]:
            changed.add(file_name)
    previous_file_data = current_file_data
    dump_json_to_dot_sentry(apath)
    return new, changed, missing


def get_current_file_stats(apath):
    current_file_data = {}
    for file_name in os.walk(apath).__next__()[-1]:
        if file_name == sentry_file_name:
            continue
        current_file_data[file_name] = os.stat(os.path.join(apath, file_name)).st_mtime
    return current_file_data


def load_json_from_dot_sentry(apath):
    global previous_file_data
    try:
        with open(os.path.join(apath, sentry_file_name), 'r') as fp:
            previous_file_data = json.load(fp)
    except FileNotFoundError:
        previous_file_data = {}


def dump_json_to_dot_sentry(apath):
    global previous_file_data
    with open(os.path.join(apath, sentry_file_name), 'w') as fp:
        json.dump(previous_file_data, fp)
