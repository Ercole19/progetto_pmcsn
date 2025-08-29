from progetto_pmcsn.simulation_8 import AirportSimulation
from computeBatchAnalysis import *
from progetto_pmcsn.rng.rng import *

# === Parametri iniziali "di esplorazione" ===
SAMPLING_RATE = 64          # Ogni quanti job si campiona (b provvisorio)
BATCH_NUM = 2048             # Numero di batch provvisori (deve essere alto)
SEED = 123456789

def extract_metric(metrics, center_name, metric_name):
    data = [
        batch[metric_name]
        for batch in metrics.get(center_name, [])
        if isinstance(batch, dict)
           and metric_name in batch
           and batch[metric_name] is not None
    ]
    return data

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

    # === Estrai i dati della metrica da analizzare ===
    # Puoi scegliere: avg_response_time, avg_utilization, avg_waiting_time...
    data = extract_metric(metrics, "security_area", "avg_utilization")

    # === Stima migliore configurazione (b, k) ===
    suggested = test_batch_configurations(data, max_autocorrelation=0.1)

    # === Visualizza suggerimenti finali ===
    if suggested:
        print(f"➡️  Imposta nella simulazione: BATCH_DIM = {suggested['b']}, BATCH_NUM = {suggested['k']}")
    else:
        print("❌ Nessuna configurazione suggerita. Prova ad aumentare il numero di batch iniziali.")


