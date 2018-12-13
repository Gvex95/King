import sys
from multiprocessing import Process, Queue
from msg_passing_api import *

def odd_round(k, remote_server_addresses, init_preference, queue, number_of_proc, mayor, mult):
    counter = 0

    # Send message to peer node's servers
    broadcastMsg(remote_server_addresses, init_preference)

    # Get message from local node's server
    msgs = rcvMsgs(queue, number_of_proc - 1)
    print('Node: ', number_of_proc, 'messages received:', msgs)

    #Saving messages from other nodes to prefs list
    # We dont need to save in proc_index position, that is already done
    # in initialization

    for i in range(len(msgs)):
        if ( i == proc_index):
            continue
        else:
            pref[i] = rcvMsgs[i]
    print('Node: ', number_of_proc, 'prefs list state after reciving messages: ', prefs)

    # Calculating mayor
    for i in range(len(msgs)):
        if (msgs[i] == init_preference):
            counter += 1

    if (counter > (len(msgs) - counter)):
        mayor = init_preference
    else if (counter < (len(msgs) - counter):
        for i in range(len(msgs)):
            if (init_preference != msgs[i]):
                mayor = msgs[i]
    else:
        mayor = 0

    print('Node: ', proc_index, ' mayor number is: ', mayor)

    #Calculating mult
    mult = 0
    for i in range(len(msgs)):
        if (msgs[i] == i):
            mult += 1
    print('Node: ', proc_index, ' mult number is: ', mult)

def main():
    # Parse command line arguments
    if len(sys.argv) != 3:
        print('Program usage: example_complete_graph proc_index number_of_proc')
        print('Example: If number_of_proc = 3, we must start 3 instances of program in 3 terminals:')
        print('example_complete_graph 0 3, example_complete_graph 1 3, and example_complete_graph 2 3')
        exit()

    # Process command line arguments
    proc_index = int( sys.argv[1] )
    number_of_proc = int( sys.argv[2] )
    init_preference = int (sys.argv[3])
    num_of_fault_process = (int(sys.argv[4])
    # Creat list of all pors
    allPorts = [6000+i for i in range(number_of_proc)]

    # Set ports
    local_port =   allPorts[proc_index]
    remote_ports = [x for x in allPorts if x != local_port]

    # Create queue for messages from the local server
    queue = Queue()

    # Create and start server process
    server = Process(target=server_fun, args=(local_port,queue))
    server.start()

    # Set the lst of the addresses of the peer node's servers
    remote_server_addresses = [('localhost', port) for port in remote_ports]

    # Send a message to the peer node and receive message from the peer node.
    # To exit send message: exit.

    k = 1
    round = 0
    pref = []
    mult = 0
    mayor = 0

    #Initialy store your initial value in corresponding place in list
    pref[proc_index] = init_preference

    msg = input('Enter message: ')

    while (k != num_of_fault_process + 1):

        round+=1

        if (round % 2 == 0):
            odd_round(k, remote_server_addresses, init_preference, queue, number_of_proc, mayor, mult)

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
