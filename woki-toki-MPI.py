# Simple 'woki-toki' MPI test script.
# Rank 0 - "Server"
# All other ranks - "Clients"
# Each client sents messages to 'server' and waiting for reply.
# Server sends reply for each received message to corresponded client
# Latency is very rough since based on timestamps from different nodes
# Some report published in csv file
#
# Author:
# - Danila Oleynik danila.oleynik@cern.ch, 2018



from mpi4py import MPI
import sys
import time
from datetime import datetime
import csv
import socket
import random


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
max_rank = comm.Get_size()
numofmsg = 50


def timestamp():
    return datetime.now().strftime("%H:%M:%S.%f")


def server():
    hostname = socket.gethostname()
    print("{0} Hi, I am server! [{1}]".format(timestamp(),hostname))
    print("Waiting for messages from client")
    nr = 0
    csvfile = open('wt_report_numbers_{0}_{1}.csv'.format(max_rank, random.randint(1000,9999)), 'wb')
    cvswriter = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    cvswriter.writerow(['Timestamp', "Operation","Node","Source_rank", "Dest_rank", "Message#", "Message timestamp", "","Latency"])
    while True:
        for r in range(max_rank)[1:]:
            req = comm.irecv(source=r)
            data = req.wait()
            latency_r = "{0:.6f}".format(time.time() - data[1])
            cvswriter.writerow([timestamp(), "received",data[2], int(data[0]), 0, data[3], datetime.fromtimestamp(data[1]).strftime('%H:%M:%S.%f'), latency_r])
            ts = timestamp()
            req = comm.isend((rank, ts, hostname, data[3]), dest=r)
            req.wait()
            latency_s = "{0:.6f}".format(time.time() - data[1])
            cvswriter.writerow([timestamp(), "sent", hostname, 0, int(data[0]), data[3], ts, latency_s])
            nr += 1
        if nr >= (max_rank - 1) * numofmsg:
            break

    csvfile.close()
    msg = "\nNumber of received messages from clients: {0}\n".format(nr)
    msg += "Number of ranks: {0}\n".format(max_rank)
    msg += "Number of clients: {0}\n".format(max_rank - 1)
    msg += "Number of msg per client: {0}\n".format(numofmsg)
    print(msg)
    return 0


def client(rank):
    hostname = socket.gethostname()
    print("{1} I am client [{2}]: {0}".format(rank, timestamp(), hostname))
    for i in range(1,numofmsg+1):
        ts = time.time()
        req = comm.isend((rank,ts,hostname,i), dest=0)
        req.wait()
        response = comm.irecv(source=0)
        data = response.wait()
        print("{0} | {1} | Message {2} from server recived ".format(timestamp(), rank, data[3]))
        time.sleep(1)
    print("{1} client [{3}]: {0}, {2} messages sent".format(rank, timestamp(), i, hostname))

    return 0


def main():

    if rank == 0:
        server()
    else:
        client(rank)

    return 0


if __name__ == "__main__":
    sys.exit(main())
