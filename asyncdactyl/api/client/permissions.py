from dataclasses import dataclass
from typing import Dict, Any

from ...objects import BasePteroObject


@dataclass
class Permission:
    description: str
    keys: Dict[str, str]

class Permissions(BasePteroObject):
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)

        data = data["attributes"]
        self.websocket = Permission(data["websocket"])
        self.control = Permission(data["control"])
        self.user = Permission(data["user"])
        self.file = Permission(data["file"])
        self.backup = Permission(data["backup"])
        self.allocation = Permission(data["allocation"])
        self.startup = Permission(data["startup"])
        self.database = Permission(data["database"])
        self.schedule = Permission(data["schedule"])
        self.settings = Permission(data["settings"])