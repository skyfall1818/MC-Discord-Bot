import discord # need pipinstall
import os
import os.path
import sys
import subprocess # need pip install i think
import threading
import time
import math
from datetime import date
#from requests import get
import psutil #need pip install
from discord.ext import commands

GREEN = 0x1BCA00
RED = 0xD74625
ORANGE = 0xE59315
YELLOW = 0xF9F905
TEAL = 0x19EADB
BLUE = 0x1946E0


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

#bot = discord.Client()
bot = commands.Bot(command_prefix=KEYWORD)


def embed(header, context, RGB=GREEN):
    embed=discord.Embed(title=header, description=context,color=RGB)
    return embed

@bot.event
@commands.has_role(ADMIN_TAG)
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
    
@bot.command(aliases=['r', 'run'])
@commands.has_role(ADMIN_TAG)
async def _run(ctx, index = ''):
    if index == '':
        await list_games(ctx)
    else:
        out, title= set_game(index)
        if out:

            em = embed(f'Starting Server - **{title}**', f'```Loading...```', ORANGE)
            new_message = await ctx.send(embed = em)
            
            out_line = get_std_out_line()
            while check_running() and '%' not in out_line:
                if ']: ' in out_line:
                    out_line = out_line.split(']: ')[1]
                if len(out_line) > 70:
                    out_line = out_line[:67] + '...'

                em = embed(f'Starting Server - **{title}**', f'```{out_line}```', ORANGE)
                await new_message.edit(embed = em)
                
                time.sleep(0.1)
                out_line = get_std_out_line()
            while check_running() and '%' in out_line:
                if ']: ' in out_line:
                    out_line = out_line.split(']: ')[1]
                if len(out_line) > 70:
                    out_line = out_line[:67] + '...'

                em = embed(f'Starting Server - **{title}**', f'```{out_line}```', ORANGE)
                await new_message.edit(embed = em)
                
                time.sleep(0.05)
                out_line = get_std_out_line()
            if check_running():
                START_UP = True
                em = embed(f'Starting Server - **{title}**', f'```Done!```')
                await new_message.edit(embed = em)
            else:
                await ctx.send(embed = embed('Error', 'ERROR: server crashed on startup. check your settings', RED))
        else:
            await ctx.send(embed = embed('Error', 'ERROR: did not find folder', RED))


@bot.command(aliases=['s', 'stop'])
@commands.has_role(ADMIN_TAG)
async def _stop(ctx):
    global PROCESS
    PROCESS.stdin.write('stop\n'.encode())
    PROCESS.stdin.flush()
    out_line = get_std_out_line()
    em = embed(f'Closing Server - **{SERVER_NAME}**', f'```Loading...```', ORANGE)
    new_message = await ctx.send(embed = em)
    while check_running():
        if ']: ' in out_line:
            out_line = out_line.split(']: ')[1]
        if len(out_line) > 70:
            out_line = out_line[:67] + '...'
            
        #await new_message.edit(content = '```' + out_line + '```')
        em = embed(f'Closing Server - **{SERVER_NAME}**', f'```{out_line}```', ORANGE)
        await new_message.edit(embed = em)
        
        time.sleep(0.05)
        out_line = get_std_out_line()
    em = embed(f'Closing Server - **{SERVER_NAME}**', f'```Server Closed```', RED)
    await new_message.edit(embed = em)

@bot.command()
async def status(ctx):
    out = check_running()
    if out:
        await ctx.send(embed = embed ('Status' , f"```Server Name: **{SERVER_NAME}**\nPlayer Count: {PLAYER_NUM}```", YELLOW))
    else:
        await ctx.send(embed = embed ('Status' , "```No server is running```", YELLOW))

#rename file
@bot.command(aliases=['re', 'rename'])
@commands.has_role(ADMIN_TAG)
async def _rename(ctx, index = '', name = ''):
    if index == '':
        await list_games(ctx)
    elif name == '':
        await ctx.send(embed = embed('Error', 'ERROR: invalid command', RED))
    else:
        test, text = rename_game([index, name])
        if test:
            await ctx.send(embed = embed('Success!', text))
        else:
            await ctx.send(embed = embed('Error', text, RED))

@bot.command(aliases=['c', 'command'])
@commands.has_role(ADMIN_TAG)
async def _command(ctx, *, msg=''):
    if not check_running():
        await ctx.send(embed = embed('Error', 'ERROR: no server detected', RED))
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
            log = f'[day_time] [{ctx.author.name}:{ctx.author.id}, command]: {command}'
            #write_to_log_file(log)
            messaging = await ctx.send(embed = embed('Command',f"```...```", ORANGE))
            output = returning_input()
            await messaging.edit(embed = embed('Command',f'```{output}```'))
        except Exception as e:
            print(e)

@bot.command(aliases=['set', 'setting', 'settings'])
@commands.has_role(ADMIN_TAG)
async def _setting(ctx, index = '', line = '', txt = ''):
    global bot
    if index == '':
        await list_games(ctx)
    elif line == '':
        found, title = get_title(index)
        if found:
            await create_list(ctx, f'Settings - {title}', read_settings(index))
        else:
            await ctx.send(embed = embed('ERROR', read_settings(index)))
    elif txt == '':
        await ctx.send(embed = embed('ERROR', read_settings(index, [line,''])))
    else:
        await ctx.send(embed = embed('ERROR', read_settings(index, [line, txt])))

@bot.command(aliases=['l', 'log'])
@commands.has_role(ADMIN_TAG)
async def _log(ctx, date=''):
    global LOG_PT, TIMER_ON
    if date == '':
        if not check_running():
            await ctx.send(embed = embed('Error', 'ERROR: no server detected', RED))
            return 
        TIMER_ON = True
        message = await ctx.send(embed = embed('Log', '```Loading...```', TEAL))
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
    if date.isnumeric():
        if int(date) < 7200:
            await ctx.send(embed = embed('Error', 'ERROR: Timer set is too long', RED))
            return
        if not check_running():
            await ctx.send(embed = embed('Error', 'ERROR: no server detected', RED))
            return
        TIMER_ON = True
        message = await ctx.send(embed = embed('Log', '```Loading...```', TEAL))
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
                await ctx.send(embed = embed('Opening Log - ' + file_date, '', BLUE),file=discord.File(file_name))
            else:
                await ctx.send(embed = embed('Error', f'ERROR: did not find file for {date}', RED))
        else:
            await ctx.send(embed = embed('Error', f'ERROR: did not find file for {date}', RED))
    else:
        await ctx.send(embed = embed('Error', f'ERROR: invalid command', RED))

@bot.command(aliases=['t', 'temp', 'temperature'])
@commands.has_role(ADMIN_TAG)
async def _temp(ctx):
    await ctx.send(embed = embed('Temp:',get_cpu_temp(), BLUE))

@bot.command()
@commands.has_role(ADMIN_TAG)
async def ip(ctx):
    ip = get('https://api.ipify.org').text
    await ctx.send('```Server IP: '+ip + '```')
             
async def create_list(ctx, title, full_txt, space = 20.0):
    text = full_txt.replace('```','').split('\n')
    pages = []
    size = math.ceil(len(text)/space)
    
    for count in range(size):
        end_range = (count+1)*20
        if end_range > len(text):
            end_range = len(text)
        pages.append(discord.Embed (
            title = title,
            description = '```' + '\n'.join(text[count*20:end_range]) + '```' + f'\n Page: {count+1}/{size}',
            colour = 0xAEAEAE
        ))
    message = await ctx.send(embed = pages[0])
    await message.add_reaction(emoji = '⏮')
    await message.add_reaction(emoji = '◀')
    await message.add_reaction(emoji = '▶')
    await message.add_reaction(emoji = '⏭')
    i = 0
    emoji = ''
    while True:
        if emoji == '⏮':
            i = 0
            await message.edit(embed = pages[i])
        elif emoji == '◀':
            if i > 0:
                i -= 1
                await message.edit(embed = pages[i])
        elif emoji == '▶':
            if i < 2:
                i += 1
                await message.edit(embed = pages[i])
        elif emoji == '⏭':
            i = size-1
            await message.edit(embed=pages[i])
        try:
            res = await bot.wait_for('reaction_add', timeout = 30.0)
        except:
            break
        if res == None:
            break
        if bot.user.name not in str(res[1]):  #Example: 'MyBot#1111'
            emoji = str(res[0].emoji)
            await message.remove_reaction(res[0].emoji, res[1])
    await message.clear_reactions()
           
async def list_games(ctx):
    txt = "```"
    count = 0
    for i,f in enumerate(os.listdir(MC_FILE_LOCATION)):
        txt += f'{i+1}: {f}\n'
        count = i
    txt += '```'
    if count > 20:
        await create_list(ctx, 'Choose Server', txt)
    else:
        em = embed('Choose Server:',txt,0xAEAEAE)
        await ctx.send(embed = em)
    
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
        file_location = MC_FILE_LOCATION + '\\' + title
        PROCESS = subprocess.Popen(['java', '-jar', file_location + '\\server.jar'],cwd=file_location , stdout = subprocess.PIPE, stdin = subprocess.PIPE)
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

bot.run(TOKEN)
