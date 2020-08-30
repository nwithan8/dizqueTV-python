from urllib.parse import urlencode
from typing import Union

import requests

import dizqueTV.logging as logs


def get(url: str,
        params: dict = None,
        headers: dict = None,
        timeout: int = 2,
        log: str = None) -> Union[requests.Response, None]:
    if params:
        url += f"?{urlencode(params)}"
    if log:
        logs.log(message=f"GET {url}", level=log)
    try:
        return requests.get(url=url, headers=headers, timeout=timeout)
    except requests.exceptions.Timeout:
        return None


def post(url: str,
         params: dict = None,
         headers: dict = None,
         data: dict = None,
         timeout: int = 2,
         log: str = None) -> Union[requests.Response, None]:
    if params:
        url += f"?{urlencode(params)}"
    if log:
        logs.log(message=f"POST {url}, Body: {data}", level=log)
    try:
        return requests.post(url=url, json=data, headers=headers, timeout=timeout)
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
    if log:
        logs.log(message=f"PUT {url}, Body: {data}", level=log)
    try:
        return requests.put(url=url, json=data, headers=headers, timeout=timeout)
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
    if log:
        logs.log(message=f"DELETE {url}", level=log)
    try:
        return requests.delete(url=url, json=data, headers=headers, timeout=timeout)
        # use json= rather than data= to convert single-quoted dict to double-quoted JSON
    except requests.exceptions.Timeout:
        return None
