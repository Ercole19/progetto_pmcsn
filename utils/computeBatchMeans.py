import numpy as np
from scipy import stats

def confidence_interval(data, confidence=0.95):
    n = len(data)
    mean = np.mean(data)
    sem = stats.sem(data)
    h = sem * stats.t.ppf((1 + confidence) / 2., n - 1)
    return mean, mean - h, mean + h

def compute_batch_means_cis(metrics):
    metriche_da_controllare = [
        "avg_utilization",
        "avg_queue_population",
        "avg_response_time",
        "avg_waiting_time",
        "avg_system_population",
    ]

    print("\n--- Intervalli di Confidenza (95%) per le metriche ---\n")

    for metrica in metriche_da_controllare:
        valori = [m[metrica] for m in metrics if metrica in m and m[metrica] is not None]

        if len(valori) < 2:
            print(f"Non ci sono abbastanza dati per calcolare l'IC per '{metrica}'.")
            continue

        media, ci_low, ci_high = confidence_interval(valori)
        print(f"{metrica}: {media:.4f} (95% CI: {ci_low:.4f} - {ci_high:.4f})")