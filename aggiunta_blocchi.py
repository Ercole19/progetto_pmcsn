def run(self):
    self.next_sampling = self.sampling_rate
    self.last_arrival_time = {k: 0.0 for k in
                              ["business", "premium_economy", "economy", "flexi_plus", "self_bd", "bd",
                               "turnstile_area", "exogenous"]}

    self.batch_metrics = []  # 🔹 Qui salviamo le metriche batch
    self.completed_jobs = 0  # 🔹 Numero di completamenti nel batch corrente
    self.processed_batch = 0  # 🔹 Batch processati

    # Genera un arrivo iniziale per ogni centro
    for op_index in ["business", "premium_economy", "economy", "flexi_plus", "self_bd", "bd", "turnstile_area"]:
        self.generate_new_arrival(op_index)
    self.generate_exogenous_arrival()

    # 🔁 Simulazione a orizzonte infinito
    while self.processed_batch < self.batch_num:
        event_type, event = self.process_next_event()
        if event and getattr(event, "exogenous", False):
            self.generate_exogenous_arrival()

        if self.completed_jobs >= self.sampling_rate:
            self.collect_metrics()
            self.batch_metrics.append(self.metrics[-1])  # 🔹 Salva ultimo snapshot come batch
            self.processed_batch += 1
            print(f"[BATCH] → Batch {self.processed_batch}/{self.batch_num} completato a t={self.times.next:.2f}")

            # 🔁 Reset per il batch successivo
            self.completed_jobs = 0
            self.next_sampling = self.sampling_rate
            # opzionale: azzera i busy_time dei server se vuoi batch disgiunti
            for s in self.servers:
                s.total_busy_time = 0.0

    return self.batch_metrics  # 🔹 Ritorna solo le metriche di batch



# DOPO la simulazione
sim = AirportSimulation(
    end_time=float('inf'),  # orizzonte infinito
    sampling_rate=500,      # 500 passeggeri per batch
    type_simulation="infinite",
    batch_num=20            # 20 batch
)

batch_results = sim.run()

# Calcolo media + intervallo di confidenza
import numpy as np
from scipy import stats

utilizations = [b["global"]["avg_utilization"] for b in batch_results]
mean_util = np.mean(utilizations)
std_util = np.std(utilizations, ddof=1)
conf_int = stats.t.interval(0.95, len(utilizations)-1, loc=mean_util, scale=std_util / np.sqrt(len(utilizations)))

print(f"\nUtilizzazione media: {mean_util:.4f}")
print(f"95% CI: ({conf_int[0]:.4f}, {conf_int[1]:.4f})")

# analisi risultati per tutti gli indicatori
import numpy as np
from scipy import stats

def analyze_batch_results(batch_results):
    """
    Analizza le metriche batch e stampa media, std e intervallo di confidenza per ciascun indicatore globale.
    """
    if not batch_results:
        print("Nessun batch disponibile.")
        return

    # Estrai metriche globali da ciascun batch
    metrics_by_key = {
        "avg_utilization": [],
        "avg_queue_length": [],
        "total_in_system": [],
        "passengers_completed": []
    }

    for batch in batch_results:
        for key in metrics_by_key:
            metrics_by_key[key].append(batch["global"][key])

    print(f"\n📊 Risultati su {len(batch_results)} batch:\n")

    for key, values in metrics_by_key.items():
        arr = np.array(values)
        mean = np.mean(arr)
        std = np.std(arr, ddof=1)
        conf_int = stats.t.interval(0.95, len(arr) - 1, loc=mean, scale=std / np.sqrt(len(arr)))
        half_width = (conf_int[1] - conf_int[0]) / 2

        print(f"🔹 {key}:")
        print(f"    → Media                = {mean:.4f}")
        print(f"    → Deviazione standard = {std:.4f}")
        print(f"    → 95% CI               = ({conf_int[0]:.4f}, {conf_int[1]:.4f})")
        print(f"    → Half-width (±)       = {half_width:.4f}")
        print("-" * 60)

#come usarla
analyze_batch_results(batch_results)


# Autocorrelazione
import matplotlib.pyplot as plt
import statsmodels.api as sm

def check_autocorrelation(data, variable):
    y = [batch["global"][variable] for batch in data]
    sm.graphics.tsa.plot_acf(y, lags=10)
    plt.title(f"Autocorrelazione dei batch: {variable}")
    plt.show()

check_autocorrelation(batch_results, "avg_queue_length")


#verifica convergenza della media
def plot_cumulative_means(data, variable):
    y = [batch["global"][variable] for batch in data]
    cum_means = [np.mean(y[:i]) for i in range(1, len(y)+1)]
    plt.plot(cum_means)
    plt.title(f"Media cumulativa di {variable}")
    plt.xlabel("Numero batch")
    plt.ylabel("Media cumulativa")
    plt.grid(True)
    plt.show()

