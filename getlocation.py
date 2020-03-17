#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to identify country from IP address
Useful if you want to identify a country.
"""

import datetime
import ipaddress
import json
import os
import pprint
import re
import requests
import socket
import sys

from collections import defaultdict, deque
from functools import lru_cache
from typing import List, Dict

LOCATION_API_URL = "https://ipapi.co"

DEBUG = os.environ.get("LOCATION_DEBUG", "False")
ASYNC_FLG = os.environ.get("LOCATION_ASYNC_REQUESTS", "False")


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
Private addresses do not execute the API.
    """
    print(msg)
    sys.exit(1)


class pycolor:
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    PURPLE = "\033[35m"
    CYAN = "\033[36m"
    END = "\033[0m"


def debug_info_deco(func):
    """
    Decorator that displays arguments when calling functions during debugging.
    """

    def wrapper(*args, **kwargs):
        if DEBUG is True:
            now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            print(
                pycolor.BLUE
                + f"[DEBUG]: {now}, {func.__name__}, args: {args}"
                + pycolor.END
            )
        return func(*args, **kwargs)

    return wrapper


def lookup_ip_address():
    """
    Convert from domain to IP address.
    """
    ip = socket.inet_ntoa(struct.pack("!L", random.getrandbits(32)))
    # record = reader.city(str(ip))
    return ip


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


def guess_filename(obj):
    """
    Tries to guess the filename of the given object.
    """
    basestring = None
    name = getattr(obj, "name", None)
    if name and isinstance(name, basestring) and name[0] != "<" and name[-1] != ">":
        return os.path.basename(name)


@debug_info_deco
def read_from_stdin(ip_nums: int) -> List[int]:
    """
    Reads the specified number of lines from stdin.
    If more than the specified number is passed, the rest will be ignored.
    """
    try:
        return [input() for i in range(ip_nums)]
    except KeyboardInterrupt:
        # If standard input is stopped in the middle, it returns an empty List.
        return []


@debug_info_deco
def is_valid_ip(ip_list: List[str]) -> deque:
    """
    Select only IP addresses with the correct format.
    Discard anything that is incorrect.
    """
    que = deque()
    for ip in ip_list:
        try:
            ip = ipaddress.ip_address(ip)
            # Excluded from private address because it
            # will be null at the time of inquiry
            if not ip.is_private:
                que.append(ip)
        except ValueError:
            continue
    return que if len(que) > 0 else False


@debug_info_deco
def print_pretty_json(json_location: dict):
    """
    Format and display the passed json format data
    """
    try:
        json_location = json.loads(json_location)
        ip = json_location["ip"]
        city = json_location["city"]
        region = json_location["region"]
        country = json_location["country"]
        languages = json_location["languages"]

        if country not in ["Ja", "Japan", "JP"]:
            print(pycolor.RED, end="")
        print(
            f"IP:{ip}, city:{city}, region:{region}, country:{country}, languages:{languages}"
        )
        print(pycolor.END, end="")

        # else:
        #     print()
    except KeyError:
        print("Bad result. I couldn't get country information from IP.")
    except TypeError:
        print("The information passed is corrupt. Try running with DEBUG enabled.")


@lru_cache(maxsize=8192, typed=True)
def exec_requests(url: str):
    """
    API execution function.
    The request is not executed because the already
    executed IP address is returned from the cache.
    """
    headers = {"content-type": "application/json"}
    res = requests.get(url, headers=headers, timeout=(3.0, 7.5))

    if res.status_code != 200:
        raise requests.exceptions.HTTPError
    else:
        return 0


def dict_to_sequence(d):
    """
    Returns an internal sequence dictionary update.
    """
    if hasattr(d, "items"):
        d = d.items()

    return d


def url_construction(ip_list: deque):
    """
    Generate URL to hit api.
    Call the function to execute http request based on the generated URL.
    After the call, fetch the json data and call the display function.
    """
    res = None
    for _ in range(len(ip_list)):
        url = f"{LOCATION_API_URL}/{ip_list.popleft()}/json"
        try:
            res = exec_requests(url)
        except requests.exceptions.ConnectTimeout:
            pass
        except Exception as ex:
            print(ex)

        if res:
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
