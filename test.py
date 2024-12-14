import ray

# Start verbinding met de Ray cluster
ray.init(address="192.168.178.157:6379")

# Een simpele Ray taak
@ray.remote
def test_task():
    return "Success"

# Voer de taak uit en print het resultaat
result = ray.get(test_task.remote())
print(result)
