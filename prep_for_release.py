#!/usr/bin/python3

import argparse
import os
import re
import datetime
from typing import List

parser = argparse.ArgumentParser(description="Prep dizqueTV for release")
parser.add_argument('-v',
                    '--version',
                    type=str,
                    required=True,
                    help='Version of release')
args = parser.parse_args()


class ReplacePair:
    def __init__(self, old_regex: str, new_string: str):
        self.regex = old_regex
        self.new = new_string


def replace(file_path: str, old_new_pairs: List[ReplacePair]):
    content = ""
    temp_file_path = f"{file_path}.temp"

    with open(file_path, 'r+') as f:
        content = f.read()

    for replace_pair in old_new_pairs:
        content = re.sub(replace_pair.regex, replace_pair.new, content, flags=re.M)

    with open(temp_file_path, "w+") as f:
        f.write(content)
    os.replace(temp_file_path, file_path)


# Update version and copyright year in documentation config
doc_conf_file_path = os.path.join(os.path.dirname(__file__), 'docs/source/conf.py')
pairs = [
    ReplacePair(old_regex="(release = \"\d+(\.\d+)+\")", new_string=f"release = \"{args.version}\""),
    ReplacePair(old_regex="(Copyright © \d{4})", new_string=f"Copyright © {datetime.datetime.today().year}")
]
replace(doc_conf_file_path, pairs)

# Update version and copyright year in _info.py
info_file_path = os.path.join(os.path.dirname(__file__), 'dizqueTV/_info.py')
pairs = [
    ReplacePair(old_regex="(__version__ = \'\d+(\.\d+)+\')", new_string=f"__version__ = \'{args.version}\'"),
    ReplacePair(old_regex="(Copyright © \d{4})", new_string=f"Copyright © {datetime.datetime.today().year}")
]
replace(info_file_path, pairs)
