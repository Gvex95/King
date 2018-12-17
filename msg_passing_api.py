import sys
from multiprocessing import Process, Queue
from multiprocessing.connection import Client, Listener
from array import array
from datetime import datetime

def server_fun(local_port, queue):
    # Set the address of the local node's server
    local_server_address = ('localhost', local_port)

    # Send fixed message
    with Listener(local_server_address, authkey=b'Lets work together') as listener:

        while True:
            with listener.accept() as conn:
                #print('connection accepted from', listener.last_accepted)
                msg = conn.recv()
                #print('Recived msg in listner: ', msg)

                # Forward msg to local node's process
                queue.put(msg)

                # Exit if msg is 'exit'
                if msg == 'exit':
                    break
	

def sendMsg(remote_server_address, msg):
        with Client(remote_server_address, authkey=b'Lets work together') as conn:
            #print(' Sending message to remote_server_addresses: ', remote_server_address, " message is: ", msg)
            conn.send(msg)
            i = datetime.now()
            print (str(i))

def rcvMsg(queue):
    return queue.get()

def broadcastMsg(list_of_remote_server_address, msg):
    for remote_server_address in list_of_remote_server_address:
        sendMsg(remote_server_address, msg)

def rcvMsgs(queue, no_of_messages_to_receive):
    msgs = []

    for i in range(no_of_messages_to_receive):
        msgs.append( rcvMsg(queue) )

    return msgs
