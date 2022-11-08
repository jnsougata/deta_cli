import os
import sys
import base64
from typing import Dict


def env_to_dict(env_path: os.PathLike) -> Dict[str, str]:
    with open(env_path, "r") as f:
        env = f.read().splitlines()
    env = [e.split("=") for e in env]
    return {k: v for k, v in env}

def make_resource_addr(account: str, region: str) -> str:
    return base64.b64encode(f"aws:{account}:{region}".encode("UTF-8")).decode("UTF-8")

def read_script(script_path: os.PathLike) -> str:
    with open(script_path, "r") as f:
        return f.read()

def binary_to_base64(binary_path: os.PathLike) -> str:
    with open(binary_path, "rb") as f:
        return base64.b64encode(f.read()).decode("UTF-8")