from dataclasses import dataclass
from typing import Dict, Any, List
from functools import cached_property
from datetime import datetime

from .baseobject import BasePteroObject


@dataclass
class Allocation:
    id: int
    ip: str
    ip_alias: str
    port: int
    notes: str
    is_default: bool

@dataclass
class EggVariable:
    name: str
    description: str
    env_variable: str
    default_value: str
    server_value: str
    is_editable: bool
    rules: str

class DatabaseHost(BasePteroObject):
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)

        data = data["attributes"]
        self.id: int = data["id"]
        self.name: str = data["name"]
        self.host: str = data["host"]
        self.port: int = data["port"]
        self.username: str = data["username"]
        self.node: int = data["node"]
        self.created_at: datetime = self.strptime(data["created_at"])
        self.updated_at: datetime = self.strptime(data["updated_at"])
    
class Relationships(BasePteroObject):
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        
        default = {"data": []}
        allocations = data.get("allocations", default)
        self.allocations: List[Allocation] = [
            Allocation(**d) for d in allocations["data"]
        ]
        
        variables = data.get("variables", default)
        self.variables: List[EggVariable] = [
            EggVariable(**d) for d in variables["data"]
        ]

        if password := data.get("password"):
            self.password = password["attributes"]["password"]
        else:
            self.password = None

        if host := data.get("host"):
            self.host = DatabaseHost(host)
        else:
            self.host = None
        
    @cached_property
    def default_allocation(self) -> Allocation:
        for allocation in self.allocations:
            if allocation.is_default:
                return allocation