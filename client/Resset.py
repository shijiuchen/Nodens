import os
from collections import defaultdict
from client.client import rpc_adjust_res
import pandas
import time
from multiprocessing import Process
import datetime



def setProfile(ip_str,uids,value):
    return rpc_adjust_res(ip_str,uids,value)


if __name__ == '__main__':
    # setProfile("10.2.64.8:50052")
    print("Resset")