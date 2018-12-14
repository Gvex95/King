import sys
from multiprocessing import Process, Queue
from msg_passing_api import *
from datetime import datetime

def even_round(k, remote_server_addresses, init_preference, queue, number_of_proc, proc_index, mayor, mult, pref, num_of_fault_process):

    local_mayor = mayor
    king_mayor = -1

    # Find new king and send your mayor to everybody
    if (proc_index == k):
        print('Node: ', proc_index, ' I am king mother fuckers, broadcasting...')

        recivedOKMessagesCounter = 0
        responded_proces = []
        broadcastMsg(remote_server_addresses, pref[proc_index])

        i = datetime.now()
        print (str(i))

        print('I have sent my mayor to all my minions')


        # wait for comfirmation
        msgs = rcvMsgs(queue, number_of_proc - 1)

        recivedOKMessagesCounter = len(msgs)

        if (recivedOKMessagesCounter != num_of_fault_process - 1):
            print('Some process did not send comfirmation message!!!')
        else:
            print('Recived comformation from all..')


    # If you are not king, recive message and determine new mayor for yourself
    else:

        i = datetime.now()
        print (str(i))

        print('Node: ', proc_index, ' waiting for mayor from king...')

        # Recevie message from king
        msg = rcvMsgs(queue, 1)

        print('Recived major from king')
        #Sanity check
        if len(msg) == 1:
            king_mayor = msg[0]
            print('Node: ', proc_index, ' recived mayor: ', local_mayor, ' from king: ', k)

        print('Send confirmation that i recived msg from king')
        sendMsg(remote_server_addresses[k], "OK KRALJU")


        if (mult > (number_of_proc / 2) + num_of_fault_process):
            print('Node: ', proc_index, ' will keep local mayor: ', local_mayor)
            pref[proc_index] = local_mayor

        else:
            print('Node: ', proc_index, ' will take kings mayor: ', king_mayor)
            pref[proc_index] = king_mayor


    print('Round: ', 2*k, 'Node: ', proc_index,  'state: ', 'Pref: ', pref, ' Major: ', mayor, ' Mult: ', mult)
    k = k + 1
    return k, mayor,mult, pref

def odd_round(round, remote_server_addresses, init_preference, queue, number_of_proc, proc_index, mayor, mult, pref):
    counter = 0

    # Send message to peer node's servers
    broadcastMsg(remote_server_addresses, init_preference)

    # Get message from local node's server
    msgs = rcvMsgs(queue, number_of_proc - 1)
    print('Node: ', proc_index, 'messages received:', msgs)

    pref = [None] * 5
    #Saving messages from other nodes to prefs lists
    #Copy recived list
    pref = msgs[:]
    #Insert initial_preference at correct position
    pref.insert(proc_index, init_preference)
    print('Node: ', proc_index, 'prefs list state after reciving messages: ', pref)

    # Calculating mayor
    dictonary = {"Valid": 0, "Invalid":0}
    for i in range(len(pref)):
        if pref[i] == 1:
            dictonary["Valid"] += 1
        else:
            dictonary["Invalid"] += 1

    print('Dictonary: ', dictonary)

    if (dictonary["Valid"] > dictonary["Invalid"]):
        mayor = 1
        mult = dictonary["Valid"]
    else:
        mayor = 0
        mult = dictonary["Invalid"]

    print('Round: ', round, 'Node: ', proc_index,  'state: ', 'Pref: ', pref, ' Major: ', mayor, ' Mult: ', mult)
    dict = {"Mayor":mayor, "Mult":mult, "Pref":pref}
    return dict

def main():
    # Parse command line arguments
    if len(sys.argv) != 5:
        print('Program usage: example_complete_graph proc_index number_of_proc')
        print('Example: If number_of_proc = 3, we must start 3 instances of program in 3 terminals:')
        print('Params: 1: Index of proces, 2: Number of process, 3: Initial prefernces, 4: Num of faulty nodes')
        exit()

    # Process command line arguments
    proc_index = int( sys.argv[1] )
    number_of_proc = int( sys.argv[2] )
    init_preference = int (sys.argv[3])
    num_of_fault_process = int (sys.argv[4])

    # Creat list of all pors
    allPorts = [6000+i for i in range(number_of_proc)]

    #Set ports
    local_port = allPorts[proc_index]
    remote_ports = [x for x in allPorts if x != local_port]

    #Create queue for messages from the local server
    queue = Queue()

    #Create and start server process
    server = Process(target=server_fun, args=(local_port,queue))
    server.start()

    #Set the lst of the addresses of the peer node's servers
    remote_server_addresses = [('localhost', port) for port in remote_ports]

    k = 1
    round = 0
    pref = [None] * number_of_proc
    mult = 0
    mayor = 0
    even_counter = 0;
    result = [None] * number_of_proc

    msg = input('Enter message: ')
    #  while condition
    while (even_counter != num_of_fault_process + 1):

        round = round + 1

        if (round % 2 == 1):
            dict = odd_round(round, remote_server_addresses, init_preference, queue, number_of_proc, proc_index, mayor, mult, pref)
            mayor = dict.get("Mayor")
            mult = dict.get("Mult")
            pref = dict.get("Pref")
            print('MRS: ', mayor, mult, pref, '\n')
            print('################################')

        else:
            k, mayor, mult, pref = even_round(k, remote_server_addresses, init_preference, queue, number_of_proc, proc_index, mayor, mult, pref, num_of_fault_process)
            print('Round: ', round, 'ended, ', 'params:\n')
            print('K:', k, '\n')
            print('Major:', mayor, '\n')
            print('Mult:', mult, '\n')
            print('Pref:', pref, '\n')
            print('################################')
            even_counter += 1

    print(" Got out of while loop")
    result[proc_index] = pref[proc_index]

    print('Result: ', result)
    sendMsg( ('localhost', local_port), 'exit')


    # Join with server process
    server.join()

    # Delete queue and server
    del queue
    del server

if __name__ == '__main__':
    main()
