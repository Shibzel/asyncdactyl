from .location import Location, LocationAPI
from .nest import Nest, NestAPI
from .node import Node, NodeAPI
from .server import Server, ServerAPI
from .user import User, UserAPI


class ApplicationAPI:
    def __init__(self, client):
        self.client = client