import os
import secrets
from .https import request
from typing import Dict, Any, List, Optional
from .utils import env_to_dict, make_resource_addr


class Micro:

    def __init__(self, info: Dict[str, Any], access_token: str) -> None:
        self.id: Optional[str] = info.get("id")
        self.space: Optional[str] = info.get("space")
        self.group: Optional[str] = info.get("group")
        self.name: Optional[str] = info.get("name")
        self.role: Optional[str] = info.get("role")
        self.code: Optional[str] = info.get("code")
        self.path: Optional[str] = info.get("path")
        self.runtime: Optional[str] = info.get("runtime")
        self.lib: Optional[str] = info.get("lib")
        self.account: Optional[str] = info.get("account")
        self.region: Optional[str] = info.get("region")
        self.memory: Optional[int] = info.get("memory")
        self.timeout: Optional[int] = info.get("timeout")
        self.created: Optional[str] = info.get("created")
        self.http_auth: bool = info.get("http_auth", False)
        self.log_level: Optional[str] = info.get("log_level")
        self.api_key = info.get("api_key")
        self.forked_from: Optional[str] = info.get("forked_from")
        self.path_alias: Optional[str] = info.get("path_alias")
        self.project: Optional[str] = info.get("project")
        self.custom_domains: Optional[str] = info.get("custom_domains")
        self._access_token = access_token

    def __repr__(self) -> str:
        return f"Micro(name={self.name}, id={self.id}, space={self.space})"
    
    @classmethod
    def from_data(cls, data: Dict[str, Any], access_token: str) -> "Micro":
        return cls(data, access_token)
    
    def delete(self) -> Dict[str, Any]:
        path = f"/programs/{self.id}"
        return self._request(path=path, method="DELETE").json()

    def update_name(self, name: str) -> Dict[str, Any]:
        if not name:
            return
        return request(
            access_token=self._access_token,
            path=f"/programs/{self.id}", 
            method="PATCH", 
            body={"name": name}
        ).json()
    
    def update_env(self, path: Optional[os.PathLike]) -> Dict[str, Any]:
        if not path:
            return
        return request(
            access_token=self._access_token,
            path=f"/programs/{self.id}/envs", 
            method="PATCH", 
            body=env_to_dict(path), 
            headers={"X-Resource-Addr": make_resource_addr(self.account, self.region)}
        ).json()
    
    def download_src(self) -> bytes:
        # TODO: handle archieve later
        return request(
            access_token=self._access_token,
            path=f"/viewer/archives/{self.id}", 
            method="GET", 
            headers={"X-Resource-Addr": make_resource_addr(self.account, self.region)}
        ).content
    
    def add_deps(self, dependencies: List[str]) -> Dict[str, Any]:
        path = f"/pigeon/commands"
        command = "pip install " + " ".join(dependencies)
        body = {
            "program_id": self.id,
            "command": command,
        }
        return request(access_token=self._access_token,path=path, method="POST", body=body).json()

    def remove_deps(self, dependencies: List[str]) -> Dict[str, Any]:
        path = f"/pigeon/commands"
        command = "pip uninstall " + " ".join(dependencies)
        body = {
            "program_id": self.id,
            "command": command,
        }
        return request(access_token=self._access_token,path=path, method="POST", body=body).json()

    def deploy(self, *, changed_files: List[str], deleted_files: List[str]) -> Dict[str, Any]:
        changes = {file: secrets.token_hex(32) for file in changed_files}
        body = {
            "pid": self.id,
            "change": changes,
            "delete": deleted_files,
        }
        path = f"/patcher/"
        headers = {"X-Resource-Addr": make_resource_addr(self.account, self.region)}
        return self._request(path=path, method="POST", body=body, headers=headers).json()
