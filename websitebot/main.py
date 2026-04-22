#################
# imports
#################
import socket
import threading
import time
import random
import json
from BackEndSecurity import Authenticator, FirewallRules

from Message_Queuing import Message_Queue
from MC_bot import message_handler

from flask import Flask, request, jsonify
from flask_cors import CORS
#from flask_socketio import SocketIO, emit
from flask_sock import Sock


# get IP
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # This address doesn't need to be reachable
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


##################
# Global Variables
##################
hostname = socket.gethostname()
local_ip = get_local_ip()
server_port = 5000

# Dictionary to map user IDs to session IDs
connected_users = {}

timeout_connection = 600
allowed_connections = 30

app = Flask(__name__)
# This handles preflight (OPTIONS) requests automatically for all routes
CORS(app)
app.config['SECRET_KEY'] = 'PD'
sock = Sock(app)
Firewall = FirewallRules(server_port)
Auth = Authenticator()

################
# functions
################

def kill_connection_thread():
    global connected_users, timeout_connection
    if connected_users:
        for key in connected_users.keys():
            if time.time() - connected_users[key].updated >= timeout_connection:
                del connected_users[key]
                print(f"Message queue timeout: deleted {key}")
        time.sleep(60)
    else:
        time.sleep(timeout_connection)

def get_ws_id():
    global connected_users, allowed_connections
    keys = connected_users.keys()
    id = 0
    attempts = 5
    while id == 0 and len(connected_users) < allowed_connections and attempts > 0:
        id = random.randint(1000, 9999)
        if id in keys:
            id = 0
        attempts -= 1
    return id

def set_ws_connection(ws_id):
    print(f"New message queue added: {ws_id}")
    connected_users[ws_id] = Message_Queue()

##################
# API message handlers
##################

@app.route('/message', methods=['POST'])
def handle_message():
    global connected_users, Auth
    # 1. Receive the incoming message
    if request.is_json:
        # Parse the JSON data from the request body into a Python dictionary
        ip_addr = request.remote_addr
        print(f'receive message from {ip_addr}')
        incoming_data = request.get_json()

        received_message = incoming_data.get("message", "")
        user = incoming_data.get("user", "")
        ws_id = incoming_data.get("ws_id", "")
        token = incoming_data.get("token", "")
        print(f"{user}: {ws_id} {token}")
        # Log the received message (optional)
        print(f"Received message: {received_message}")

        # 2. Process the message and prepare a reply
        code = 400
        reply_message = ''
        if not received_message:
            reply_message = "Server reply: 'Error did not receive message."
        if not token:
            reply_message = "Server reply: 'Error did not receive token."
        elif Auth.confirm_session(token, user, ip_addr, add = ws_id):
            reply_message = f"Server reply: received '{received_message}'. Status: Success."
            code = 200
            message_args = received_message.split()
            thread = threading.Thread(target=message_handler, args=(connected_users[ws_id],  *message_args))
            thread.start()
        else:
            reply_message = "Server reply: 'Invalid Session please return to Login Screen."
        print(reply_message)
        # 3. Send the reply
        # Return a JSON response with a status code
        return jsonify({
            "status": "received",
            "reply": reply_message
        }), code # 200 OK status code

    else:
        # Handle non-JSON requests
        print("non json file!")
        return jsonify({
            "status": "error",
            "message": "Request must be JSON"
        }), 400 # 400 Bad Request status code
    
@app.route('/request', methods=['POST'])
def handle_request():
    global connected_users, Firewall
    # 1. Receive the incoming message
    if request.is_json:
        # Parse the JSON data from the request body into a Python dictionary
        ip_addr = request.remote_addr
        print(f'receive request from {ip_addr}')
        incoming_data = request.get_json()
        received_message = incoming_data.get("message", "No message provided")
        user = incoming_data.get("user", "")
        ws_id = incoming_data.get("ws_id", "")
        token = incoming_data.get("token", "")

        # Log the received message (optional)
        print(f"Received message: {received_message}")

        # 2. Process the message and prepare a reply
        code = 400
        reply_message = ''
        if not received_message:
            reply_message = "Server reply: 'Error did not receive message."
        if not token:
            reply_message = "Server reply: 'Error did not receive token."

        elif received_message == "register IP":
            Firewall.allowIP(ip_addr)
            reply_message = "Server reply: IP Registered."
            code = 200

        elif Auth.confirm_session(token, user, ip_addr, ws_id):
            code = 200
            my_message_queue = Message_Queue()
            message_handler(my_message_queue, *received_message.split())
            while my_message_queue.Size() > 0:
                reply_message += my_message_queue.Dequeue()['MESSAGE'] + '\n'
        print(f"sending: {reply_message}")
        # 3. Send the reply
        # Return a JSON response with a status code
        return jsonify({
            "status": "received",
            "reply": reply_message
        }), code # 200 OK status code

    else:
        # Handle non-JSON requests
        print("non json file!")
        return jsonify({
            "status": "error",
            "message": "Request must be JSON"
        }), 400 # 400 Bad Request status code

@app.route('/login', methods=['POST'])
def handle_login():
    global Auth, connected_users
    # 1. Receive the incoming message
    if request.is_json:
        # Parse the JSON data from the request body into a Python dictionary
        ip_addr = request.remote_addr
        incoming_data = request.get_json()
        username = incoming_data.get("user", "No message provided")
        password = incoming_data.get("pass", "No message provided")

        # Log the received message (optional)
        print(f"Received account login")

        # 2. Process the message and prepare a reply
        
        reply_message = "fail"
        ws_id = "0"
        token = ""
        if Auth.authenticate_user(username, password):
            reply_message = "Success"
            ws_id = str(get_ws_id())
            token = Auth.generate_token_session(username, password, ip_addr, ws_id)
            connected_users[ws_id] = Message_Queue()
            print(f'login session authorized for: [{ip_addr}]:{username}')
            print(f'websocket ID: {ws_id}')
        print(reply_message)
        # 3. Send the reply
        # Return a JSON response with a status code
        return jsonify({
            "status": "received",
            "reply": reply_message,
            "token": token,
            "ws_id": ws_id
        }), 200 # 200 OK status code

    else:
        # Handle non-JSON requests
        print("non json file!")
        return jsonify({
            "status": "error",
            "message": "Request must be JSON"
        }), 400 # 400 Bad Request status code

@app.route("/")
def home():
    return "Home"

#########################
# Constant webscoket Messaging
#########################

@sock.route('/ws/<user_id>', methods=['GET'])
def handle_socket(ws, user_id):
    global connected_users, Auth
    print(f"found connection ID: {user_id}")
    if int(user_id) not in range(1000,9999):
        print("Invalid ws range")
    elif str(user_id) not in connected_users:
        print("unknown connection closing")
        return
    else:
        try:
            last_call_time = time.time()
            while time.time() - last_call_time < 300:
                if connected_users[user_id].Size() > 0:
                    out = connected_users[user_id].Dequeue()
                    ws.send(json.dumps(out))
                    last_call_time = time.time()
                else:
                    time.sleep(3)
        except Exception as e:
            print(e)
            while user_id in connected_users and connected_users[user_id].sending_status():
                time.sleep(3)
            if user_id in connected_users:
                del connected_users[user_id]
                print(f"Message queue deleted: {user_id}")

if __name__ == '__main__':
    print(f"Running on: {hostname}")
    print(f"Local IP: {local_ip}")
    kill_connections_thread = threading.Thread(target=kill_connection_thread)
    kill_connections_thread.start()
    app.run(debug=True, host=local_ip, port=server_port, ssl_context=('SSL/cert.pem', 'SSL/key.pem'))