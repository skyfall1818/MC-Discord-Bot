from tkinter import *
from tkinter import filedialog
import os

TOKEN_SHOW = False
TOKEN_CODE = ''
FILE_NAME = ''
CHAR_KEY = ''
KEY_FILE = 'ImportantCode.txt'
ADMIN_TAG = ''

with open(KEY_FILE, "r") as file:
    #global TOKEN_CODE, FILE_NAME, CHAR_KEY, ADMIN_TAG
    for line in file:
        try:
            name, val = line.split('|')
            if val != '' and val != ' ':
                if name == 'Token':
                    TOKEN_CODE = val
                elif name == 'MC File':
                    FILE_NAME = val
                elif name == 'Char Key':
                    CHAR_KEY = val
                elif name == 'Admin Tag':
                    ADMIN_TAG = val
        except:
            print("Error: cannot split line")

def file_open():
    path=filedialog.askdirectory()
    file_txt.delete('1.0','end')
    file_txt.insert(INSERT, path)

def show_or_hide_token():
    global TOKEN_SHOW, TOKEN_CODE
    global token_txt, toggle_token_show
    if(TOKEN_SHOW == False and TOKEN_CODE != ''):
        TOKEN_SHOW = True
        token_txt.delete('1.0','end')
        token_txt.insert(INSERT, TOKEN_CODE)
        toggle_token_show['text'] = 'Hide'
    elif(TOKEN_SHOW):
        hide_token()
        
def hide_token():
    global TOKEN_SHOW
    global token_txt
    TOKEN_SHOW = False
    token_txt.delete('1.0','end')
    toggle_token_show['text'] = 'Show'
    if TOKEN_CODE != '':
        token_txt.insert(INSERT, "*"*60)

def save_input():
    global TOKEN_CODE, FILE_NAME, CHAR_KEY, ADMIN_TAG
    global token_txt, file_txt, char_txt
    if token_txt.get('1.0', END) != ('*' * 60) + '\n' :
        TOKEN_CODE = token_txt.get('1.0', END).replace('\n','')
    FILE_NAME = file_txt.get('1.0', END).replace('\n','')
    CHAR_KEY = char_txt.get('1.0', END).replace('\n','')
    ADMIN_TAG = tag_txt.get('1.0', END).replace('\n','')
    hide_token()
    with open(KEY_FILE, "w") as file:
        file.write('Token|' + TOKEN_CODE + '\n'
                   'MC File|' + FILE_NAME + '\n'
                   'Char Key|' + CHAR_KEY+ '\n'
                   'Admin Tag|' + ADMIN_TAG)

def reset_input():
    hide_token()
    file_txt.delete('1.0','end')
    file_txt.insert(INSERT, FILE_NAME)
    char_txt.delete('1.0','end')
    char_txt.insert(INSERT, CHAR_KEY)
    tag_txt.delete('1.0','end')
    tag_txt.insert(INSERT, ADMIN_TAG)
    
window=Tk()
# add widgets here

window.title('FITSSFF MC Discord Bot')
window.geometry("650x250+10+20")

#title
text = Label(text = "FITSSFF Minecrat Settings Bot", font = 50)
text.place(x = 220, y= 20)

#input token
token_lbl = Label(text = "Token", font = 50)
token_lbl.place(x = 30, y= 65)

token_txt = Text(window, height=1, width=75, font=("Consolas", 8))
token_txt.place(x = 90, y = 70)
if TOKEN_CODE != '':
    token_txt.insert(INSERT, "*"*60)

toggle_token_show = Button(window, text="Show", command=show_or_hide_token, font=("Times New Roman", 10))
toggle_token_show.place(x = 560, y = 66)

#MC file location
file_btn = Button(window, text= "Open File Location", command=file_open, font=("Times New Roman", 11))
file_btn.place(x = 30, y = 100)

file_txt = Text(window, height=1, width=55, font=("Arial", 11))
file_txt.place(x=165, y= 105)

#Discord Char manip
char_lbl = Label(text = "Char Key", font = 50)
char_lbl.place(x = 30, y= 140)

char_txt = Text(window, height=1, width=3, font=("Times New Roman", 11))
char_txt.place(x = 105, y= 143)

#admin tag
tag_lbl = Label(text = "Admin Tag", font = 50)
tag_lbl.place(x = 245, y= 140)

tag_txt = Text(window, height=1, width=30, font=("Times New Roman", 11))
tag_txt.place(x = 335, y= 143)

#save button
save_btn = Button(window, text= "Save", command=save_input, font=("Times New Roman", 16))
save_btn.place(x = 170, y = 190)

#reset button
reset_btn = Button(window, text= "Reset", command=reset_input, font=("Times New Roman", 16))
reset_btn.place(x = 300, y = 190)

#run bot button
run_bot_btn =Button(window, text= "Run", command=file_open, font=("Times New Roman", 16))
run_bot_btn.place(x = 430, y = 190)

reset_input()

window.mainloop()
