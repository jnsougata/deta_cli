import os
import sys
import base64
from typing import Dict, List


def env_to_dict(env_path: os.PathLike) -> Dict[str, str]:
    with open(env_path, "r") as f:
        env = f.read().splitlines()
    env = [e.split("=") for e in env]
    env = {k: v for k, v in env}
    return env

def make_resource_addr(account: str, region: str) -> str:
    return base64.b64encode(f"aws:{account}:{region}".encode("UTF-8")).decode("UTF-8")

def file_to_base64(content: bytes) -> str:
    return base64.b64encode(content).decode("UTF-8")