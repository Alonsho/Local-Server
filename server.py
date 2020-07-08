import socket
import sys
import os

# create a listening socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = '0.0.0.0'
server_port = int(sys.argv[1])
try:
    server.bind((server_ip, server_port))
except OverflowError:
    print 'bad argument given for server socket'
    exit(1)
server.listen(5)
client_socket, client_address = server.accept()
is_connected = True
client_socket.settimeout(1.0)
while True:
    # because of not using threads, only one client will be connected at a time, and a client may have more
    # than one request
    if not is_connected:
        client_socket, client_address = server.accept()
        is_connected = True
        client_socket.settimeout(1.0)
    try:
        data = client_socket.recv(1024)
        # close connection if client sends empty package (happens with Google Chrome)
        if not data:
            client_socket.close()
            is_connected = False
            print 'empty request'
            continue
        # read all the request
        while not data.endswith('\r\n\r\n'):
            data += client_socket.recv(1024)
    # close connection if timeout occurs
    except socket.timeout as e:
        client_socket.close()
        is_connected = False
        print e
        continue
    print data
    lines = data.split('\n')
    # get the name of the requested file
    file_name = 'files' + lines[0][4:-10]
    # redirect if needed
    if file_name == 'files/':
        file_name = 'files/index.html'
    if file_name == 'files/redirect':
        message = 'HTTP/1.1 301 Moved Permanently\r\n' + 'Connection: close\r\n' + 'Location: /result.html\r\n\r\n'
        client_socket.send(message)
        client_socket.close()
        is_connected = False
        continue
    # try to open the requested file depending on its extension (binary read or text)
    # if file was not found or an error occurred while accessing it, sent a 404 error
    if file_name.endswith('ico') or file_name.endswith('jpg'):
        try:
            fileToSend = open(file_name, 'rb')
        except IOError:
            message = 'HTTP/1.1 404 Not Found\r\n' + 'Connection: close\r\n\r\n'
            client_socket.send(message)
            client_socket.close()
            is_connected = False
            continue
    else:
        try:
            fileToSend = open(file_name, 'r')
        except IOError:
            message = 'HTTP/1.1 404 Not Found\r\n' + 'Connection: close\r\n\r\n'
            client_socket.send(message)
            client_socket.close()
            is_connected = False
            continue
    conn_line = ''
    # find connection type requested by the client
    for line in lines:
        if line.startswith('Connection'):
            conn_line = line
            break
    if conn_line == '':
        print 'bad request given by client'
        client_socket.close()
        is_connected = False
        continue
    conn_type = conn_line[12:-1]
    # send the headers followed by the requested file data
    try:
        message = fileToSend.read()
        file_size = len(message)
        message = 'HTTP/1.1 200 OK\r\n' + 'Connection: ' + conn_type + '\r\n' + 'Content-Length: '\
                  + str(file_size) + '\r\n\r\n' + message + '\r\n\r\n'
        client_socket.send(message)
    except IOError:
        print 'error reading the file'
    except socket.error:
        print 'error sending the file'
    # close the connection if the connection type is 'close'
    fileToSend.close()
    if conn_type == 'close':
        client_socket.close()
        is_connected = False
