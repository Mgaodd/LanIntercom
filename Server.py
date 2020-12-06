#region Imports
import socket
import time
import sys
import subprocess
import selectors
import types
import pyttsx3
from tkinter import *
from multiprocessing import Process

#endregion Imports

#region GENERAL CODE
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP
#endregion

#region SERVER CODE
def accept_wrapper(sock,sel):
    conn, addr = sock.accept()  # Should be ready to read
    print("accepted connection from", addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask,sel):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
        else:
            print("closing connection to", data.addr)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            ##PRINTS
            print(data.outb.decode())
            engine = pyttsx3.init()
            engine.say(data.outb.decode())
            engine.runAndWait()

            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]

def startServer():
    host  = get_ip()
    port =  1234
    num_conns = 1000

    sel = selectors.DefaultSelector()
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(False)
    

    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((host, port))
    lsock.listen()
    print("listening on", (host, port))
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj,sel)
                else:
                    service_connection(key, mask,sel)
    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
    finally:
        sel.close()
#endregion

#region CLIENT CODE

def findListofIps():
    result = subprocess.run('arp -a', stdout=subprocess.PIPE)
    string = result.stdout

    split = string.splitlines()
    dynamics = []

    for x in split:
        x = str(x)
        if "dynamic" not in x:
         continue;
    
        cleaned = []
    
        for z in x.split(" "):
            if len(z) > 2:
                cleaned.append(z)
        dynamics.append(cleaned)
    print(dynamics)
    return dynamics

def isOpen(ip, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
                s.connect((ip, int(port)))
                s.shutdown(socket.SHUT_RDWR)
                return True
        except:
                return False
        finally:
                s.close()

def checkHost(ip, port):
        print("Checking: ", ip , ": ", port)
        ipup = False
        for i in range(retry):
                if isOpen(ip, port):
                        ipup = True
                        break
                else:
                        time.sleep(delay)
        return ipup

def findlistofHosts():
    iterdynamics = iter(findListofIps())
    next(iterdynamics)

    # listofhosts = ['192.168.1.164', '192.168.1.223']
    listofhosts = []

    for x in iterdynamics:
        ip = x[0]
        flag = False;
        
        if checkHost(ip, 445):
            flag = True
            print(ip + " is UP")
        elif checkHost(ip, 139):
            flag = True
            print(ip + " is UP")
        elif checkHost(ip, 138):
            flag = True
            print(ip + " is UP")
        elif checkHost(ip, 135):
            flag = True
            print(ip + " is UP")
        if flag:
            listofhosts.append(ip)

retry = 2
delay = 1
timeout = 3
listofhosts = findlistofHosts()

#endregion ClientCode

#region CHAT CODE 
def chatGui():
    window = Tk()

    messages = Text(window)
    messages.pack()

    input_user = StringVar()
    input_field = Entry(window, text=input_user)
    input_field.pack(side=BOTTOM, fill=X)

    def Enter_pressed(event):
        input_get = input_field.get()
        print(input_get)
        messages.insert(INSERT, '%s\n' % input_get)
        
        sendMessage(input_get)
        # label = Label(window, text=input_get)
        input_user.set(' ')
        # label.pack()
        return "break"

    frame = Frame(window)  # , width=300, height=300)
    input_field.bind("<Return>", Enter_pressed)
    frame.pack()

    window.mainloop()



def sendMessage(message):
    if not listofhosts:
        engine = pyttsx3.init()
        engine.say("No Hosts.")
        engine.runAndWait()

        return;
    
    for x in listofhosts:
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((x, 1234))
            sendme = message
            s.sendall(sendme.encode())
            data = s.recv(1024)
            s.close()

#endregion Chat Code

if __name__== '__main__': 
      p1 = Process(target = startServer)
      p1.start()
      p2 = Process(target = chatGui)
      p2.start()
      p1.join()
      p2.join()
      print(listofhosts)



