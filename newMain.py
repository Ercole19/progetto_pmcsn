from rng.rng import *
from simulation_8 import AirportSimulation

# Parametri della simulazione
SEED = 123456789
seed_used = []

# INFINITE HORIZON SIMULATION
INFINITE_HORIZON = True
BATCH_DIM = 64 #48  #64
BATCH_NUM = 32 #256 #1344
INFINITE_HORIZON_TIME = BATCH_DIM * BATCH_NUM

# FINITE HORIZON SIMULATION
FINITE_HORIZON = False
FINITE_HORIZON_TIME = 86400.0  # 1 giorno
REPLICATION_NUM = 1
SAMPLING_RATE = 120


def finite_horizon_run():
    all_metrics = []

    current_seed = SEED
    seed_used.append(current_seed)

    for index in range(REPLICATION_NUM):
        remaining_replica = REPLICATION_NUM - (index + 1)
        print(f"\nAvvio replica {index + 1}/{REPLICATION_NUM} - Seed: {get_seed()}")
        plant_seeds(seed_used[index])

        sim = AirportSimulation(
            end_time=FINITE_HORIZON_TIME,
            sampling_rate=SAMPLING_RATE,
            type_simulation="finite"
        )

        replica_metrics = sim.run()
        all_metrics.append(replica_metrics)

        if remaining_replica != 0:
            current_seed = get_seed()
            seed_used.append(current_seed)

    print("Tutte le repliche finite.")
    for s in seed_used:
        print("Seed usato:", s)

    print("\nMetriche finali per ogni replica:\n")
    for idx, replica_metrics in enumerate(all_metrics):
        last_snapshot = replica_metrics[-1]

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


def infinite_horizon_run():
    current_seed = SEED
    seed_used.append(current_seed)
    plant_seeds(current_seed)

    sim = AirportSimulation(
        end_time=float('inf'),
        sampling_rate=BATCH_DIM,
        type_simulation="infinite",
        batch_num=BATCH_NUM
    )
    metrics = sim.run()

    print("\nBatch Means completati. Statistiche raccolte:")

    # Caso 1: metrics è un dizionario per pool
    if isinstance(metrics, dict):
        for pool_name, snapshots in metrics.items():
            print(f"\nPool: {pool_name}")
            aggregated = {
                "avg_utilization": [],
                "avg_waiting_time": [],
                "avg_response_time": [],
                "avg_queue_population": [],
                "avg_system_population": []
            }

            for snap in snapshots:
                for key in aggregated:
                    if key in snap and snap[key] is not None:
                        aggregated[key].append(snap[key])

            for key, values in aggregated.items():
                if values:
                    avg = sum(values) / len(values)
                    print(f"  {key}: {avg:.4f}")
                else:
                    print(f"  {key}: dati non disponibili")

    # Caso 2: metrics è una lista di snapshot globali
    elif isinstance(metrics, list):
        metrics = sorted(metrics, key=lambda x: x.get("time", 0.0))
        aggregated = {
            "avg_utilization": [],
            "avg_waiting_time": [],
            "avg_response_time": [],
            "avg_queue_population": [],
            "avg_system_population": []
        }

        for snap in metrics:
            for key in aggregated:
                if key in snap and snap[key] is not None:
                    aggregated[key].append(snap[key])

        print("\nMetriche globali:")
        for key, values in aggregated.items():
            if values:
                avg = sum(values) / len(values)
                print(f"  {key}: {avg:.4f}")
            else:
                print(f"  {key}: dati non disponibili")

    else:
        print("Formato dati non riconosciuto")

    return metrics


if __name__ == '__main__':

    if INFINITE_HORIZON:
        infinite_horizon_run()

    elif FINITE_HORIZON:
        finite_horizon_run()

    else:
        raise ValueError("Errore: Nessun orizzonte di simulazione selezionato")