from typing import Union

from .baseobject import BasePteroObject


class BaseUser(BasePteroObject):
    def __init__(self, data):
        super().__init__(data)

        data = data["attributes"]
        self.id: int = data["id"]
        self.username: str = data["username"]
        self.email: str = data["email"]
        self.first_name: str = data["first_name"]
        self.last_name: str = data["last_name"]
        self.language: str = data["language"]