from google.auth.transport import requests
from google.oauth2 import id_token

import logging

logger = logging.getLogger(__name__)


class Google:
    """Google class to fetch the user info and return it"""

    @staticmethod
    def validate(auth_token):
        """
        validate method Queries the Google oAUTH2 api to fetch the user info
        """
        try:
            idinfo = id_token.verify_oauth2_token(auth_token, requests.Request())

            if "accounts.google.com" in idinfo["iss"]:
                logger.info("Google AUth: Valid token")
                return idinfo

        except Exception:
            logger.info("Google Auth: Invalid token.")
            return "The token is either invalid or has expired"
