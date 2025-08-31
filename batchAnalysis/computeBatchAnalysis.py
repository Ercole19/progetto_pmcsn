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

def test_batch_configurations_multiple_metrics(
    data_dict,
    b_candidates=[64, 128, 256, 512, 1024, 2048, 4096],
    k_min=5,
    acf_weight=1.0,
    ci_weight=1.0,
    penalty_factor=10.0,
    verbose=True
):
    valid_configs = []

    total = len(next(iter(data_dict.values())))  # assume tutte le metriche hanno stessa lunghezza

    for b in b_candidates:
        if total % b != 0:
            continue  # salta i b non divisori

        k = total // b
        if k < k_min:
            continue  # ignora k troppo piccoli

        config_metrics = {}
        total_score = 0.0
        valid = True

        for metric_name, data in data_dict.items():
            batches = [data[i * b:(i + 1) * b] for i in range(k)]
            batch_means = [mean(batch) for batch in batches]

            m, ci_low, ci_high = confidence_interval(batch_means)
            acf1 = autocorrelation_lag1(batch_means)

            if ci_low is None or ci_high is None:
                valid = False
                break

            ci_range = ci_high - ci_low
            raw_score = acf_weight * abs(acf1) + ci_weight * ci_range
            penalty = 1 + (penalty_factor / k)
            metric_score = raw_score * penalty
            total_score += metric_score

            config_metrics[metric_name] = {
                "mean": m,
                "ci_low": ci_low,
                "ci_high": ci_high,
                "acf1": acf1,
                "score": metric_score
            }

        if valid:
            avg_score = total_score / len(data_dict)
            valid_configs.append({
                "b": b,
                "k": k,
                "score": avg_score,
                "metrics": config_metrics
            })

    if not valid_configs:
        if verbose:
            print("❌ Nessuna configurazione valida trovata.")
        return None

    best_config = min(valid_configs, key=lambda x: x["score"])

    if verbose:
        print("\n✅ Configurazione ottimale trovata:")
        print(f"   b = {best_config['b']}, k = {best_config['k']}, score medio = {best_config['score']:.6f}")
        for name, stats in best_config["metrics"].items():
            print(f"   ➤ {name:22s} ρ₁ = {stats['acf1']:.4f}  CI = ({stats['ci_low']:.4f}, {stats['ci_high']:.4f})  score = {stats['score']:.6f}")

    return {
        "b": best_config["b"],
        "k": best_config["k"]
    }
