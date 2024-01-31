import time
import docker
import redis
import shutil
from torch.utils.tensorboard import SummaryWriter

SERVICE_NAME = "simpleweb_web"

class RedisClient:
    red = None
    def __init__(self, host='localhost', port=6379):
        self.red = redis.Redis(host=host, port=port)
    
    def get_hits(self):
        i = self.red.get("hits")
        return i if i else 0
    
    def reset_hits(self):
        self.red.set("hits", 0)


class AutoScaler:
    disabled = None
    client = None
    api_client = None
    model = None
    limit = None
    red = None
    def __init__(self, limit=50, disabled=False):
        self.client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        self.api_client = docker.APIClient(base_url='unix://var/run/docker.sock')
        self.red = RedisClient()
        self.limit = limit
        self.disabled = disabled
        self.connect()
        self.model.scale(replicas=1)

    def get_replicas(self):
        conf_dic = self.api_client.inspect_service(SERVICE_NAME)
        try:
            n_replicas = conf_dic["Spec"]["Mode"]["Replicated"]["Replicas"]
        except:
            print("SERVICE NOT CONFIGURED PROPERLY!!!!")
        return n_replicas
    
    def scale_up(self, ratio):
        n_replicas = self.get_replicas()
        self.model.scale(replicas=int(n_replicas+1+(ratio-5)))

    def scale_down(self):
        n_replicas = self.get_replicas()
        self.model.scale(replicas=n_replicas-1)
    
    def connect(self):
        services = self.client.services.list(filters = { "name": SERVICE_NAME })
        m = services[0]
        self.model = self.client.services.get(m.id)
    
    def get_hits(self):
        hits = self.red.get_hits()
        self.red.reset_hits()
        return int(hits)
    
    def monitor(self, interval):
        logger = SummaryWriter()
        counter = 0
        self.red.reset_hits()
        while True:
            # update model of service
            self.connect()

            hits = self.get_hits()
            replicas = self.get_replicas()
            ratio = (hits*2/replicas) if replicas != 0 else 1

            print("hits: ", hits, "ratio: ", ratio, "replicas: ", replicas)
            if not self.disabled:
                if replicas==0 or (ratio>5 and replicas<self.limit):
                    self.scale_up(ratio)
                elif ratio<2 and replicas>1:
                    self.scale_down()
            
            logger.add_scalar("replicas", replicas, counter)
            logger.add_scalar("requests/s", hits/10, counter)
            counter += 1 
            time.sleep(interval)


if __name__ == "__main__":
    interval = 10
    if os.path.exists("runs/"):
        shutil.rmtree("runs/")
    red = redis.Redis(host='localhost', port=6379)
    scaler = AutoScaler()
    # scaler = AutoScaler(disabled=True)
    scaler.monitor(interval)
