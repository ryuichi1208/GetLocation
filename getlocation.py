#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import ipaddress
import json
import os
import pprint
import re
import requests
import sys

from collections import defaultdict, deque
from functools import lru_cache
from typing import List, Dict

DEBUG = os.environ.get('LOCATION_DEBUG', 'False')
LOCATION_API_URL = "https://ipapi.co"

def usage():
    msg = """
Usage: python3 getlocation.py N
               IPAddr 1
               IPAddr 2
               IPAddr ...
               IPAddr N

Enter the number of the IP address you want to check in N.
Do not enter more than one IP address per line.
Please enter a number between 1 and 100.
    """
    print(msg)
    sys.exit(1)


def debug_info_deco(func):
    class pycolor:
        YELLOW = '\033[33m'
        BLUE = '\033[34m'
        PURPLE = '\033[35m'
        END = '\033[0m'

    def wrapper(*args, **kwargs):
        if DEBUG == True:
            now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            print(pycolor.BLUE\
                  + f"[DEBUG]: {now}, {func.__name__}, args: {args}"\
                  + pycolor.END)
        return func(*args, **kwargs)
    return wrapper


@debug_info_deco
def check_args_validate(args: List[str]):
    """
    Function for checking the legitimacy of an option.
    Details are written in usage.
    """
    if len(args) != 2 or not args[1].isdigit():
        return False, 0
    elif not 0 < int(args[1]) < 100:
        return False, 0

    return True, int(args[1])


@debug_info_deco
def read_from_stdin(ip_nums: int) -> List[int]:
    """
    Reads the specified number of lines from stdin.
    If more than the specified number is passed, the rest will be ignored.
    """
    return [input() for i in range(ip_nums)]


@debug_info_deco
def is_valid_ip(ip_list: List[str]) -> deque:
    """
    Select only IP addresses with the correct format.
    Discard anything that is incorrect.
    """
    que = deque()
    for ip in ip_list:
        try:
            que.append(ipaddress.ip_address(ip))
        except ValueError:
            continue
    return que if len(que) > 0 else False


@debug_info_deco
def print_pretty_json(json_location: dict):
    """
    Format and display the passed json format data
    """
    json_location = json.loads(json_location)
    print(f"IP = {json_location['ip']} \
          Country = {json_location['country']} \
          City = {json_location['city']}")


@lru_cache(maxsize=None)
def exec_requests(url: str):
    """
    API execution function.
    The request is not executed because the already
    executed IP address is returned from the cache.
    """
    headers = {"content-type": "application/json"}
    return requests.get(url, headers=headers, timeout=(3.0, 7.5))


def url_construction(ip_list: deque):
    """
    Generate URL to hit api.
    Call the function to execute http request based on the generated URL.
    After the call, fetch the json data and call the display function.
    """
    for _ in range(len(ip_list)):
        url = f"{LOCATION_API_URL}/{ip_list.popleft()}/json"
        try:
            res = exec_requests(url)
        except requests.exceptions.ConnectTimeout:
            pass
        except Exception as ex:
            print(ex)

        print_pretty_json(json.dumps(res.json()))


def main(args):
    flg, ip_nums = check_args_validate(args)

    if not flg:
        usage()

    ip_list = is_valid_ip(read_from_stdin(ip_nums))
    if not ip_list:
        usage()

    url_construction(ip_list)


if __name__ == "__main__":
    main(sys.argv)
