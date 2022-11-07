from .https import request
from typing import Dict, Any, List


class Project:

    def __init__(self, *, data: Dict[str, Any], access_token: str) -> None:
        self.id = data.get("id")
        self.name = data.get("name")
        self.space_id = data.get("space")
        self.created = data.get("created")
        self.region = data.get("region")
        self.access_token = access_token
    
    def bases(self)-> Dict[str, Any]:
        path = f"/spaces/{self.space_id}/projects/{self.id}/bases"
        return request(access_token=self.access_token, path=path, method="GET").json()
    
    def delete_base(self, base_name: str) -> Dict[str, Any]:
        path = f"/spaces/{self.username}/projects/{self.name}/bases/{base_name}"
        return self._request(path=path, method="DELETE").json()
    
    def keys(self) -> Dict[str, Any]:
        path = f"/projects/{self.id}/keys"
        return request(access_token=self.access_token, path=path, method="GET").json()
    
    