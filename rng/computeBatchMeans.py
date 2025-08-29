import math

# Calcolo manuale della media
def mean(data):
    return sum(data) / len(data)

# Calcolo della deviazione standard corretta (sample std)
def stddev(data):
    n = len(data)
    m = mean(data)
    return math.sqrt(sum((x - m) ** 2 for x in data) / (n - 1))

# Calcolo del t-score per intervallo di confidenza
# Valori comuni per 95% CI: df -> t
t_table_95 = {
    1: 12.71, 2: 4.30, 3: 3.18, 4: 2.78,
    5: 2.57, 6: 2.45, 7: 2.36, 8: 2.31,
    9: 2.26, 10: 2.23, 11: 2.20, 12: 2.18,
    13: 2.16, 14: 2.14, 15: 2.13, 16: 2.12,
    17: 2.11, 18: 2.10, 19: 2.09, 20: 2.09,
    25: 2.06, 30: 2.04, 40: 2.02, 50: 2.01,
    60: 2.00, 80: 1.99, 100: 1.98, 1000: 1.96
}

def get_t_score(df, confidence=0.95):
    if confidence != 0.95:
        raise ValueError("Solo il 95% è supportato in questa versione semplificata.")
    # Approssimazione per df grandi
    if df >= 1000:
        return t_table_95[1000]
    # Altrimenti cerca il valore più vicino
    available_dfs = sorted(t_table_95.keys())
    for d in available_dfs:
        if df <= d:
            return t_table_95[d]
    return t_table_95[available_dfs[-1]]

# Calcolo intervallo di confidenza
def confidence_interval(data, confidence=0.95):
    n = len(data)
    m = mean(data)
    s = stddev(data)
    sem = s / math.sqrt(n)
    t_score = get_t_score(n - 1, confidence)
    h = t_score * sem
    return m, m - h, m + h

# Funzione principale per stampare gli intervalli
def compute_batch_means_cis(metrics):
    metriche_da_controllare = [
        "avg_utilization",
        "avg_waiting_time",
        "avg_queue_population",
        "avg_response_time",
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
