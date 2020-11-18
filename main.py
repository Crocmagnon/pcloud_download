import hashlib
import logging
import os
import sys

import requests

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

PCLOUD_USER_EMAIL = os.getenv("PCLOUD_USER_EMAIL")
PCLOUD_USER_PASSWORD = os.getenv("PCLOUD_USER_PASSWORD")
PCLOUD_USER_REGION = os.getenv("PCLOUD_USER_REGION").lower()


def main():
    client = PCloudClient()
    logger.info(client.login())


class PCloudClient:
    def __init__(self):
        self.session = requests.Session()
        self.auth = None

    def login(self):
        digest = self.get_digest()
        logger.debug("digest %s", digest)
        email_sha = self._sha1(PCLOUD_USER_EMAIL.lower())
        logger.debug("email_sha: %s", email_sha)
        password_digest = self._sha1(PCLOUD_USER_PASSWORD + email_sha + digest)
        res = self._get(
            "/userinfo",
            params={
                "getauth": 1,
                "digest": digest,
                "username": PCLOUD_USER_EMAIL,
                "passworddigest": password_digest,
            },
        )
        self.auth = res["auth"]
        return res

    def get_digest(self):
        return self._get("/getdigest").get("digest")

    @staticmethod
    def _sha1(string):
        return hashlib.sha1(string.encode("utf-8")).hexdigest()

    def _get(self, path, *args, **kwargs):
        base_url = self._get_base_url()
        url = base_url + path
        logger.debug("args: %s", args)
        logger.debug("kwargs: %s", kwargs)
        res = self.session.get(url, *args, **kwargs)
        res.raise_for_status()
        return res.json()

    def _get_base_url(self):
        if PCLOUD_USER_REGION == "us":
            return "https://api.pcloud.com"
        elif PCLOUD_USER_REGION == "eu":
            return "https://eapi.pcloud.com"
        raise ValueError(
            "PCLOUD_USER_REGION doesn't contain a supported value. Supported values: [us, eu]."
        )


if __name__ == "__main__":
    main()
