from progetto_pmcsn.simulation_8 import AirportSimulation
from computeBatchAnalysis import *
from progetto_pmcsn.rng.rng import *

# === Parametri iniziali "di esplorazione" ===
SAMPLING_RATE = 256          # Ogni quanti job si campiona (b provvisorio)
BATCH_NUM = 8192             # Numero di batch provvisori (deve essere alto)
SEED = 123456789

def extract_all_metrics(metrics, metric_names):
    data_dict = {metric: [] for metric in metric_names}
    for metric_name in metric_names:
        for center_name, center_batches in metrics.items():
            for batch in center_batches:
                if isinstance(batch, dict) and metric_name in batch and batch[metric_name] is not None:
                    data_dict[metric_name].append(batch[metric_name])
    return data_dict



if __name__ == '__main__':

    plant_seeds(SEED)

    # === Avvia simulazione iniziale ===
    sim = AirportSimulation(
        end_time=float('inf'),
        sampling_rate=SAMPLING_RATE,
        type_simulation="infinite",
        batch_num=BATCH_NUM
    )

    print("Esecuzione simulazione preliminare...")
    metrics = sim.run()
    print("Simulazione completata.")

    metrics_to_analyze = [
        "avg_utilization",
        "avg_waiting_time",
        "avg_response_time",
        "avg_queue_population",
        "avg_system_population"
    ]

    data_dict = extract_all_metrics(metrics, metrics_to_analyze)
    suggested = test_batch_configurations_multiple_metrics(data_dict)

    # === Visualizza suggerimenti finali ===
    if suggested:
        print(f" -->  Imposta nella simulazione: BATCH_DIM = {suggested['b']}, BATCH_NUM = {suggested['k']}")
    else:
        print(" Nessuna configurazione suggerita. Prova ad aumentare il numero di batch iniziali.")


