from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread

LIST = []
PASSWORD = str()

def search(conn : socket, addr : tuple):
    global LIST
    try:
        while True:
            inp = conn.recv(1024).decode()
            if inp == '/':
                for _ in LIST:
                    if _[0] == adrr[0]:
                        LIST.remove(_)
                break
            result = str()
            for i in LIST:
                if inp in i[1]:
                    result += i[0] + '>>' +i[1] + ':'
            if not result:
                result = 'nothing found'
            conn.send(result.encode())
        conn.close()
    except:
        conn.close()

def main():
    PASSWORD = input('set password for server >>')
    s = socket(AF_INET, SOCK_STREAM)
    s.bind(('', 6985))
    s.listen(50)
    print('server started...')
    while True:
        try:
            conn, addr = s.accept()
            print(addr)
            checkpass = conn.recv(1024).decode()
            if checkpass != PASSWORD:
                conn.send(b'0')
                conn.close()
                continue
            conn.send(b'1')
            client_list = conn.recv(1024).decode().split(':')
            for i in client_list:
                if (addr[0],i) not in LIST:
                    LIST.append((addr[0],i))
            Thread(target=search, args=(conn, addr)).start()
        except :
            conn.close()

if __name__ == '__main__':
    main()