from urllib.parse import urlencode
from typing import Union

import requests

import dizqueTV.dizquetv_logging as logs


def get(url: str,
        params: dict = None,
        headers: dict = None,
        timeout: int = 2,
        log: str = None) -> Union[requests.Response, None]:
    if params:
        url += f"?{urlencode(params)}"
    try:
        res = requests.get(url=url, headers=headers, timeout=timeout)
        if log:
            logs.log(message=f"GET {url}", level=log)
            logs.log(message=f"Response: {res}", level=("error" if not res else log))
        return res
    except requests.exceptions.Timeout:
        return None


def post(url: str,
         params: dict = None,
         headers: dict = None,
         data: dict = None,
         files: dict = None,
         timeout: int = 2,
         log: str = None) -> Union[requests.Response, None]:
    if params:
        url += f"?{urlencode(params)}"
    try:
        res = requests.post(url=url, json=data, files=files, headers=headers, timeout=timeout)
        if log:
            logs.log(message=f"POST {url}, Body: {data}", level=log)
            logs.log(message=f"Response: {res}", level=("error" if not res else log))
        return res
        # use json= rather than data= to convert single-quoted dict to double-quoted JSON
    except requests.exceptions.Timeout:
        return None


def put(url: str,
        params: dict = None,
        headers: dict = None,
        data: dict = None,
        timeout: int = 2,
        log: str = None) -> Union[requests.Response, None]:
    if params:
        url += f"?{urlencode(params)}"
    try:
        res = requests.put(url=url, json=data, headers=headers, timeout=timeout)
        if log:
            logs.log(message=f"PUT {url}, Body: {data}", level=log)
            logs.log(message=f"Response: {res}", level=("error" if not res else log))
        return res
        # use json= rather than data= to convert single-quoted dict to double-quoted JSON
    except requests.exceptions.Timeout:
        return None


def delete(url: str,
           params: dict = None,
           headers: dict = None,
           data: dict = None,
           timeout: int = 2,
           log: str = None) -> Union[requests.Response, None]:
    if params:
        url += f"?{urlencode(params)}"
    try:
        res = requests.delete(url=url, json=data, headers=headers, timeout=timeout)
        if log:
            logs.log(message=f"DELETE {url}, Body: {data}", level=log)
            logs.log(message=f"Response: {res}", level=("error" if not res else log))
        return res
        # use json= rather than data= to convert single-quoted dict to double-quoted JSON
    except requests.exceptions.Timeout:
        return None
