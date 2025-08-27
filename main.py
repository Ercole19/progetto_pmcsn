from rng.rng import *
from simulation_6 import AirportSimulation
import pandas as pd
import matplotlib.pyplot as plt

# Parametri della simulazione
SEED = 123456789 #987654321 #123456789 #1359796324 # 1161688905
seed_used = []  # Lista dei seed utilizzati per ogni replica della simulazione (Per ripetibilità)

# ---------------- INFINITE HORIZON SIMULATION ----------------
INFINITE_HORIZON = True
BATCH_DIM = 512                                   # Campionamento ogni 512 job (b)
BATCH_NUM = 64                                    # Numero di batch da eseguire (k)
INFINITE_HORIZON_TIME = BATCH_DIM * BATCH_NUM       # Lunchezza del campione

# ---------------- FINITE HORIZON SIMULATION ----------------
FINITE_HORIZON =        False
FINITE_HORIZON_TIME =   86400.0     # una giornata completa all'aeroporto --> 00:00 - 23:59
REPLICATION_NUM =       1           # numero di repliche eseguite
SAMPLING_RATE =         120           # Tempo di campionamento per le statistiche


def finite_horizon_run():
    all_metrics = []
    replica_metrics = None

    # Inizializza il primo seed
    current_seed = SEED
    seed_used.append(current_seed)

    # Esecuzione delle repliche
    for index in range(REPLICATION_NUM):

        # Contatore che tiene traccia delle repliche rimanenti
        remaining_replica = REPLICATION_NUM - (index + 1)

        print(f"\n Avvio replica {index + 1}/{REPLICATION_NUM} - Seed: {get_seed()}")
        plant_seeds(seed_used[index])                 # imposta il seed per la replica corrente

        # Crea nuova istanza della simulazione (stato pulito!)
        sim = AirportSimulation(
            end_time=FINITE_HORIZON_TIME,
            sampling_rate=SAMPLING_RATE,
            type_simulation="finite"
        )

        replica_metrics = sim.run()
        all_metrics.append(replica_metrics)

        # Prepara seed per la prossima replica, se è presente
        if remaining_replica != 0:
            current_seed = get_seed()
            seed_used.append(current_seed)

    # Fine ciclo repliche
    print("Tutte le repliche finite.")
    for s in seed_used:
        print("Seed usato:", s)

    # -------------------- STAMPA METRICHE FINALI --------------------
    print("\n Metriche finali per ogni replica:\n")

    for idx, replica_metrics in enumerate(all_metrics):
        last_snapshot = replica_metrics[-1]  # Ultimo snapshot temporale della replica

        print(f"Replica {idx + 1}:")
        print(f"  Passeggeri da Servire: {last_snapshot['global']['total_in_system']}")
        print(f"  Passeggeri usciti dal sistema: {last_snapshot['global']['passengers_completed']}")
        print(f"  Lunghezza media code: {last_snapshot['global']['avg_queue_length']:.2f}")
        print(f"  Utilizzo medio server: {last_snapshot['global']['avg_utilization']:.2f}")

        print("  --> Utilizzazione per ogni centro:")
        for s in last_snapshot["servers"]:
            print(f"     - {s['name']}: Utilizzazione={s['utilization']:.2f}, in sistema={s['in_system']}, busy={s['busy']}")

        print("  --> Lunghezza code per pool:")
        for q in last_snapshot["queue_lengths"]:
            print(f"     - {q['name']}: {q['length']}")

        print("-" * 50)

    # -------------------- Extract Metrics --------------------
    times = [m["time"] for m in replica_metrics]

    # Global metrics
    total_in_system = [m["global"]["total_in_system"] for m in replica_metrics]
    avg_queues = [m["global"]["avg_queue_length"] for m in replica_metrics]
    avg_utilizations = [m["global"]["avg_utilization"] for m in replica_metrics]

    # Per-server metrics
    server_names = [s["name"] for s in replica_metrics[0]["servers"]]
    server_utilizations = {name: [] for name in server_names}

    # Per-pool queue length
    pool_names = [q["name"] for q in replica_metrics[0]["queue_lengths"]]
    pool_queues = {name: [] for name in pool_names}

    for m in replica_metrics:
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
    # Inizializza il seed
    current_seed = SEED
    seed_used.append(current_seed)
    plant_seeds(current_seed)

    # Avvia simulazione
    sim = AirportSimulation(
        end_time=float('inf'),
        sampling_rate=BATCH_DIM,
        type_simulation="infinite",
        batch_num=BATCH_NUM
    )
    metrics = sim.run()

    # -------------------- Converti in DataFrame --------------------
    df = pd.DataFrame(metrics)
    df = df.sort_values("time")

    # -------------------- Grafici per pool --------------------
    pool_names = df["pool_name"].unique()

    for pool in pool_names:
        df_pool = df[df["pool_name"] == pool]
        t = df_pool["time"]

        plt.figure(figsize=(12, 6))

        plt.subplot(2, 2, 1)
        plt.plot(t, df_pool["avg_utilization"], label="Utilizzazione media")
        plt.xlabel("Tempo")
        plt.ylabel("Utilizzazione")
        plt.title(f"Pool: {pool} — Utilizzazione")
        plt.grid(True)

        plt.subplot(2, 2, 2)
        plt.plot(t, df_pool["avg_waiting_time"], label="Tempo medio di attesa", color="orange")
        plt.xlabel("Tempo")
        plt.ylabel("Attesa (s)")
        plt.title(f"Pool: {pool} — Tempo medio di attesa")
        plt.grid(True)

        plt.subplot(2, 2, 3)
        plt.plot(t, df_pool["avg_response_time"], label="Tempo medio di risposta", color="green")
        plt.xlabel("Tempo")
        plt.ylabel("Risposta (s)")
        plt.title(f"Pool: {pool} — Tempo medio di risposta")
        plt.grid(True)

        plt.subplot(2, 2, 4)
        plt.plot(t, df_pool["avg_queue_population"], label="Popolazione media in coda", color="purple")
        plt.xlabel("Tempo")
        plt.ylabel("Lq")
        plt.title(f"Pool: {pool} — Popolazione media in coda")
        plt.grid(True)

        plt.tight_layout()
        plt.savefig(f"{pool}_metrics.png")
        plt.close()

    # -------------------- Grafico comparativo tra pool --------------------
    plt.figure(figsize=(12, 6))
    for pool in pool_names:
        df_pool = df[df["pool_name"] == pool]
        plt.plot(df_pool["time"], df_pool["avg_utilization"], label=pool)

    plt.xlabel("Tempo")
    plt.ylabel("Utilizzazione media")
    plt.title("Utilizzazione media per Pool nel tempo")
    plt.legend()
    plt.grid(True)
    plt.savefig("all_pools_utilization.png")
    plt.close()

    return df



# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    if INFINITE_HORIZON:
        infinite_horizon_run()

    elif FINITE_HORIZON:
        finite_horizon_run()

    else:
        raise ValueError("Errore: Nessun orizzonte di simulazione selezionato")