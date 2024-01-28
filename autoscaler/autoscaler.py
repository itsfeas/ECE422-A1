import time
import docker
import redis

SERVICE_NAME = "simpleweb_web"

def get_replicas(api_client):
    conf_dic = api_client.inspect_service(SERVICE_NAME)
    try:
        n_replicas = conf_dic["Spec"]["Mode"]["Replicated"]["Replicas"]
    except:
        print("SERVICE NOT CONFIGURED PROPERLY!!!!")
    return n_replicas

def scale_up(api_client, model, ratio):
    conf_dic = api_client.inspect_service(SERVICE_NAME)
    n_replicas = get_replicas(api_client)
    model.scale(replicas=n_replicas+1+(ratio-5))

def scale_down(api_client, model):
    n_replicas = get_replicas(api_client)
    model.scale(replicas=n_replicas-1)
    

def get_hits(red):
    i = red.get("hits")
    i = i if i else 0
    red.set("hits", 0)
    return int(i)

if __name__ == "__main__":
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    api_client = docker.APIClient(base_url='unix://var/run/docker.sock')
    # api_client.remove_service("simpleweb")

    # model = init_service(client)
    red = redis.Redis(host='localhost', port=6379)

    interval = 10
    while True:
        # update model of service
        services = client.services.list(filters = { "name": SERVICE_NAME })
        model = services[0]
        model = client.services.get(model.id)

        hits = get_hits(red)
        replicas = get_replicas(api_client)
        ratio = (hits*2/replicas) if replicas != 0 else 1

        print("hits: ", hits, "ratio: ", ratio, "replicas: ", replicas)
        if replicas==0 or (ratio>5 and replicas<50):
            scale_up(api_client, model, ratio)
        elif ratio<2 and replicas>1:
            scale_down(api_client, model)
        time.sleep(interval)
