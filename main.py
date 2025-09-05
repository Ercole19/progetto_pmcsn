import os
from libs.rng import *
import pandas as pd
import numpy as np
from half_improved_simulation import AirportSimulation
import matplotlib.pyplot as plt

# Parametri della simulazione
SEED = 123456789 #987654321 #123456789 #1359796324 # 1161688905
seed_used = []  # Lista dei seed utilizzati per ogni replica della simulazione (Per ripetibilità)

# ---------------- INFINITE HORIZON SIMULATION ----------------
INFINITE_HORIZON = False
BATCH_DIM =  16384                           # Campionamento ogni 16384 job (b)
BATCH_NUM =  25                              # Numero di campionamenti da eseguire (k)
INFINITE_HORIZON_TIME = BATCH_DIM * BATCH_NUM       # Lunghezza del campione

# ---------------- FINITE HORIZON SIMULATION ----------------
FINITE_HORIZON =        True
FINITE_HORIZON_TIME =  3600.0 * 24     # una giornata completa all'aeroporto --> 00:00 - 23:59
REPLICATION_NUM =      28           # numero di repliche eseguite
SAMPLING_RATE =        60           # Tempo di campionamento per le statistiche


def finite_horizon_run():
    total_percentiles_waits = []
    all_seeds_metrics = {}  # per memorizzare df di ogni seed
    current_seed = SEED
    seed_used.append(current_seed)

    for idx in range(REPLICATION_NUM):
        print(f"\nAvvio replica {idx + 1}/{REPLICATION_NUM} - Seed: {current_seed}")
        plant_seeds(seed_used[idx])  # imposta il seed per la replica corrente

        sim = AirportSimulation(
            end_time=FINITE_HORIZON_TIME,
            sampling_rate=SAMPLING_RATE,
            type_simulation="finite"
        )

        replica_metrics = sim.run()
        total_percentiles_waits.append(replica_metrics["daily_percentile_90_wait"])

        # -------------------- Stampa metriche finali e conteggi --------------------
        total_in_system = 0

        for pool_name, snapshots in replica_metrics.items():
            # Gestione pool vuoti o turnstiles
            if isinstance(snapshots, dict):  # caso turnstiles
                all_snaps = []
                for server_name, server_snaps in snapshots.items():
                    all_snaps = []
                    all_snaps.extend(server_snaps)
                    if not all_snaps:
                        continue
                    last_snapshot = all_snaps[-1]
                    print(f"  Pool={server_name}")
                    print(f"    In System: {last_snapshot.get('in_system', 0)}")
                    print(f"    Queue Length: {last_snapshot.get('queue_length', 0)}")
                    print(f"    Utilization: {last_snapshot.get('avg_utilization', 0):.2f}")
                    print(f"    Avg Waiting Time: {last_snapshot.get('avg_waiting_time', 0):.2f}")
                    print(f"    Avg Response Time: {last_snapshot.get('avg_response_time', 0):.2f}")
                    total_in_system += last_snapshot.get('in_system', 0) + last_snapshot.get("queue_length", 0)

            elif isinstance(snapshots, list):
                if not snapshots:
                    continue
                last_snapshot = snapshots[-1]
                print(f"  Pool={pool_name}")
                print(f"    In System: {last_snapshot.get('in_system', 0)}")
                print(f"    Queue Length: {last_snapshot.get('queue_length', 0)}")
                print(f"    Utilization: {last_snapshot.get('avg_utilization', 0):.2f}")
                print(f"    Avg Waiting Time: {last_snapshot.get('avg_waiting_time', 0):.2f}")
                print(f"    Avg Response Time: {last_snapshot.get('avg_response_time', 0):.2f}")
                total_in_system += last_snapshot.get('in_system', 0)
            else:
                continue

        print(f"\n  Totale passeggeri completati: {replica_metrics["security_area"]["security_0"][-1]["passengers_completed"]}")
        print(f"  Totale passeggeri ancora in sistema: {total_in_system}")
        print("-" * 50)

        # -------------------- Converti in DataFrame --------------------
        all_data = []
        for key in replica_metrics.keys():
            if key != "daily_percentile_90_wait":
                if isinstance(replica_metrics[key], list):
                    for snap in replica_metrics[key]:
                        snap["pool_name"] = key
                        all_data.append(snap)
                else:  # turnstiles
                    for server_name, server_snaps in replica_metrics[key].items():
                        for snap in server_snaps:
                            snap["pool_name"] = f"{key}_{server_name}"
                            all_data.append(snap)

        df = pd.DataFrame(all_data)
        df = df.sort_values(["pool_name", "time"])
        all_seeds_metrics[current_seed] = df

        # -------------------- Grafici per ogni pool --------------------
        out_dir = f"finite_seed_{current_seed}"
        """os.makedirs(out_dir, exist_ok=True)

        pool_names = df["pool_name"].unique()
        for pool in pool_names:
            df_pool = df[df["pool_name"] == pool]
            x = df_pool["time"]

            plt.figure(figsize=(12,6))
            for metric, color in zip(
                ["avg_utilization","avg_waiting_time","avg_response_time","avg_queue_population"],
                ["blue","orange","green","purple"]
            ):
                plt.plot(x, df_pool[metric], label=metric, color=color)
            plt.xlabel("Tempo")
            plt.ylabel("Valore")
            plt.title(f"Pool: {pool} - Seed {current_seed}")
            plt.legend()
            plt.grid(True)
            plt.savefig(os.path.join(out_dir, f"{pool}_metrics.png"))
            plt.close()

        # Aggiorna seed per la prossima replica
        """

        current_seed = get_seed()
        seed_used.append(current_seed)

    # -------------------- Grafici globali per metrica e per pool --------------------
    total_percentile = np.percentile(total_percentiles_waits, 90)
    print(f"90th percentile global: {total_percentile:.2f} seconds")

    metrics = ["avg_utilization", "avg_waiting_time", "avg_response_time", "avg_queue_population"]

    # Recupero tutti i pool/centro presenti
    all_pools = set()
    for df in all_seeds_metrics.values():
        all_pools.update(df["pool_name"].unique())

    for pool in all_pools:
        for metric in metrics:
            plt.figure(figsize=(12, 6))
            for seed, df in all_seeds_metrics.items():
                df_pool = df[df["pool_name"] == pool]
                if df_pool.empty:
                    continue
                df_grouped = df_pool.groupby("time")[metric].mean().reset_index()
                plt.plot(df_grouped["time"], df_grouped[metric], label=f"Seed {seed}")

            plt.xlabel("Tempo")
            plt.ylabel(metric)
            plt.title(f"Andamento di {metric} per {pool} (confronto seed)")
            plt.legend()
            plt.grid(True)

            global_dir = "global_metrics_half"
            os.makedirs(global_dir, exist_ok=True)
            plt.savefig(os.path.join(global_dir, f"{pool}_{metric}.png"))
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

    # Avvia simulazione
    sim = AirportSimulation(
        end_time=float('inf'),
        sampling_rate=BATCH_DIM,
        type_simulation="infinite",
        batch_num=BATCH_NUM
    )
    metrics = sim.run()

    # -------------------- Converti in DataFrame unico --------------------
    all_data = []
    for key in metrics.keys():
        if isinstance(metrics[key], list):
            for snap in metrics[key]:
                snap["pool_name"] = key
                all_data.append(snap)
        else:  # caso turnstiles (dizionario per server)
            for server_name, server_snaps in metrics[key].items():
                for snap in server_snaps:
                    snap["pool_name"] = f"{key}_{server_name}"
                    all_data.append(snap)

    df = pd.DataFrame(all_data)
    df = df.sort_values(["pool_name", "time"])

    # 🔹 Aggiungi colonna batch (contatore snapshot per pool)
    df["batch"] = df.groupby("pool_name").cumcount() + 1

    # --- Crea cartella ---
    out_dir = "infinite_plots"
    os.makedirs(out_dir, exist_ok=True)

    # -------------------- Grafici per singolo pool --------------------
    pool_names = df["pool_name"].unique()

    for pool in pool_names:
        df_pool = df[df["pool_name"] == pool]
        x = df_pool["batch"]  # uso batch al posto del tempo

        plt.figure(figsize=(12, 6))

        plt.subplot(2, 2, 1)
        plt.plot(x, df_pool["avg_utilization"], label="Utilizzazione media")
        plt.xlabel("Batch")
        plt.ylabel("Utilizzazione")
        plt.title(f"Pool: {pool} — Utilizzazione")
        plt.grid(True)

        plt.subplot(2, 2, 2)
        plt.plot(x, df_pool["avg_waiting_time"], label="Tempo medio di attesa", color="orange")
        plt.xlabel("Batch")
        plt.ylabel("Attesa (s)")
        plt.title(f"Pool: {pool} — Tempo medio di attesa")
        plt.grid(True)

        plt.subplot(2, 2, 3)
        plt.plot(x, df_pool["avg_response_time"], label="Tempo medio di risposta", color="green")
        plt.xlabel("Batch")
        plt.ylabel("Risposta (s)")
        plt.title(f"Pool: {pool} — Tempo medio di risposta")
        plt.grid(True)

        plt.subplot(2, 2, 4)
        plt.plot(x, df_pool["avg_queue_population"], label="Popolazione media in coda", color="purple")
        plt.xlabel("Batch")
        plt.ylabel("Lq")
        plt.title(f"Pool: {pool} — Popolazione media in coda")
        plt.grid(True)

        plt.tight_layout()
        plt.savefig(os.path.join(out_dir, f"{pool}_metrics.png"))
        plt.close()

    # -------------------- Grafico comparativo tra pool --------------------
    plt.figure(figsize=(12, 6))
    for pool in pool_names:
        df_pool = df[df["pool_name"] == pool]
        plt.plot(df_pool["batch"], df_pool["avg_utilization"], label=pool)

    plt.xlabel("Batch")
    plt.ylabel("Utilizzazione media")
    plt.title("Utilizzazione media per Pool per batch")
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(out_dir, "all_pools_utilization.png"))
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