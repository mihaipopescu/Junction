import logging
from requests.auth import AuthBase
from requests import models

logger = logging.getLogger(__name__)

class HttpBearerAuth(AuthBase):
    def __init__(self, token: str):
        self.token = token

    def __call__(self, r: models.PreparedRequest) -> models.PreparedRequest:
        if  not'Authorization' in r.headers:
            r.headers['Authorization'] = f'Bearer {self.token}'
        else:
            logger.debug('Failed to configure Bearer request authorization since Authorization was already present in request headers.')
        return super().__call__(r)
