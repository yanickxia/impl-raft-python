# This is a sample Python script.
import time

import zerorpc
from server import RaftServer
import threading
from concurrent.futures import ThreadPoolExecutor

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    servers = {}

    for i in range(1, 6):
        sid = str(i)
        rs = RaftServer(sid)
        servers[sid] = (zerorpc.Server(rs), rs)

    for i in range(1, 6):
        sid = str(i)
        rs = servers[sid][1]
        remotes = {}
        for j in range(1, 6):
            if j != i:
                remotes[str(j)] = servers[str(j)][0]

        rs.servers = remotes

    with ThreadPoolExecutor() as executor:
        for i in range(1, 6):
            sid = str(i)
            rs = servers[sid][0]
            rs.bind("tcp://127.0.0.1:1500" + sid)
            executor.submit(rs.run)
    print("inited.....")
    while True:
        time.sleep(1000)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
