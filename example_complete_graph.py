import sys
from multiprocessing import Process, Queue
from msg_passing_api import *

def odd_round(k, remote_server_addresses, init_preference, queue, number_of_proc, proc_index, mayor, mult, pref):
    counter = 0

    # Send message to peer node's servers
    broadcastMsg(remote_server_addresses, init_preference)

    # Get message from local node's server
    msgs = rcvMsgs(queue, number_of_proc - 1)
    print('Node: ', proc_index, 'messages received:', msgs)

    #Saving messages from other nodes to prefs lists
    #Copy recived list
    pref = msgs[:]
    #Insert initial_preference at correct position
    pref.insert(proc_index, init_preference)
    print('Node: ', proc_index, 'prefs list state after reciving messages: ', pref)

    # Calculating mayor
    for i in range(len(msgs)):
        if (msgs[i] == init_preference):
            counter += 1

    if (counter > (len(msgs) - counter)):
        mayor = init_preference
    elif (counter < (len(msgs) - counter)):
        for i in range(len(msgs)):
            if (init_preference != msgs[i]):
                mayor = msgs[i]
    else:
        mayor = 0

    print('Node: ', proc_index, ' mayor number is: ', mayor)

    #Calculating mult 
    mult = 0
    for i in range(len(pref)):
        if (pref[i] == mayor):
            mult += 1
    print('Node: ', proc_index, ' mult number is: ', mult)

    print('Round: ', 2*k-1, 'Node: ', proc_index,  'state: ', 'Pref: ', pref, ' Major: ', mayor, ' Mult: ', mult)

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

    msg = input('Enter message: ')
    # k != num_of_fault_process + 1 while condition
    while (True):

        round+=1

        if (round % 2 == 0):
            odd_round(k, remote_server_addresses, init_preference, queue, number_of_proc, proc_index, mayor, mult, pref)
            break
        # if (recived_sum == 2 * (counter)):
        #     print("Phase :", counter, " passed ok, moving to next phase")
        #     print("There are: ", max_phases - counter, " phases remaining...")
        #     recived_sum = 0
        #
        # else:
        #     print(" Wrong phase: ", counter)
        #     print("State: \n", "Counter: ", counter, "\n", "Recived Sum: ", recived_sum, "\n")

    print(" Got out of while loop")
    sendMsg( ('localhost', local_port), 'exit')

    # Join with server process
    server.join()

    # Delete queue and server
    del queue
    del server

if __name__ == '__main__':
    main()
