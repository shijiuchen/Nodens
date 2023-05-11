
from client.client import rpc_get_profile




def getProfile(v,svc_name):
    return rpc_get_profile(v,svc_name)


if __name__ == '__main__':
    getProfile("10.2.64.8:50052","ebc1")
    