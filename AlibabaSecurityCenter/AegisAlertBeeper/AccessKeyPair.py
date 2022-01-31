import ujson
from os import path
script_path = path.dirname(path.abspath(__file__)) + "/"


class AccessKeyPair:
    def __init__(self):
        with open(script_path + "config.json", "r") as f:
            access_key_pair = ujson.load(f)
        self.access_id = access_key_pair.get("ali_api_access_id")
        self.access_key = access_key_pair.get("ali_api_access_secret_key")

    def get_access_id(self):
        return self.access_id

    def get_access_key(self):
        return self.access_key

    def main(self) -> None:
        print('access id: ' + self.get_access_key() + '\naccess key: ' + self.get_access_id())


if __name__ == '__main__':
    AccessKeyPair.main(AccessKeyPair())
