import os
import base64
from typing import Dict, Any
from dataclasses import dataclass, field

@dataclass(frozen=False)
class Micro:
    id: str
    space: int
    group: str
    name: str
    role: str
    code: str
    path: str
    runtime: str
    lib: str
    account: str
    region: str
    memory: int
    timeout: int
    created: str
    http_auth: bool
    log_level: str
    api_key: bool
    forked_from: str
    path_alias: str
    project: str
    custom_domains: str

def env_to_dict(env_path: os.PathLike) -> Dict[str, str]:
    with open(env_path, "r") as f:
        env = f.read().splitlines()
    env = [e.split("=") for e in env]
    env = {k: v for k, v in env}
    return env

def make_resource_addr(account: str, region: str) -> str:
    return base64.b64encode(f"aws:{account}:{region}".encode("UTF-8")).decode("UTF-8")