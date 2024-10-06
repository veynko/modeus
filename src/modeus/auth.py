import jwt
from datetime import datetime
from typing import Dict
import aiohttp
from bs4 import BeautifulSoup as bs
from uuid import uuid4
import yarl


CLIENT_ID = "sKir7YQnOUu4G0eCfn3tTxnBfzca"
LOGIN_URL = "https://auth.modeus.org/oauth2/authorize"
USER_AGENT = "Modeus_bot"
# USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'


import logging, os, asyncio
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(os.environ.get("LOGLEVEL", logging.DEBUG))


class Token:
    def __init__(self, token: str) -> None:
        self.token = token
        data = jwt.decode(self.token, key=None, options={"verify_signature":False})
        self.expierd = data['exp']
        self.id = data['person_id']
    
    def is_expired(self) -> bool:
        return self.expierd <= datetime.timestamp()


class AuthData:
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password
    
    def getData(self) -> Dict[str, str]:
        return {
            "UserName": self.username,
            "Password": self.password,
            "AuthMethod": "FormsAuthentication"
        }



async def get_token(username: str, password: str) -> None:
    headers = {
        'User-Agent':  USER_AGENT,
        'Accept-Encoding': 'gzip, deflate',
        'Accept': '*/*',
        'Connection': 'keep-alive'
    }

    async with aiohttp.ClientSession(headers=headers) as session:

    
        params = {
            "client_id": CLIENT_ID,
            "redirect_uri": "https://utmn.modeus.org/",
            "response_type": "id_token",
            "scope": "openid",
            "state": str(uuid4()).replace("-", ""),
            "nonce": str(uuid4()).replace("-", "")
        }

        authData = AuthData(username, password)


        async with session.get(LOGIN_URL,  allow_redirects=False, params=params) as response:
                fs_post_link = response.headers['Location']

        # POST запрос для отправки данных формы аутентификации
        async with session.post(yarl.URL(fs_post_link, encoded=True), data=authData.getData(), allow_redirects=False) as fs_link_resp:
            fs_get_link = response.headers['Location']
        
        async with session.get(yarl.URL(fs_get_link, encoded=True), allow_redirects=False) as fs_link_resp:
            soup = bs(await fs_link_resp.text(), 'html.parser')
            inputs = soup.find_all('input')
            SAMLResponse, RelayState = list(map(lambda x: x["value"], inputs))[:2]

        # Формирование данных для последующего POST-запроса
        auth_data = {
            "SAMLResponse": SAMLResponse,
            "RelayState": RelayState
        }


        # POST запрос для передачи SAML и RelayState
        async with session.post("https://auth.modeus.org:443/commonauth", data=auth_data, allow_redirects=False) as auth_resp:
            redirect_url = auth_resp.headers["Location"]

        # Финальные редиректы для получения токена
        async with session.get(yarl.URL(redirect_url, encoded=True), allow_redirects=False) as final_resp:
            auth_url = final_resp.headers["Location"]

        # Извлечение токена из URL
        strat_token = auth_url.find("=")
        stop_token = auth_url.find("&state", strat_token)
        token_str = auth_url[strat_token + 1:stop_token]
        return Token(token_str)

