# Simple MPI test script.
# Rank 0 - "Server"
# All other ranks - "Clients"
# Each client sents 'numofmsg' to 'server' with 1 sec. delay
# Latency is very rough since based on timestamps from different nodes
#
# Author:
# - Danila Oleynik danila.oleynik@cern.ch, 2018

from mpi4py import MPI
import sys
import time
from datetime import datetime

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
max_rank = comm.Get_size()
numofmsg = 100

def timestamp():
    return datetime.now().strftime("%H:%M:%S.%f")


def server():

    print("{0} Hi, I am server!".format(timestamp()))
    print("Waiting for message from client")
    nr = 0
    while True:
        req = comm.irecv()
        data = req.wait()
        print("{0} recived: {1}, latency: {2:.6f}".format(timestamp(), data[0], time.time() - data[1]))
        nr += 1
        if nr >= (max_rank - 1) * numofmsg:
            break
    msg = "\nNumber of received messages from clients: {0}\n".format(nr)
    msg += "Number of ranks: {0}\n".format(max_rank)
    msg += "Number of clients: {0}\n".format(max_rank - 1)
    msg += "Number of msg per client: {0}\n".format(numofmsg)
    print(msg)

    return 0


def client():

    print("{1} I am client: {0}".format(rank, timestamp()))
    for i in range(1, numofmsg + 1):
        data = "Message {2} from rank: {0} at: {1}".format(rank, timestamp(), i)
        ts = time.time()
        req = comm.isend((data,ts), dest=0)
        req.wait()
        time.sleep(1)
    print("{1} client: {0}, {2} messages sent".format(rank, timestamp(), i))

    return 0


def main():

    #print('{0} Started'.format(timestamp()))
    #print("Job size: {0} ranks".format(max_rank))
    if rank == 0:
        server()
    else:
        client()

    return 0


if __name__ == "__main__":
    sys.exit(main())
