import discord # need pipinstall
import os
import os.path
import sys
import subprocess # need pip install i think
import threading
import time
import math
import asyncio
from datetime import date
#from requests import get
import psutil #need pip install
import http.server
import ssl
import urllib.request

KEY_FILE = 'ImportantCode.txt'
MC_FILE_LOCATION = ''
TOKEN = ''
KEYWORD = ''
README = 'README.txt'
ADMIN_TAG = ''
SERVER_NAME = ''
PROCESS = None
GAME_LOG_LENGTH = 40
LOG = ['' for _ in range(GAME_LOG_LENGTH)]
LOG_PT = 0

HOLD_PT = 0

PLAYER_NUM = 0

START_UP = False

TIMER_ON = False

def messageFormatter(title, message, replace = False):
    return f'**{title}**\n{message}'

with open(KEY_FILE, "r") as file:
    for line in file:
        try:
            name, val = line.split('|')
            if val != '' and val != ' ':
                if name == 'Token':
                    TOKEN = val.replace('\n','')
                elif name == 'MC File':
                    MC_FILE_LOCATION = val.replace('\n','')
                elif name == 'Char Key':
                    KEYWORD = val.replace('\n','')
                elif name == 'Admin Tag':
                    ADMIN_TAG = val.replace('\n','')
        except:
            print("Error: cannot split line")

async def on_ready():
    guild_count = 0
    # LOOPS THROUGH ALL THE GUILD / SERVERS THAT THE BOT IS ASSOCIATED WITH.
    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")
    	# INCREMENTS THE GUILD COUNTER.
        guild_count = guild_count + 1
	# PRINTS HOW MANY GUILDS / SERVERS THE BOT IS IN.
        print("SampleDiscordBot is in " + str(guild_count) + " guilds.")
# EVENT LISTENER FOR WHEN A NEW MESSAGE IS SENT TO A CHANNEL.

async def help(Message_Manager):
    text=''
    with open(README, 'r') as f:
        text = f.read()
    await 'Help','```' + text +'```'

async def _run(Message_Manager, index = ''):
    if index == '':
        await list_games(Message_Manager)
    else:
        out, title= set_game(index)
        if out:

            message = messageFormatter(f'Starting Server - **{title}**', f'```Loading...```')
            new_message = await Message_Manager.send(message)
            
            out_line = get_std_out_line()
            while check_running() and '%' not in out_line:
                if ']: ' in out_line:
                    out_line = out_line.split(']: ')[1]
                if len(out_line) > 70:
                    out_line = out_line[:67] + '...'

                message = messageFormatter(f'Starting Server - **{title}**', f'```{out_line}```')
                await new_message.edit(embed = em)
                
                time.sleep(0.1)
                out_line = get_std_out_line()
            while check_running() and '%' in out_line:
                if ']: ' in out_line:
                    out_line = out_line.split(']: ')[1]
                if len(out_line) > 70:
                    out_line = out_line[:67] + '...'

                message =(f'Starting Server - **{title}**', f'```{out_line}```')
                await new_message.edit(embed = em)
                
                time.sleep(0.05)
                out_line = get_std_out_line()
            if check_running():
                START_UP = True
                message =(f'Starting Server - **{title}**', f'```Done!```')
                await new_message.edit(embed = em)
            else:
                await Message_Manager.send(messageHandler('Error', 'ERROR: server crashed on startup. check your settings', RED))
        else:
            await Message_Manager.send(embed = embed('Error', 'ERROR: did not find folder', RED))

async def _stop(Message_Manager):
    global PROCESS
    PROCESS.stdin.write('stop\n'.encode())
    PROCESS.stdin.flush()
    out_line = get_std_out_line()
    message =(f'Closing Server - **{SERVER_NAME}**', f'```Loading...```', ORANGE)
    new_message = await Message_Manager.send(embed = em)
    while check_running():
        if ']: ' in out_line:
            out_line = out_line.split(']: ')[1]
        if len(out_line) > 70:
            out_line = out_line[:67] + '...'
            
        #await new_message.edit(content = '```' + out_line + '```')
        message =(f'Closing Server - **{SERVER_NAME}**', f'```{out_line}```', ORANGE)
        await new_message.edit(embed = em)
        
        time.sleep(0.05)
        out_line = get_std_out_line()
    message =(f'Closing Server - **{SERVER_NAME}**', f'```Server Closed```', RED)
    await new_message.edit(embed = em)

async def status(Message_Manager):
    out = check_running()
    if out:
       return ('Status' , f"```Server Name: **{SERVER_NAME}**\nPlayer Count: {PLAYER_NUM}```")
    else:
       return ('Status' , "```No server is currently running```")

async def _rename(Message_Manager, index = '', name = ''):
    if index == '':
        await list_games(Message_Manager)
    elif name == '':
        return ('Error', 'ERROR: invalid command')
    else:
        test, text = rename_game([index, name])
        if test:
           return ('Success!', text)
        else:
            return ('Error', text)

async def _command(Message_Manager, *, msg=''):
    if not check_running():
        return ('Error', 'ERROR: no server detected')
    else:
        command = msg
        print(command)
        if command[0] != '/':
            command = '/' + command +'\n'
        try:
            holding_input_pt()
            PROCESS.stdin.write(command.encode())
            PROCESS.stdin.flush()
            today = date.today()
            day_time = today.strftime("%H:%M:%S")
            log = f'[day_time] [{Message_Manager.author.name}:{Message_Manager.author.id}, command]: {command}'
            #write_to_log_file(log)
            output = returning_input()
            return ('Command',f'```{output}```')
        except Exception as e:
            print(e)

async def _log(Message_Manager, date=''):
    global LOG_PT, TIMER_ON
    if date == '':
        if not check_running():
            await Message_Manager.send(embed = embed('Error', 'ERROR: no server detected', RED))
            return 
        TIMER_ON = True
        message = await Message_Manager.send(embed = embed('Log', '```Loading...```', TEAL))
        stdin_reader = threading.Thread(target=start_timer, args=[30])
        stdin_reader.start()
        current_pt = -1
        text = ''
        while TIMER_ON:
            if current_pt != LOG_PT:
                current_pt = (LOG_PT - 20) % GAME_LOG_LENGTH
                text = ''
                while current_pt != LOG_PT:
                    text += LOG[current_pt]
                    current_pt = (current_pt + 1) % GAME_LOG_LENGTH
                await message.edit(embed = embed('Log', f'```{text}```', TEAL))
            time.sleep(3)
            await message.edit(embed = embed('Log', f'```{text}```'))
    elif date.isnumeric():
        if int(date) < 7200:
            await Message_Manager.send(embed = embed('Error', 'ERROR: Timer set is too long', RED))
            return
        if not check_running():
            await Message_Manager.send(embed = embed('Error', 'ERROR: no server detected', RED))
            return
        TIMER_ON = True
        message = await Message_Manager.send(embed = embed('Log', '```Loading...```', TEAL))
        stdin_reader = threading.Thread(target=start_timer, args=[int(date)])
        stdin_reader.start()
        current_pt = -1
        text = ''
        while TIMER_ON:
            if current_pt != LOG_PT:
                current_pt = (LOG_PT - 20) % GAME_LOG_LENGTH
                text = ''
                while current_pt != LOG_PT:
                    text += LOG[current_pt]
                    current_pt = (current_pt + 1) % GAME_LOG_LENGTH
                await message.edit(embed = embed('Log', f'```{text}```', TEAL))
            time.sleep(3)
        await message.edit(embed = embed('Log', f'```{text}```'))
    elif date.count('-') == 2 or date.count('/') == 2:
        div = '/'
        if date.count('-') == 2:
            div = '-'
        cal = date.split(div)
        if len(cal) == 3:
            if len(cal[0]) == 1:
                cal[0] = '0'+cal[0]
            if len(cal[1]) == 1:
                cal[1] = '0'+cal[1]
            if len(cal[2]) == 2:
                cal[2] = '20'+cal[2]
            file_date = '-'.join(cal) + '.txt'
            file_name = f'Log/{file_date}'
            print('finding: ' + file_name)
            if os.path.exists(file_name):
                await Message_Manager.send(embed = embed('Opening Log - ' + file_date, '', BLUE),file=discord.File(file_name))
            else:
                await Message_Manager.send(embed = embed('Error', f'ERROR: did not find file for {date}', RED))
        else:
            await Message_Manager.send(embed = embed('Error', f'ERROR: did not find file for {date}', RED))
    else:
        await Message_Manager.send(embed = embed('Error', f'ERROR: invalid command', RED))

async def _temp(Message_Manager):
    return ('Temperature :',get_cpu_temp())

async def ip(Message_Manager):
    return ("IP Address: ",str(urllib.request.urlopen('https://ident.me').read().decode('utf8')))
           
async def list_games():
    txt = "```"
    count = 0
    for i,f in enumerate(os.listdir(MC_FILE_LOCATION)):
        txt += f'{i+1}: {f}\n'
        count = i
    txt += '```'
    return ('Choose Server:', txt)
    
def get_cpu_temp():
    temp = psutil.sensors_temperatures(fahrenheit=True)
    return f'C: {str(temp)}'

def get_std_out_line():
    index = LOG_PT - 1
    while LOG[index] == '':
        index = (index - 1) % GAME_LOG_LENGTH
    return LOG[LOG_PT - 1]

def check_running():
    return PROCESS is not None and PROCESS.poll() is None 

def get_title(index):
    found = False
    title = ''
    for i,f in enumerate(os.listdir(MC_FILE_LOCATION)):
        if f == index:
            found = True
            title = index
            break
        elif index.isnumeric() and int(index) == i + 1:
            found = True
            title = f
            break
    return found, title

def rename_game(file_input):
    global SERVER_NAME
    new_name = ' '.join(file_input[1:])
    index = file_input[0]
    found, title = get_title(index)
    if found:
        if not check_running() or SERVER_NAME != title:
            os.rename(MC_FILE_LOCATION + '\\' + title, MC_FILE_LOCATION + '\\' + new_name)
            return True, f'Successfully changed **{title}** to **{new_name}**'
        else:
            return False, 'ERROR: server is curently running'
    return False, f'ERROR: did not find "{index}"'
    
def set_game(index):
    global PROCESS, SERVER_NAME, START_UP
    found, title = get_title(index)
    if found:
        file_location = MC_FILE_LOCATION + '/' + title
        if 'run.bat' in os.listdir(file_location):
            PROCESS = subprocess.Popen(file_location + '/run.bat',cwd=file_location , stdout = subprocess.PIPE, stdin = subprocess.PIPE)
        else:
            PROCESS = subprocess.Popen(['java', '-jar', file_location + '/server.jar'],cwd=file_location , stdout = subprocess.PIPE, stdin = subprocess.PIPE)
        SERVER_NAME = title
        START_UP = False
        stdin_reader = threading.Thread(target=thread_running)
        stdin_reader.start()
        return True, title
    return False, ''

def holding_input_pt():
    global HOLD_PT, LOG_PT
    HOLD_PT = LOG_PT

def returning_input():
    global LOG_PT
    first_pt = HOLD_PT
    current_pt = LOG_PT
    tries = 0
    text = ''
    while tries < 3:
        if LOG_PT != current_pt:
            current_pt = LOG_PT
            tries = 0
        else:
            tries +=1
        time.sleep(0.1)
    while first_pt != current_pt:
        text += LOG[first_pt] + '\n'
        first_pt = (first_pt +1) % GAME_LOG_LENGTH
    if text == '':
        text = '_'
    if len(text) > 1993:
        text = text[:1990] + '...'
    return text
    
def thread_running():
    global PROCESS, GAME_LOG_LENGTH, LOG, LOG_PT, PLAYER_NUM, START_UP
    while check_running():
        
        realtime_output = PROCESS.stdout.readline()
        if realtime_output:
            txt = str(realtime_output).replace('\\n','').replace('\\r','')
            if "b'" in txt:
                txt = txt[2:]
            if txt[-1] == "'":
                txt = txt[:-1]
            
            '''if START_UP:
                write_to_log_file(txt + '\n')
            if 'Stopping server' in txt:
                START_UP = False'''
       
            LOG[LOG_PT] = txt
            if '<' not in LOG[LOG_PT] and 'joined the game' in LOG[LOG_PT]:
                PLAYER_NUM += 1
            elif '<' not in LOG[LOG_PT] and 'lost connection: Disconnected' in LOG[LOG_PT]:
                PLAYER_NUM -= 1
            #print(realtime_output)
            LOG_PT = (LOG_PT + 1) % GAME_LOG_LENGTH
            sys.stdout.flush()
            time.sleep(0.1)
        else:
            time.sleep(1)
    PLAYER_NUM = 0

def write_to_log_file(txt):
    today = date.today()
    day = today.strftime("%m-%d-%Y")
    file_loc = 'Log/' + day + '.txt'
    if os.path.exists(file_loc):
        with open(file_loc, 'a') as file:
            file.write(txt)
    else:
        with open(file_loc, 'w') as file:
            file.write(txt)
    
def read_settings(index, context = None):
    global PROCESS, SERVER_NAME
    found, title = get_title(index)
    if found:
        filename = MC_FILE_LOCATION + '/' + title
        if os.path.isfile(filename + '/server.properties'):
            filename += '/server.properties'
        elif os.path.isfile(filename + '/server.txt'):
            filename += '/server.txt'
        else:
            return f'Error: cannot find settings in **{title}** '

        text = ''
        if context:
            return write_settings(title, filename, context)
        else:
            with open(filename,'r') as file_read:
                text += '```'
                counter = 1;
                for line in file_read.readlines():
                    if '=' in line:
                        text += f'{counter}:{line}'
                        counter += 1
                    else :
                        text += line
                text += '```'
        return text
    return f'Error: did not find folder'

def write_settings(title, filename, context):
    text = ''
    comments = ''
    SETTINGS = {}
    with open(filename,'r') as file_read:
        for line in file_read.readlines():
            if line[0] == '#':
                comments += line
                continue
            name = ''
            val = ''
            if line[-1] == '=':
                name = line[:-1]
            else:
                try:
                    name, val = line.split('=')
                except:
                    i = line.find('=')
                    name = line[:i]
                    val = line[i+1:]
                val = val.replace('\r','').replace('\n','')
            SETTINGS[name] = val
    
    name = context[0]
    if name.isnumeric():
        name = list(SETTINGS.keys())[int(name)-1]
    prev_val = SETTINGS[name]
    SETTINGS[name] = context[1]
    for key in SETTINGS.keys():
        text += f'{key}={SETTINGS[key]}\n'
    with open(filename,'w') as file_write:
        file_write.write(comments + text[:-1])
    if prev_val == '':
        prev_val = '___'
    if SETTINGS[name] == '':
        SETTINGS[name] = '___'
    return f'Sucessfully changed **{name}** from **{prev_val}** to **{SETTINGS[name]}** in **{title}**'

def get_readme():
    readme_file = open(README)
    text = ''.join(readme_file.readlines())
    return '```' + text + '```'

def start_timer(length):
    global TIMER_ON
    try:
        if TIMER_ON:
            time.sleep(length)
    finally:
        TIMER_ON = False

# ========================================
# Receiver code
# ========================================

# Define the handler to process incoming requests
class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print(f"Received: {post_data.decode('utf-8')}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Data received successfully")

# Set up the server
server_address = ('localhost', 4443)
httpd = http.server.HTTPServer(server_address, SimpleHTTPRequestHandler)

# Wrap the socket with SSL
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print("Serving HTTPS on localhost:4443...")
httpd.serve_forever()