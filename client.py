from socket import socket, AF_INET, SOCK_STREAM
from os import getcwd, walk, path, remove
from cryptography.fernet import Fernet
from random import randint, choice
from string import ascii_letters
from threading import Thread
from zipfile import ZipFile
from time import sleep

PACKET_SIZE = 102400
SHARED = {}
PRIVATE_KEY = ['2','f','t','n','g','F','u','Z','T','8','9','a','C','7','h','0','y','K','d','B','c','6','w','k','H','P','m','A','v','j','r','z','x','R','3','e','Q','Y','q','S','M','D','o','5','V','s','L','X','O','G','E','W','U','1','l','J','4','I','N','p','b','i']
PUBLIC_KEY = ''
KEY = ''
for _ in range(43):
    rand = randint(0, len(PRIVATE_KEY)-1)
    PUBLIC_KEY += str(rand) + choice(ascii_letters)
    KEY += PRIVATE_KEY[rand]
KEY += '='

def encrypt(data : bytes, key : str):
    return Fernet(key.encode()).encrypt(data)

def decrypt(cypher : bytes, key : str):
    try:
        return Fernet(key.encode()).decrypt(cypher)
    except:
        return b''

def search(s : socket):
    try:
        while True:
            inp = input('Search (Enter "/" to stop searching)>>')
            if inp == '/':
                break
            s.send(inp.encode())
            ans = s.recv(1024).decode().split(':')
            if ans:
                for i in ans:
                    print(i+'\n')
    except:
        raise

def download():
    global PACKET_SIZE, PRIVATE_KEY
    try:
        while True:
            s = socket(AF_INET, SOCK_STREAM)
            ip = input('Client IP (Enter "/" to stop downloading)>>')
            if ip == '/':
                break
            s.connect((ip, 6986))
            pub_key = s.recv(1024).decode()
            i, j = 0, 0
            list = []
            while i<len(pub_key):
                if pub_key[i] in ascii_letters:
                    list.append(int(pub_key[j:i]))
                    j = i + 1
                i += 1
            key = ''
            for l in list:
                key += PRIVATE_KEY[l]
            key += '='
            inp = input('enter file name (Enter "/" to stop downloading)>>')
            if inp == '/':
                break
            s.send(inp.encode())
            isd = s.recv(1024).decode()
            data = decrypt(s.recv(PACKET_SIZE), key)
            while data:
                file = open('downloaded-'+inp, 'ab')
                file.write(data)
                file.close()
                data = decrypt(s.recv(PACKET_SIZE), key)
            if isd == '1':
                zip_ = ZipFile('downloaded-'+inp, 'r')
                zip_.extractall()
                zip_.close()
    except:
        raise

def upload():
    global PUBLIC_KEY, SHARED
    up = socket(AF_INET, SOCK_STREAM)
    up.bind(('', 6986))
    up.listen(10)
    while True:
        try:
            conn, addr = up.accept()
            conn.send(PUBLIC_KEY.encode())
            name = conn.recv(1024).decode()
            if path.isfile(SHARED[name]):
                conn.send(b'2')
                file = open(SHARED[name], 'rb')
                data = file.read(PACKET_SIZE)
                while data:
                    conn.send(encrypt(data, KEY))
                    data = file.read(PACKET_SIZE)
                file.close()  
            else :
                conn.send(b'1')
                zfile = ZipFile(str(addr[1])+name+'.zip', 'w')
                for root, dirs, files in walk(SHARED[name]):
                    root = root.replace(getcwd()+'\\', '')
                    zfile.write(root)
                    for f in files:
                        zfile.write(path.join(root, f))
                zfile.close()
                file_ = open(str(addr[1])+name+'.zip', 'rb')
                data = file_.read(PACKET_SIZE)
                while data:
                    conn.send(encrypt(data, KEY))
                    data = file_.read(PACKET_SIZE)
                file_.close()
                remove(str(addr[1])+name+'.zip')
            conn.close()
        except:
            raise

def exit_(s : socket):
    s.send(b'/')
    s.close()
    exit()

def main():
    global PRIVATE_KEY, SHARED
    Thread(target=upload).start()
    while True:
        try:
            s = socket(AF_INET, SOCK_STREAM)
            s.connect((input('Server IP >>'), 6985))
            password = input('enter server password>>')
            s.send(password.encode())
            if not int(s.recv(1024).decode()):
                print('wrong password')
                s.close()
                continue
            list = str()
            for root, dirs, files in walk(getcwd()):
                for d in dirs:
                    SHARED[d] = root+'\\'+d
                    list += d+':'
                for f in files:
                    if not root.replace(getcwd(), '') :
                        SHARED[f] = f
                    list += f+':'
            s.send(list.encode())
            break
        except:
            print('something went wrong...')
            continue
    while True:
        print('\n [1] Search\n [2] Download\n [3] Exit')
        menu = input('\nEnter Number >>')
        if menu == '1':
            search(s) 
        elif menu == '2':
            download()
        elif menu == '3':
            exit_(s)
        else:
            print('Wrong Input')

if __name__ == '__main__':
    main()