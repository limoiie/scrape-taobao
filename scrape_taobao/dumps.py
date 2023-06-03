import json
import sys
from contextlib import nullcontext
from typing import Optional

import yaml


def dump(data: dict, out_path: Optional[str], fmt: str):
    """
    Dump data to file or stdout.

    :param data: data to dump
    :param out_path: output file path, if None, dump to stdout
    :param fmt: output format, support 'json' and 'yaml'
    """
    stream_guard = open(out_path, "w+") if out_path else nullcontext(sys.stdout)
    with stream_guard as stream:
        if fmt == "json":
            json.dump(data, stream, ensure_ascii=False, indent=2)
        elif fmt in ["yaml", "yml"]:
            yaml.dump(data, stream, allow_unicode=True, indent=2)
        else:
            raise ValueError("unsupported format: {}".format(fmt))
