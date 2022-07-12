import sys
import requests

def main():
    if len(sys.arg) > 1 and sys.arg[1] == 'rerun':
        x = requests.get('https://raw.githubusercontent.com/skyfall1818/MC-Discord-Bot/main/FITSSFF%20MC%20discord%20bot/README.txt')
    else:
        print(x.text)
        

if __name__ == "__main__":
    main()
