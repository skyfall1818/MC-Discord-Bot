import os
import os.path
import sys
import subprocess
import threading
import time
import math
import asyncio
from Message_Queuing import Message_Queue
from datetime import date
#from requests import get
#import psutil #need pip install
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
GAME_LOG_LENGTH = 200
START_UP_TIMEOUT = 30
LOG = ['' for _ in range(GAME_LOG_LENGTH)]
LOG_PT = 0

HOLD_PT = 0

PLAYER_NUM = 0

START_UP = False

TIMER_ON = False

with open(KEY_FILE, "r") as file:
    for line in file:
        try:
            name, val = line.split('|')
            if val != '' and val != ' ':
                if name == 'Game File':
                    MC_FILE_LOCATION = val.replace('\n','')
                    print(f"setting MC File location to {MC_FILE_LOCATION}")
        except:
            print("Error: cannot split line")

##################
# API functions
##################

def help(Message_Manager):
    text=''
    with open(README, 'r') as f:
        text = f.read()
    Message_Manager.Enqueue('Help',text)

def run(Message_Manager, index = ''):
    global START_UP_TIMEOUT, START_UP
    if index == '':
        list_games(Message_Manager)
    else:
        out, title= set_game(index)
        if out:
            print(f'Starting Server - {title}')
            Message_Manager.Enqueue(f'Starting Server - {title}', f'Loading...')
            start_time = time.time()
            out_line = get_std_out_line()
            while check_running() and '%' not in out_line and time.time() - start_time < START_UP_TIMEOUT:
                if ']: ' in out_line:
                    out_line = out_line.split(']: ')[1]
                if len(out_line) > 70:
                    out_line = out_line[:67] + '...'

                Message_Manager.Enqueue(f'Starting Server - {title}', f'{out_line}')
                
                time.sleep(0.1)
                out_line = get_std_out_line()

            while check_running() and '%' in out_line and time.time() - start_time < START_UP_TIMEOUT:
                if ']: ' in out_line:
                    out_line = out_line.split(']: ')[1]
                if len(out_line) > 70:
                    out_line = out_line[:67] + '...'

                Message_Manager.Enqueue(f'Starting Server - {title}', f'{out_line}')
                
                time.sleep(0.05)
                out_line = get_std_out_line()
            if check_running():
                print("Done!")
                START_UP = True
                Message_Manager.Enqueue(f'Starting Server - {title}', f'Done!')
            else:
                Message_Manager.Enqueue(f'Starting Server - {title} Error', 'ERROR: server crashed on startup. check your settings')
        else:
            print(f'ERROR: did not find folder')
            Message_Manager.Enqueue('Error', 'ERROR: did not find folder')

def stop(Message_Manager):
    global PROCESS, SERVER_NAME
    PROCESS.stdin.write('stop\n'.encode())
    PROCESS.stdin.flush()
    out_line = get_std_out_line()
    print(SERVER_NAME)
    Message_Manager.Enqueue(f'Closing Server - {SERVER_NAME}', 'Closing Server - {SERVER_NAME}...')
    while check_running():
        if ']: ' in out_line:
            out_line = out_line.split(']: ')[1]
        if len(out_line) > 70:
            out_line = out_line[:67] + '...'
            
        Message_Manager.Enqueue(f'Closing Server - {SERVER_NAME}', f'{out_line}')
        
        time.sleep(0.05)
        out_line = get_std_out_line()
    Message_Manager.Enqueue(f'Closing Server - {SERVER_NAME}', f'Server Closed')

def status(Message_Manager):
    out = check_running()
    if out:
       Message_Manager.Enqueue('Status' , f"Server Name: {SERVER_NAME}\nPlayer Count: {PLAYER_NUM}")
    else:
       Message_Manager.Enqueue('Status' , "No server is currently running")

def rename(Message_Manager, index = '', name = ''):
    if index == '':
        list_games(Message_Manager)
    elif name == '':
        return ('Error', 'ERROR: invalid command')
    else:
        test, text = rename_game([index, name])
        if test:
           return ('Success!', text)
        else:
            return ('Error', text)

def command(Message_Manager, msg=''):
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
            return ('Command',f'{output}')
        except Exception as e:
            print(e)

def log(Message_Manager, date=''):
    global LOG_PT, TIMER_ON
    if date == '':
        if not check_running():
            Message_Manager.Enqueue('Error', 'ERROR: no server detected')
            return 
        TIMER_ON = True
        Message_Manager.Enqueue('Log', 'Loading...')
        stdin_reader = threading.Thread(target=start_timer, args=[30])
        stdin_reader.start()
        current_pt = (LOG_PT - 20) % GAME_LOG_LENGTH
        while TIMER_ON:
            while current_pt != LOG_PT:
                text = LOG[current_pt] + '\n'
                Message_Manager.Enqueue('Log', f'{text}')
                current_pt = (current_pt + 1) % GAME_LOG_LENGTH
            time.sleep(3)
    elif date.isnumeric():
        if int(date) < 7200:
            Message_Manager.Enqueue('Error', 'ERROR: Timer set is too long')
            return
        if not check_running():
            Message_Manager.Enqueue('Error', 'ERROR: no server detected')
            return
        TIMER_ON = True
        Message_Manager.Enqueue('Log', 'Loading...')
        stdin_reader = threading.Thread(target=start_timer, args=[int(date)])
        stdin_reader.start()
        current_pt = (LOG_PT - 20) % GAME_LOG_LENGTH
        while TIMER_ON:
            while current_pt != LOG_PT:
                text = LOG[current_pt] + '\n'
                Message_Manager.Enqueue('Log', f'{text}')
                current_pt = (current_pt + 1) % GAME_LOG_LENGTH
            time.sleep(3)
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
                Message_Manager.Enqueue('Opening Log - ' + file_date, '')
            else:
                Message_Manager.Enqueue('Error', f'ERROR: did not find file for {date}')
        else:
            Message_Manager.Enqueue('Error', f'ERROR: did not find file for {date}')
    else:
        Message_Manager.Enqueue('Error', f'ERROR: invalid command')

def ip(Message_Manager):
    return ("IP Address: ",str(urllib.request.urlopen('https://ident.me').read().decode('utf8')))

##################
# helper functions
##################

def list_games(Message_Manager):
    txt = ""
    count = 0
    for i,f in enumerate(os.listdir(MC_FILE_LOCATION)):
        txt += f'{i+1}: {f}\n'
        count = i
    txt += ''
    Message_Manager.Enqueue('Server List', txt)

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
            return True, f'Successfully changed {title} to {new_name}'
        else:
            return False, 'ERROR: server is curently running'
    return False, f'ERROR: did not find "{index}"'
    
def set_game(index):
    global PROCESS, SERVER_NAME, START_UP
    found, title = get_title(index)
    if found:
        file_location = MC_FILE_LOCATION + '\\' + title
        file_run = ''
        with open(file_location + '\\runapplication.txt', 'r') as temp:
            file_run = temp.readline()
        if '.jar' in file_run:
            PROCESS = subprocess.Popen(['java', '-jar', file_location + '\\' + file_run],cwd=file_location , stdout = subprocess.PIPE, stdin = subprocess.PIPE)
        elif '.bat' in file_run:
            PROCESS = subprocess.Popen(file_location + '\\' + file_run, cwd=file_location, stdout = subprocess.PIPE, stdin = subprocess.PIPE)
        else:
            return False, ''
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
            return f'Error: cannot find settings in {title} '

        text = ''
        if context:
            return write_settings(title, filename, context)
        else:
            with open(filename,'r') as file_read:
                text += ''
                counter = 1
                for line in file_read.readlines():
                    if '=' in line:
                        text += f'{counter}:{line}'
                        counter += 1
                    else :
                        text += line
                text += ''
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
    return f'Sucessfully changed {name} from {prev_val} to {SETTINGS[name]} in {title}'

def get_readme():
    readme_file = open(README)
    text = ''.join(readme_file.readlines())
    return '' + text + ''

def start_timer(length):
    global TIMER_ON
    try:
        if TIMER_ON:
            time.sleep(length)
    finally:
        TIMER_ON = False

##################
# Message handler
##################
def message_handler(MQ, *args):
    subargs = None
    main = None
    if len(args) > 1:
        main = args[0]
        subargs = args[1:]
    else:
        main = args[0]
    
    MQ.start_sending()
    if main == "help":
        print("running help")
        help(MQ)
    elif main == "run":
        if subargs:
            run(MQ, subargs[0])
        else:
            run(MQ)
    elif main == "stop":
        stop(MQ)
    elif main == "status":
        status(MQ)
    elif main == "command":
        command(MQ, msg = " ".join(subargs))
    elif main == "ip":
        ip(MQ)
    elif main == "log":
        log(MQ)
    else:
        print(f"Error: Unkown command '{main}'")
    MQ.done_sending()
    print('finish handling request')
