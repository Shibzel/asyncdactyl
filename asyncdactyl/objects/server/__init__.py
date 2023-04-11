from typing import Dict, Any, Union
from dataclasses import dataclass

from ..baseobject import BasePteroObject

from .database import BaseDatabase


@dataclass
class Limits:
    memory: int
    swap: int
    disk: int
    io: int
    cpu: int
    threads: Union[str, None] = None
    oom_disabled: Union[bool, None] = None
    
@dataclass
class FeatureLimits:
    databases: int
    allocations: int
    backups: int

class BaseServer(BasePteroObject):
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        
        data = data["data"]
        self.uuid: str = data["uuid"]
        self.identifier: str = data["identifier"]
        self.name: str = data["name"]
        self.description: str = data["description"]
        self.limits = Limits(**data["limit"])
        self.feature_limit = FeatureLimits(**data["feature_limit"])