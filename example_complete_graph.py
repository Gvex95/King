import sys
from multiprocessing import Process, Queue
from msg_passing_api import *
from datetime import datetime

def even_round(k, remote_server_addresses, init_preference, queue, number_of_proc, proc_index, mayor, mult, pref, num_of_fault_process, pref1):

    local_mayor = mayor
    king_mayor = -1
	
	# Find new king and send your mayor to everybody
    if (proc_index != k):
	    
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

        if (mult > (number_of_proc / 2) + num_of_fault_process):
            print('Node: ', proc_index, ' will keep local mayor: ', local_mayor)
            pref[proc_index] = local_mayor

        else:
            print('Node: ', proc_index, ' will take kings mayor: ', king_mayor)
            pref[proc_index] = king_mayor
        
        for i in range(len(pref)):
            if (pref[proc_index] == local_mayor):
                pref1[i] = 1


    # If you are not king, recive message and determine new mayor for yourself
    else:
        print('Node: ', proc_index, ' I am king mother fuckers, broadcasting...')

        responded_proces = []
        broadcastMsg(remote_server_addresses, pref[proc_index])

        i = datetime.now()
        print (str(i))

        print('I have sent my mayor to all my minions')

		
    print('Round: ', 2*k, 'Node: ', proc_index,  'state: ', 'Pref: ', pref, ' Major: ', mayor, ' Mult: ', mult)
    k = k + 1
    return k, mayor,mult, pref, pref1

def odd_round(round, remote_server_addresses, init_preference, queue, number_of_proc, proc_index, mayor, mult, pref, pref1):
    counter = 0

    # Send message to peer node's servers
    broadcastMsg(remote_server_addresses, pref[proc_index])

    # Get message from local node's server
    msgs = rcvMsgs(queue, number_of_proc - 1)
    print('Node: ', proc_index, 'messages received:', msgs)

    #Saving messages from other nodes to prefs lists
    #Copy recived list
    pref = msgs[:]
    #Insert initial_preference at correct position
    pref.insert(proc_index, init_preference)
    print('Node: ', proc_index, 'prefs list state after reciving messages: ', pref)

    # Calculating mult
    mult = 0
    mayorIndex = -1
    for i in range(len(pref1)):
        if pref1[i] == 1:
            mayorIndex = i
            mult += 1
    
    mayor = pref[mayorIndex]

    print('Round: ', round, 'Node: ', proc_index,  'state: ', 'Pref: ', pref, ' Major: ', mayor, ' Mult: ', mult)
    dict = {"Mayor":mayor, "Mult":mult, "Pref":pref, "Pref1":pref1}
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
    pref1 = [None] * number_of_proc
    mult = 0
    mayor = 0
    even_counter = 0;
    result = [None] * number_of_proc
	
    pref[proc_index] = init_preference

    msg = input('Enter 0 or 1 (0 for fault value, 1 is correct value): ')
    
    msg2 = input('Press any key to start...')
    
    print('Sending correct or fault values to all processess')
    broadcastMsg(remote_server_addresses, int(msg))
    
    print('Receving correct or wrong from everyone else')
    
    
    pref1 = rcvMsgs(queue, number_of_proc - 1)
    pref1.insert(proc_index, int(msg))
    
    print('Pref1: ', pref1)
    print('############################################')
    
    
    
    
    #  while condition
    while (even_counter != num_of_fault_process + 1):

        round = round + 1

        if (round % 2 == 1):
            dict = odd_round(round, remote_server_addresses, init_preference, queue, number_of_proc, proc_index, mayor, mult, pref, pref1)
            mayor = dict.get("Mayor")
            mult = dict.get("Mult")
            pref = dict.get("Pref")
            pref1 = dict.get("Pref1")
            print('MRS: ', mayor, mult, pref, '\n')
            print('################################')

        else:
            k, mayor, mult, pref, pref1 = even_round(k, remote_server_addresses, init_preference, queue, number_of_proc, proc_index, mayor, mult, pref, num_of_fault_process, pref1)
            print('Round: ', round, 'ended, ', 'params:\n')
            print('K:', k, '\n')
            print('Major:', mayor, '\n')
            print('Mult:', mult, '\n')
            print('Pref:', pref, '\n')
            print('Pref1:', pref1, '\n')
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
