import math

# --- Statistiche base ---
def mean(data):
    return sum(data) / len(data) if data else 0.0

def stddev(data):
    n = len(data)
    if n < 2:
        return 0.0
    m = mean(data)
    return math.sqrt(sum((x - m) ** 2 for x in data) / (n - 1))

def get_t_score(df, confidence=0.95):
    t_table_95 = {
        1: 12.71, 2: 4.30, 3: 3.18, 4: 2.78, 5: 2.57, 6: 2.45,
        7: 2.36, 8: 2.31, 9: 2.26, 10: 2.23, 11: 2.20, 12: 2.18,
        13: 2.16, 14: 2.14, 15: 2.13, 16: 2.12, 17: 2.11, 18: 2.10,
        19: 2.09, 20: 2.09, 25: 2.06, 30: 2.04, 40: 2.02, 50: 2.01,
        60: 2.00, 80: 1.99, 100: 1.98, 1000: 1.96
    }
    if df >= 1000:
        return t_table_95[1000]
    available_dfs = sorted(t_table_95.keys())
    for d in available_dfs:
        if df <= d:
            return t_table_95[d]
    return t_table_95[available_dfs[-1]]

def confidence_interval(data, confidence=0.95):
    n = len(data)
    if n < 2:
        return mean(data), None, None
    m = mean(data)
    s = stddev(data)
    sem = s / math.sqrt(n)
    t = get_t_score(n - 1, confidence)
    h = t * sem
    return m, m - h, m + h

def autocorrelation_lag1(data):
    n = len(data)
    if n < 2:
        return 0.0
    mu = mean(data)
    num = sum((data[i] - mu) * (data[i - 1] - mu) for i in range(1, n))
    den = sum((x - mu) ** 2 for x in data)
    return num / den if den != 0 else 0.0

# --- Test di configurazioni b e k ---
def test_batch_configurations(
    data,
    b_candidates=[64, 128, 256, 512, 1024],
    k_min=10,
    max_autocorrelation=0.1,
    verbose=True
):
    total = len(data)
    if verbose:
        print(f"\nAnalisi configurazioni (b, k) per {total} dati raccolti\n")
    best_config = None
    valid_configs = []

    for b in b_candidates:
        if total % b != 0:
            if verbose:
                print(f"[b={b:4}] Ignorato perché {total} non è multiplo di {b}")
            continue
        k = total // b
        if k < k_min:
            if verbose:
                print(f"[b={b:4}, k={k:3}] Ignorato perché k < {k_min}")
            continue
        batches = [data[i * b:(i + 1) * b] for i in range(k)]
        batch_means = [mean(batch) for batch in batches]

        m, ci_low, ci_high = confidence_interval(batch_means)
        acf1 = autocorrelation_lag1(batch_means)

        if verbose:
            print(f"[b={b:4}, k={k:3}]  μ={m:.4f}  CI=({ci_low if ci_low else 'N/A'}, {ci_high if ci_high else 'N/A'})  ρ₁={acf1:.4f}")

            # Mostra i primi batch per debug
            print("   Primi 5 batch means:", ["{:.4f}".format(x) for x in batch_means[:5]])

        valid_configs.append({"b": b, "k": k, "acf1": acf1, "mean": m, "ci_low": ci_low, "ci_high": ci_high})

        if abs(acf1) < max_autocorrelation and best_config is None:
            best_config = {"b": b, "k": k, "acf1": acf1}

    if best_config is None and valid_configs:
        # Nessuna con autocorrelazione accettabile → prendi quella con autocorrelazione minore in valore assoluto
        best_config = min(valid_configs, key=lambda x: abs(x["acf1"]))

    if best_config:
        if verbose:
            print(f"\n✅ Configurazione suggerita: b={best_config['b']}, k={best_config['k']} (ρ₁={best_config['acf1']:.4f})\n")
    else:
        if verbose:
            print("\n⚠️ Nessuna configurazione trovata con autocorrelazione accettabile. Riprova con dati più lunghi.\n")

    return best_config
