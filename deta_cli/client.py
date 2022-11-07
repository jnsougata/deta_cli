import os
import time
import json
import requests
from .sign import singature
from typing import Dict, Any, Union, List, Optional
from .utils import Micro, env_to_dict, make_resource_addr


class DetaClient:
    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token or os.getenv("DETA_ACCESS_TOKEN")
        assert self.access_token, "You must provide an access token."
        self.base_url = "https://v1.deta.sh"
        self.space_id = None
        self.username = None
        self.role = None
        self.__fill_extras()
    
    def __fill_extras(self):
        path = "/spaces/"
        options = self._request(path=path, method="GET").json()[0]
        self.space_id = options["spaceID"]
        self.username = options["name"]
        self.role = options["role"]
        
    def _request(
        self,
        path: str,
        method: str,
        headers: dict = {},
        query: dict = {},
        body: Any = None,
        content_type: str = "application/json",
    ) -> requests.Response:
        timestamp = str(int(time.time()))
        raw_body = json.dumps(body) if body else ""
        sig = singature(
            access_token=self.access_token,
            http_method=method,
            uri=path,
            timestamp=timestamp,
            content_type=content_type,
            raw_body=raw_body,
        )
        headers["X-Deta-Timestamp"] = timestamp
        headers["X-Deta-Signature"] = sig
        headers["Content-Type"] = content_type
        url = self.base_url + path
        return requests.request(method=method, url=url, headers=headers, params=query, data=raw_body.encode("UTF-8"))
    
    def projects(self) -> Dict[str, Any]:
        path = f"/spaces/{self.space_id}/projects"
        return self._request(path=path, method="GET").json()
    
    def bases(self, project_id: str) -> Dict[str, Any]:
        path = f"/spaces/{self.space_id}/projects/{project_id}/bases"
        return self._request(path=path, method="GET").json()
    
    @classmethod
    def drives(cls, project_key: str) -> Dict[str, Any]:
        project_id = project_key.split("_")[0]
        path = f"https://drive.deta.sh/v1/{project_id}/?last="
        headers = {
            "X-Api-Key": project_key,
        }
        return requests.request(method="GET", url=path, headers=headers).json()
    
    def project_keys(self, project_id: str) -> Dict[str, Any]:
        path = f"/projects/{project_id}/keys"
        return self._request(path=path, method="GET").json()
    
    def get_key(self, project_id: str):
        path = f"/projects/{project_id}/keys"
        return self._request(path=path, method="POST").json()

    def new_micro(self, micro_name: str, project_name: str = "default") -> Dict[str, Any]:
        runtime = "python3.9"
        path = "/programs/"
        body = {
            "spaceID": self.space_id,
            "project": project_name,
            "name": micro_name,
            "runtime": runtime
        }
        return self._request(path=path, method="POST", body=body).json()
    
    def update(
        self,
        micro_info: Dict[str, Any],
        *, 
        new_name: Optional[str] = None,
        path_to_env: Optional[os.PathLike] = None,
    ) -> Dict[str, Any]:
        micro = Micro(**micro_info)
        if path_to_env and new_name:
            raise ValueError("You can only update the name or the env_path at a time, not both.")
        if new_name:
            path = f"/programs/{micro.id}"
            body = {"name": new_name}
            resp = self._request(path=path, method="PATCH", body=body)
            return resp.json()
        
        if path_to_env:
            headers = {"X-Resource-Addr": make_resource_addr(micro.account, micro.region)}
            body = env_to_dict(path_to_env)
            path = f"/programs/{micro.id}/envs"
            resp = self._request(path=path, method="PATCH", body=body, headers=headers)
            return resp.json()
    
    def micro_info(self, micro_name: str, project: str = "default") -> Dict[str, Any]:
        path = f"/spaces/{self.space_id}/projects/{project}/programs/{micro_name}"
        return self._request(path=path, method="GET").json()
    
    def clone_micro(self, micro_name: str, project_name: str = "default") -> bytes:
        micro_info = self.get_micro_info(micro_name, project_name)
        micro_id, micro_account, micro_region = micro_info["id"], micro_info["account"], micro_info["region"]
        path = f"/viewer/archives/{micro_id}"
        headers = {"X-Resource-Addr": make_resource_addr(micro_account, micro_region)}
        # TODO: handle archieve later
        return self._request(path=path, method="GET", headers=headers).content
    
    def delete_base(self, base: str, project: str = "default") -> Dict[str, Any]:
        path = f"/spaces/{self.username}/projects/{project}/bases/{base}"
        return self._request(path=path, method="DELETE").json()
    
    def delete_micro(self, micro_id: str) -> Dict[str, Any]:
        path = f"/programs/{micro_id}"
        return self._request(path=path, method="DELETE").json()
    
    def delete_project(self, project_id: str) -> Dict[str, Any]:
        # path = f"/spaces/{self.space_id}/projects/{project_id}"
        # return self._request(path=path, method="DELETE").json()
        raise NotImplementedError("Project deletion is not yet implemented.")

    def spaces(self) -> List[Dict[str, Any]]:
        path = "/spaces/"
        return self._request(path=path, method="GET").json()
    
    def deploy(self, micro_info: Dict[str, Any], src_path: str) -> Dict[str, Any]:
        micro = Micro(**micro_info)
        patcher_path = f"/patcher/"
        headers = {"X-Resource-Addr": make_resource_addr(micro.account, micro.region)}
        
        files = {}
        for root, _, filenames in os.walk(src_path):
            for filename in filenames:
                # ignore files that begin with '.'
                if filename[0] == '.':
                    continue
                file_path = os.path.join(root, filename)
                with open(file_path, "rb") as f:
                    files[file_path] = f.read().decode("UTF-8", "ignore")
        body = {
            "pid": micro.id,
            "change": files,
        }
        # TODO: broken
        return self._request(path=patcher_path, method="POST", body=body, headers=headers).json()
    
    def add_deps(
        self, 
        micro_id: str, 
        dependencies: List[str], 
        ) -> Dict[str, Any]:
        path = f"/pigeon/commands"
        command = "pip install " + " ".join(dependencies)
        body = {
            "program_id": micro_id,
            "command": command,
        }
        return self._request(path=path, method="POST", body=body).json()

    def remove_deps(
        self, 
        micro_id: str, 
        dependencies: List[str], 
        ) -> Dict[str, Any]:
        path = f"/pigeon/commands"
        command = "pip uninstall " + " ".join(dependencies)
        body = {
            "program_id": micro_id,
            "command": command,
        }
        return self._request(path=path, method="POST", body=body).json()
    
    



