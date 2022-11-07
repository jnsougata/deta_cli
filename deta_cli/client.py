import os
import requests
from .https import request
from .micro import Micro
from .project import Project
from typing import Dict, Any, List, Optional


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
        options = request(access_token= self.access_token, path=path, method="GET").json()[0]
        self.space_id = options["spaceID"]
        self.username = options["name"]
        self.role = options["role"]
        
    def projects(self) -> List[Project]:
        path = f"/spaces/{self.space_id}/projects"
        projects = request(access_token=self.access_token,path=path, method="GET").json()['projects']
        return [Project(data=project, access_token=self.access_token) for project in projects]
    
    def get_project(self, name: str) -> Dict[str, Any]:
        path = f"/spaces/{self.space_id}/projects"
        projects = request(access_token=self.access_token,path=path, method="GET").json()['projects']
        for project in projects:
            if project['name'] == name:
                return Project(data=project, access_token=self.access_token)
    
    @classmethod
    def drives(cls, project_key: str) -> Dict[str, Any]:
        project_id = project_key.split("_")[0]
        path = f"https://drive.deta.sh/v1/{project_id}/?last="
        headers = {
            "X-Api-Key": project_key,
        }
        return requests.request(method="GET", url=path, headers=headers).json()
    
    def get_micro(self, name: str, project: str = "default") -> Micro:
        path = f"/spaces/{self.space_id}/projects/{project}/programs/{name}"
        return Micro(request(access_token= self.access_token, path=path, method="GET").json(), self.access_token)

    def create_micro(self, name: str, project: str = "default") -> Micro:
        runtime = "python3.9"
        path = "/programs/"
        body = {
            "spaceID": self.space_id,
            "project": project,
            "name": name,
            "runtime": runtime
        }
        return Micro(request(access_token= self.access_token, path=path, method="POST", body=body).json(), self.access_token)
    
    def spaces(self) -> List[Dict[str, Any]]:
        path = "/spaces/"
        return request(access_token= self.access_token, path=path, method="GET").json()
    