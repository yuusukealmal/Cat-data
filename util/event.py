import os, json
import random, time, datetime
import requests, hashlib, hmac
from .funcs import git_push

class EventOld:
    def __init__(self):
        self.aws_access_key_id = "AKIAJCUP3WWCHRJDTPPQ"
        self.aws_secret_access_key = "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"
        self.region = "ap-northeast-1"
        self.service = "s3"
        self.request = "aws4_request"
        self.algorithm = "AWS4-HMAC-SHA256"
        self.domain = "nyanko-events-prd.s3.ap-northeast-1.amazonaws.com"
        self.url = "https://{}/battlecats{}_production/{}.tsv"

    def get_auth_header(self):
        output = self.algorithm + " "
        output += f"Credential={self.aws_access_key_id}/{self.get_date()}/{self.region}/{self.service}/{self.request}, "
        output += f"SignedHeaders=host;x-amz-content-sha256;x-amz-date, "
        signature = self.get_signing_key(self.get_amz_date())
        output += f"Signature={signature.hex()}"
        return output

    def get_date(self):
        return datetime.datetime.utcnow().strftime("%Y%m%d")

    def get_amz_date(self):
        return datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

    def get_signing_key(self, amz: str):
        k = ("AWS4" + self.aws_secret_access_key).encode()
        k_date = self.hmacsha256(k, self.get_date())
        date_region_key = self.hmacsha256(k_date, self.region)
        date_region_service_key = self.hmacsha256(date_region_key, self.service)
        signing_key = self.hmacsha256(date_region_service_key, self.request)

        string_to_sign = self.get_string_to_sign(amz)

        final = self.hmacsha256(signing_key, string_to_sign)
        return final

    def hmacsha256(self, key: bytes, message: str) -> bytes:
        return hmac.new(key, message.encode(), hashlib.sha256).digest()

    def get_string_to_sign(self, amz: str):
        output = self.algorithm + "\n"
        output += amz + "\n"
        output += (
            self.get_date()
            + "/"
            + self.region
            + "/"
            + self.service
            + "/"
            + self.request
            + "\n"
        )
        request = self.get_canonical_request(amz)
        output += hashlib.sha256(request.encode()).hexdigest()
        return output

    def get_canonical_request(self, amz: str):
        output = "GET\n"
        output += self.get_canonical_uri() + "\n" + "\n"
        output += "host:" + self.domain + "\n"
        output += "x-amz-content-sha256:UNSIGNED-PAYLOAD\n"
        output += "x-amz-date:" + amz + "\n"
        output += "\n"
        output += "host;x-amz-content-sha256;x-amz-date\n"
        output += "UNSIGNED-PAYLOAD"
        return output

    def get_canonical_uri(self):
        return self.url.split(self.domain)[1]

    def make_request(self, cc: str, file: str):
        url = self.url.format(self.domain, cc, file)
        headers = {
            "accept-encoding": "gzip",
            "authorization": self.get_auth_header(),
            "connection": "keep-alive",
            "host": self.domain,
            "user-agent": "Dalvik/2.1.0 (Linux; U; Android 9; Pixel 2 Build/PQ3A.190801.002)",
            "x-amz-content-sha256": "UNSIGNED-PAYLOAD",
            "x-amz-date": self.get_amz_date(),
        }

        return requests.get(url, headers=headers)

    def to_file(self, cc: str, file: str):
        response = self.make_request(cc, file)
        return response.content

class EventNew:
    def __init__(self):
        self.accountCode = None
        self.password = None
        self.passwordRefreshToken = None
        self.jwtToken = None
        self.tokenCreatedAt = None
        self.newEventLink = "https://nyanko-events.ponosgames.com/battlecats{}_production/{}.tsv?jwt="
        self.userCreateLink = "https://nyanko-backups.ponosgames.com/?action=createAccount&referenceId="
        self.passwordLink = "https://nyanko-auth.ponosgames.com/v1/users"
        # self.passwordRefreshLink = "https://nyanko-auth.ponosgames.com/v1/user/password"
        self.jwtLink = "https://nyanko-auth.ponosgames.com/v1/tokens"

    def generateRandomHex(self, length: int) -> str:
        return ''.join(random.choice('0123456789abcdef') for _ in range(length))

    def hmacSha256(self, key, content):
        return hmac.new(key, str(content).encode('utf-8'), hashlib.sha256).digest()

    def getNyankoSignature(self, json_text):
        random_data = self.generateRandomHex(64)
        return random_data + self.hmacSha256(bytes(self.accountCode + random_data, 'utf-8'), json_text).hex()

    def getPostResponse(self, url, json_text):
        headers = {
            "Nyanko-Signature": self.getNyankoSignature(json_text),
            "Nyanko-Signature-Version": "1",
            "Nyanko-Signature-Algorithm": "HMACSHA256",
            "Content-Type": "application/json",
            "Nyanko-Timestamp": str(int(time.time()* 1000)),
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; XQ-BC52 Build/61.2.A.0.447)",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip"
        }
        return requests.post(url=url, headers=headers, data=json_text.encode("utf-8"))

    def generateAccount(self):
        self.accountCode = None
        self.password = None
        self.passwordRefreshToken = None
        acc = requests.get(self.userCreateLink)
        if acc.json()['success'] == True:
            self.accountCode = acc.json()['accountId']
        passwordHeaderData = {
            'accountCode': self.accountCode,
            'accountCreatedAt': str(int(time.time())),
            'nonce': self.generateRandomHex(32),
        }
        passwordResponse = self.getPostResponse(self.passwordLink, json.dumps(passwordHeaderData).replace(" ", ""))
        if passwordResponse.json()['statusCode'] == 1:
            self.password = passwordResponse.json()['payload']['password']
            self.passwordRefreshToken = passwordResponse.json()['payload']['passwordRefreshToken']

    def generateJWTToken(self):
        if self.accountCode == None or self.password == None:
            return
        tokenData = {
            'accountCode': self.accountCode,
            'clientInfo': {
            'client':{
                'countryCode': 'ja',
                'version': '999999',
                },
            'device':{
                'model': 'XQ-BC52'
                },
            'os':{
                'type': 'android',
                'version': 'Android 13'
                }
            },
            'nonce': self.generateRandomHex(32),
            'password': self.password
        }
        tokenResponse = self.getPostResponse(self.jwtLink, json.dumps(tokenData).replace(" ", ""))
        if tokenResponse.json()['statusCode'] == 1:
            return tokenResponse.json()['payload']['token']
        
    def get_token(self):
        self.generateAccount()
        self.jwtToken = self.generateJWTToken()
        self.tokenCreatedAt = int(time.time() * 1000)
        
    def to_file(self, cc: str, file: str):
        cc = "" if cc == "jp" else cc
        data = requests.get(self.newEventLink.format(cc, file) + self.jwtToken).content
        return data


def event(old=None, new=None):
    cc = ["jp", "tw", "en", "kr"]
    file_types = ["sale", "gatya", "item"]

    if old:
        event = EventOld()
        for c in cc:
            for f in file_types:
                process(event, c, f)

    if new:
        event = EventNew()
        event.get_token()
        for c in cc:
            for f in file_types:
                process(event, c, f)
            git_push("add", f"Update Certain Game {c.upper()} Event Data")

def process(cls, cc: str, file: str):
    data = cls.to_file(cc, file)

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    target_dir = os.path.join(base_dir, "Data", "event")
    file = os.path.join(target_dir, f"{cc.upper()}_{file}.tsv")
    
    with open(file, "wb") as f:
        f.write(data)