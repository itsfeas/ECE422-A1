import time
import docker
import redis

SERVICE_NAME = "simpleweb_web"

def get_replicas(api_client: docker.APIClient):
    conf_dic = api_client.inspect_service(SERVICE_NAME)
    try:
        n_replicas = conf_dic["Spec"]["Mode"]["Replicated"]["Replicas"]
    except:
        print("SERVICE NOT CONFIGURED PROPERLY!!!!")
    return n_replicas

def scale_up(api_client: docker.APIClient, model):
    conf_dic = api_client.inspect_service(SERVICE_NAME)
    # n_replicas = None
    # try:
    #     n_replicas = conf_dic["Spec"]["Mode"]["Replicated"]["Replicas"]
    # except:
    #     print("SERVICE NOT CONFIGURED PROPERLY!!!!")
    n_replicas = get_replicas(api_client)
    model.scale(replicas=n_replicas+1)

def scale_down(api_client: docker.APIClient, model):
    n_replicas = get_replicas(api_client)
    model.scale(replicas=n_replicas-1)

def get_hits(red: redis.Redis):
    i = red.get("hits")
    i = i if i else 0
    red.set("hits", 0)
    return i

def init_service(client: docker.DockerClient):
    model = client.services.create(
        image="zhijiewang22/simpleweb:1",
        name=SERVICE_NAME,
        resources = {
            "limits": {
                "cpus": "0.25",
                "memory": "256M"
            }
        },
        endpoint_spec = {
            "Ports": [
                {
                    "PublishedPort": 8000,
                    "TargetPort": 8000
                }
            ]
        }
    )
    return model

if __name__ == "__main__":
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    api_client = docker.APIClient(base_url='unix://var/run/docker.sock')
    # api_client.remove_service("simpleweb")

    # model = init_service(client)
    services = client.services.list(filters = { "name": SERVICE_NAME })
    model = services[0]
    model = client.services.get(model.id)
    red = redis.Redis(host='localhost', port=6379)

    while True:
        time.sleep(20)
        hits = get_hits(red)
        replicas = get_replicas(api_client)
        ratio = (hits/20)/replicas #(hits/s)/replica
        if replicas==0 or ratio>5:
            scale_up(api_client, model)
        elif hits<1 and replicas>1:
            scale_down(api_client, model)