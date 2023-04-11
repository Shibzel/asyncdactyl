from typing import Any, Dict
from datetime import datetime


class BasePteroObject:
    def __init__(self, data: Dict[str, Any]):
        self._raw_data = data
        
    def __dict__(self) -> Dict:
        return self._raw_data
    
    def __repr__(self) -> str:
        return "{}({})".format(
            type(self).__name__,
            ", ".join(f"{k}={repr(v)}" for k, v in self._raw_data)
        )
        
    def __str__(self) -> str:
        return self.__repr__()

    def strptime(self, time: str):
        return datetime.strptime(time, "%Y-%m-%dT%H:%M:%S%z")