import datetime
import json
import jwt

account_file = "accounts\\account.json"

class Account:
    def __init__(self, username, password, passcodeFile = account_file):
        self.USER = username
        self.PASS = password
    
    def is_correct_pass(self, passwrd):
        return ( passwrd == self.PASS )


class Authenticator:
    def __init__(self, AF = account_file):
        self.Accounts = {}
        self.sessions = {}
        with open(account_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        self.passcode = data["passcode"]
        for acc in data["accounts"]:
            self.Accounts[acc["username"]] = Account(acc["username"],acc["password"])
    
    def authenticate_user(self, username, password):
        if username not in self.Accounts.keys():
            return False
        
        if self.Accounts[username].is_correct_pass(password):
            return True
        return False
    
    def generate_token(self, usr, add = ''):
        payload = {
            "name": usr,
            "add": add,
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1) # 24-hour expiry
        }
        secret_key = self.passcode
        token = jwt.encode(payload, secret_key, algorithm="HS256")
        return token
    
    def decode_token(self, token):
        try:
            # Decode and verify the signature
            decoded_payload = jwt.decode(token, self.passcode, algorithms=["HS256"])
            return decoded_payload
        except jwt.ExpiredSignatureError:
            print("Token has expired")
        except jwt.InvalidTokenError:
            print("Invalid token")
        return None

    def generate_token_session(self, username, password, add=''):
        if self.authenticate_user(username, password):
            token = self.generate_token(username, add)
            self.sessions[username] =add
            return token
        return ''
    
    def confirm_session(self, user, token, add=''):
        session = self.decode_token(token)
        if session and session["name"] == user and session["add"] == add:
            return True
        return False

    
