import ray
import time

# Initialiseer Ray (verbind met de cluster)
ray.init(address='auto')  # Verbind met de cluster, automatisch de master node vinden

# Functie om de beschikbare nodes weer te geven
def print_cluster_nodes():
    nodes = ray.nodes()
    print("Beschikbare nodes in de Ray-cluster:")
    for node in nodes:
        # Toon de IP en of de node actief is
        node_ip = node['NodeManagerAddress']
        node_alive = node.get('Alive', 'Onbekend')  # Gebruik 'Alive' om te controleren of de node actief is
        print(f"Node IP: {node_ip} - Status: {'Actief' if node_alive else 'Inactief'}")

# Functie voor de rekenintensieve taak
@ray.remote
def compute_square(x):
    time.sleep(1)  # Simuleer een rekenintensieve taak
    return x * x

# Functie om een schaalbare taak uit te voeren
def run_scalability_test(num_tasks, num_nodes):
    # Toon de cluster nodes
    print_cluster_nodes()
    
    # Test met één node
    print(f"\n### Test met {num_nodes} nodes ###")
    
    # Genereer een lijst van getallen om te verwerken
    numbers = list(range(1, num_tasks + 1))
    
    # Start de parallelle berekeningen
    start_time = time.time()
    futures = [compute_square.remote(num) for num in numbers]
    
    # Wacht op de resultaten
    results = ray.get(futures)
    end_time = time.time()
    
    print(f"\nResultaten van de kwadraten (eerste 10 getallen): {results[:10]}...")
    print(f"Tijd voor {num_tasks} taken op {num_nodes} node(s): {end_time - start_time:.2f} seconden")
    
    return end_time - start_time

# Start met 1 node
run_scalability_test(num_tasks=100, num_nodes=1)

# Voeg een tweede node toe aan de Ray-cluster (op de worker node)
# Je moet handmatig de worker starten op een andere node, bijvoorbeeld:
# ray start --address='192.168.178.157:6379' --node-ip-address=192.168.178.122
# Deze stap moet gedaan worden op je worker node via de commandoregel.

# Test met 2 nodes
run_scalability_test(num_tasks=100, num_nodes=2)

# Test met 4 nodes (indien mogelijk)
# Zorg ervoor dat je meer worker nodes hebt en start ze handmatig.
run_scalability_test(num_tasks=100, num_nodes=4)

# Stop Ray-cluster na de tests
ray.shutdown()
