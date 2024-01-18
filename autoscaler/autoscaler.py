import docker

def scale_up(client: docker.DockerClient):
    service = client.services.get("web")
    n_replicas = client
    client.api.get
    client.services.model.scale(replicas=n_replicas+1)

def scale_down():
    pass

def monitor():
    pass

if __name__ == "__main__":
    client = docker.from_env()
    # api_client = docker.APIClient(base_url='unix://var/run/docker.sock')
    model = client.services.create(image="zhijiewang22/simpleweb")
    
    