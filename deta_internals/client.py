import os
import time
import json
import base64
import requests
from .sign import singature
from typing import Dict, Any, Union, List, Optional
from .utils import Micro, env_to_dict, make_resource_addr


class DetaClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://v1.deta.sh"
        extras = self.__extras()
        self.space_id = extras["spaceID"]
        self.username = extras["name"]
        self.role = extras["role"]
    
    def __extras(self):
        path = "/spaces/"
        return self._request(path=path, method="GET").json()[0]
        
    def _request(
        self,
        path: str,
        method: str,
        headers: dict = {},
        query: dict = {},
        body: Any = None,
        content_type: str = "application/json",
        needs_auth: bool=False,
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
    
    def new(self, micro_name: str, project_name: str = "default") -> Dict[str, Any]:
        runtime = "python3.9"
        path = "/programs/"
        body = {
            "spaceID": self.space_id,
            "project": project_name,
            "name": micro_name,
            "runtime": runtime
        }
        info = self._request(path=path, method="POST", body=body).json()
        if info.get("errors"):
            raise ValueError("a micro already exists with the name: " + micro_name)
        if os.path.exists(f"{micro_name}.json"):
            raise ValueError("a micro already exists here...")
        with open(f"{micro_name}.json", "w") as f:
            json.dump(info, f, indent=4)
        return info 
    
    def update(
        self,
        micro_info_json: os.PathLike,
        *, 
        new_name: Optional[str] = None,
        path_to_env: Optional[os.PathLike] = None,
    ) -> Dict[str, Any]:
        with open(micro_info_json, "r") as f:
            info = json.load(f)
        
        micro = Micro(**info)

        if path_to_env and new_name:
            raise ValueError("You can only update the name or the env_path at a time, not both.")
        
        if new_name:
            path = f"/programs/{micro.id}"
            body = {"name": new_name}
            resp = self._request(path=path, method="PATCH", body=body)
            if resp.status_code == 200:
                micro.name = new_name
                with open(micro_info_json, "w") as f:
                    json.dump(micro.__dict__, f, indent=4)
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
    
    def clone(self, micro_name: str, project_name: str = "default") -> bytes:
        micro_info = self.get_micro_info(micro_name, project_name)
        micro_id, micro_account, micro_region = micro_info["id"], micro_info["account"], micro_info["region"]
        path = f"/viewer/archives/{micro_id}"
        headers = {"X-Resource-Addr": make_resource_addr(micro_account, micro_region)}
        # TODO: handle archieve later
        return self._request(path=path, method="GET", headers=headers).content
    
    def delete_base(self, base: str, project: str = "default") -> Dict[str, Any]:
        path = f"/spaces/{self.username}/projects/{project}/bases/{base}"
        return self._request(path=path, method="DELETE").json()
    
    def delete_drive(self, drive: str, project: str = "default") -> Dict[str, Any]:
        # path = f"/spaces/{self.username}/projects/{project}/drives/{drive}"
        # return self._request(path=path, method="DELETE").json()
        raise NotImplementedError("Drive deletion is not yet implemented.")
    
    def delete_micro(self, micro_id: str) -> Dict[str, Any]:
        path = f"/programs/{micro_id}"
        return self._request(path=path, method="DELETE").json()
    
    def delete_project(self, project_id: str) -> Dict[str, Any]:
        # path = f"/spaces/{self.space_id}/projects/{project_id}"
        # return self._request(path=path, method="DELETE").json()
        raise NotImplementedError("Project deletion is not yet implemented.")

    @property
    def spaces(self) -> List[Dict[str, Any]]:
        path = "/spaces/"
        return self._request(path=path, method="GET").json()

    



