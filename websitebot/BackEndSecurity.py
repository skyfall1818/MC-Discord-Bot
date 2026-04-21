import datetime
import json
import jwt

account_file = "accounts\\account.json"

class Account:
    Token = ''
    def __init__(self, username, password):
        self.USER = username
        self.PASS = password
    
    def is_correct_pass(self, passwrd):
        return ( passwrd == self.PASS )
    
    def generate_token(self, add = ''):
        payload = {
            "name": self.USER,
            "add": add,
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24) # 24-hour expiry
        }
        secret_key = self.PASS
        token = jwt.encode(payload, secret_key, algorithm="HS256")
        print(f"created token session {token}")
        self.Token = token
        return token
    
    def delete_token(self):
        del self.Token
        self.Token = ''
    
    def is_sametoken(self, t):
        return ( t == self.Token )


class Authenticator:
    def __init__(self, AF = account_file):
        self.Accounts = {}
        self.sessions = []
        with open(account_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        for acc in data["accounts"]:
            self.Accounts[acc["username"]] = Account(acc["username"],acc["password"])
    
    def authenticate_user(self, username, password):
        if username not in self.Accounts.keys():
            return False
        
        if self.Accounts[username].is_correct_pass(password):
            return True
        return False
    
    def generate_token_session(self, username, password, add=''):
        if self.authenticate_user(username, password):
            token = self.Accounts[username].generate_token(add)
            self.sessions.append({ "token" : token, 
                                   "user" : username,
                                   "add" : add})
            return token
        return ''
    
    def confirm_session(self, token, add=''):
        for t,u,a in self.sessions:
            if t == token and (add == '' or a == add):
                return True, u
        return False, ''
    
    def delete_session_by_name(self, name, name_type):
        for s in self.sessions:
            if name_type not in self.s.keys():
                return ''
            if s[name_type] == name:
                return s["user"]
        return ''

    
