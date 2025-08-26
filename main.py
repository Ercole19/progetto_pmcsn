##from Simulation import start_simulation
import os

from PIL.JpegImagePlugin import samplings

from params import *
from rng.rng import *
from simulation_5 import AirportSimulation
import matplotlib.pyplot as plt

# Parametri della simulazione
SEED = 987654321 #123456789 #123456789 #1359796324 # 1161688905
seed_used = [SEED]  # Lista dei seed utilizzati per ogni replica della simulazione (Per ripetibilità)

# ---------------- INFINITE HORIZON SIMULATION ----------------
INFINITE_HORIZON = False
BATCH_DIM = 512  # Campionamento ogni 512 job (b)
BATCH_NUM = 1024  # Numero di batch da eseguire (k)
INFINITE_HORIZON_TIME = BATCH_DIM * BATCH_NUM

# ---------------- FINITE HORIZON SIMULATION ----------------
FINITE_HORIZON = not INFINITE_HORIZON  # Se non è una simulazione a orizzonte finito allora è a orizzonte infinito
FINITE_HORIZON_TIME = 4 * 60  # 4 ore di simulazione
REPLICATION_NUM = 1000
SAMPLING_RATE = 1  # Tempo di campionamento per le statistiche


def finite_horizon_run():
    '''end_simulation_time = FINITE_HORIZON_TIME

    # Inizializzazione file csv per le statistiche (Crea il file se non esiste o cancella contenuto se esiste)
    directory = DIRECTORY_FINITE_H
    files = [CSV_UTILIZATION, CSV_DELAY, CSV_WAITING_TIME, CSV_END_WORK_TIME_FINITE]

    # Cancella il contenuto del file
    for file in files:
        with open(os.path.join(directory, file), 'w') as f:
            f.write('')

    plant_seeds(SEED)
    # Esecuzione delle repliche
    for ri in range(REPLICATION_NUM):
        print("Starting replica for finite-horizon simulation, seed: ", get_seed())
        # plantSeeds(getSeed())
        start_simulation(end_simulation_time, "finite", SAMPLING_RATE)
        select_stream(0)
        seed_used.append(get_seed())
        print(f"Simulation {ri + 1}/{REPLICATION_NUM} ending seed: {get_seed()}")
    print("fine simulazione")
    for s in seed_used:
        print(s)'''

    sim = AirportSimulation(end_time=86400.0, sampling_rate=60.0, type_simulation="finite")
    metrics = sim.run()

    # -------------------- Extract Metrics --------------------
    times = [m["time"] for m in metrics]

    # Global metrics
    total_in_system = [m["global"]["total_in_system"] for m in metrics]
    avg_queues = [m["global"]["avg_queue_length"] for m in metrics]
    avg_utilizations = [m["global"]["avg_utilization"] for m in metrics]

    # Per-server metrics
    server_names = [s["name"] for s in metrics[0]["servers"]]
    server_utilizations = {name: [] for name in server_names}

    # Per-pool queue length
    pool_names = [q["name"] for q in metrics[0]["queue_lengths"]]
    pool_queues = {name: [] for name in pool_names}

    for m in metrics:
        for s in m["servers"]:
            server_utilizations[s["name"]].append(s["utilization"])
        for q in m["queue_lengths"]:
            pool_queues[q["name"]].append(q["length"])

    # -------------------- Plot Metrics --------------------
    import matplotlib.pyplot as plt

    plt.figure(figsize=(12, 8))

    # Clients in system
    plt.subplot(2, 2, 1)
    plt.plot(times, total_in_system, label="Total in system")
    plt.xlabel("Time")
    plt.ylabel("Clients")
    plt.title("Clients in System")
    plt.grid(True)

    # Average queue length
    plt.subplot(2, 2, 3)
    plt.plot(times, avg_queues, label="Average Queue Length", color="green")
    plt.xlabel("Time")
    plt.ylabel("Queue Length")
    plt.title("Average Queue Length Over Time")
    plt.grid(True)

    # Average utilization
    plt.subplot(2, 2, 4)
    plt.plot(times, avg_utilizations, label="Average Utilization", color="red")
    plt.xlabel("Time")
    plt.ylabel("Utilization")
    plt.title("Average Server Utilization")
    plt.grid(True)

    plt.tight_layout()
    plt.savefig("output.png")
    plt.close()

    # Per-server utilization
    plt.figure(figsize=(12, 6))
    for name, values in server_utilizations.items():
        plt.plot(times, values, label=name)
    plt.xlabel("Time")
    plt.ylabel("Utilization")
    plt.title("Utilization per Server Over Time")
    plt.legend()
    plt.grid(True)
    plt.savefig("server_utilization.png")
    plt.close()

    # Per-pool queue length
    plt.figure(figsize=(12, 6))
    for pool_name, values in pool_queues.items():
        plt.plot(times, values, label=pool_name)
    plt.xlabel("Time")
    plt.ylabel("Queue Length")
    plt.title("Queue Length per Pool Over Time")
    plt.legend()
    plt.grid(True)
    plt.savefig("pool_queue_length.png")
    plt.close()


def infinite_horizon_run():
    sim = AirportSimulation(end_time=86400.0, sampling_rate=60.0, type_simulation="finite")
    metrics = sim.run()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Inizializza il generatore di numeri casuali
    plant_seeds(SEED)
    if INFINITE_HORIZON:
        infinite_horizon_run()

    elif FINITE_HORIZON:
        finite_horizon_run()
    else:
        raise ValueError("Errore: Nessun orizzonte di simulazione selezionato")








