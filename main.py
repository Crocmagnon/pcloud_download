import hashlib
import logging
import sys

import requests


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

PCLOUD_USER_EMAIL = os.getenv("PCLOUD_USER_EMAIL")
PCLOUD_USER_PASSWORD = os.getenv("PCLOUD_USER_PASSWORD")


def main():
    client = PCloudClient()
    logger.info(client.login())


class PCloudClient:
    def __init__(self):
        self.session = requests.Session()

    def login(self):
        digest = self.get_digest()
        logger.debug("digest %s", digest)
        email_sha = self._sha1(PCLOUD_USER_EMAIL.lower())
        logger.debug("email_sha: %s", email_sha)
        password_digest = self._sha1(PCLOUD_USER_PASSWORD + email_sha + digest)
        return self._get("/userinfo", params={"getauth": 1, "digest": digest, "username": PCLOUD_USER_EMAIL, "passworddigest": password_digest})
        # return self._get("/userinfo", params={"getauth": 1, "username": PCLOUD_USER_EMAIL, "password": PCLOUD_USER_PASSWORD})

    def get_digest(self):
        return self._get("/getdigest").get("digest")
        return data.get("digest")

    @staticmethod
    def _sha1(string):
        return hashlib.sha1(string.encode("utf-8")).hexdigest()

    def _get(self, path, *args, **kwargs):
        url = "https://api.pcloud.com{}".format(path)
        logger.debug("args: %s", args)
        logger.debug("kwargs: %s", kwargs)
        res = self.session.get(url, *args, **kwargs)
        res.raise_for_status()
        return res.json()


if __name__ == "__main__":
    main()
