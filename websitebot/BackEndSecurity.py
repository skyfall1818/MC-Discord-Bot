import datetime
import json
import jwt
import subprocess

account_file = "accounts\\account.json"

class Account:
    def __init__(self, username, password):
        self.USER = username
        self.PASS = password
    
    def is_correct_pass(self, passwrd):
        return ( passwrd == self.PASS )


class Authenticator:
    def __init__(self, AF = account_file):
        self.Accounts = {}
        self.sessions = {}
        with open(AF, 'r', encoding='utf-8') as file:
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
    
    def generate_token(self, usr, ip, add = ''):
        payload = {
            "name": usr,
            "ip": ip,
            "add": add,
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1) # 1-hour expiry
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

    def generate_token_session(self, username, password, ip, add=''):
        if self.authenticate_user(username, password):
            token = self.generate_token(username, ip, add)
            self.sessions[username] =add
            return token
        return ''
    
    def confirm_session(self, token, user, ip, add=''):
        session = self.decode_token(token)
        if session and session["name"] == user and session["add"] == add and session["ip"] == ip:
            return True
        return False

class FirewallRules:
    allow_ip = {}
    def __init__(self, server_port):
        self.serverPort = server_port
        subprocess.run('netsh advfirewall firewall delete rule name="Minecraft Whitelist"', shell=True)
        subprocess.run('netsh advfirewall firewall delete rule name="Website api Whitelist"', shell=True)
        subprocess.run(f'netsh advfirewall firewall add rule name="Website api Whitelist" dir=in action=allow protocol=TCP localport={server_port}', shell=True)
    
    def allowIP(self, ip):
        self.allow_ip[ip] = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        self.purgeRules()
        self.updateFireWallRules()
    
    def purgeRules(self):
        now = datetime.datetime.utcnow()
        for ip in self.allow_ip.keys():
            if now > self.allow_ip[ip]:
                del self.allow_ip[ip]
    
    def updateFireWallRules(self):
        allow_ip_text = ",".join(self.allow_ip.keys())
        subprocess.run('netsh advfirewall firewall delete rule name="Minecraft Whitelist"', shell=True)
        subprocess.run(f'netsh advfirewall firewall add rule name="Minecraft Whitelist" dir=in action=block protocol=TCP localport=25565 remoteip={allow_ip_text}', shell=True)


