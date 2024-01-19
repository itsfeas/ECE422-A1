import time
import docker
import redis

def get_replicas(api_client: docker.APIClient):
    conf_dic = api_client.inspect_service("simpleweb")
    try:
        n_replicas = conf_dic["Spec"]["Mode"]["Replicated"]["Replicas"]
    except:
        print("SERVICE NOT CONFIGURED PROPERLY!!!!")
    return n_replicas

def scale_up(api_client: docker.APIClient, model):
    conf_dic = api_client.inspect_service("simpleweb")
    # n_replicas = None
    # try:
    #     n_replicas = conf_dic["Spec"]["Mode"]["Replicated"]["Replicas"]
    # except:
    #     print("SERVICE NOT CONFIGURED PROPERLY!!!!")
    n_replicas = get_replicas(api_client)
    model.scale(replicas=n_replicas+1)

def scale_down(api_client: docker.APIClient):
    n_replicas = get_replicas(api_client)
    model.scale(replicas=n_replicas-1)

def get_response_times():
    l = red.llen("client:times")
    lst = [int(t) for t in red.lpop("client:times", l)]
    return sum(lst)/len(lst)

def init_service(client: docker.DockerClient):
    model = client.services.create(
        image="zhijiewang22/simpleweb:1",
        name="simpleweb",
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
    api_client.remove_service("simpleweb")

    model = init_service(client)
    red = redis.Redis(host='localhost', port=6379)

    while True:
        time.sleep(20)
        ave = get_response_times()
        if ave>20:
            scale_up(api_client, model)
        elif ave<5:
            scale_down(api_client, model)