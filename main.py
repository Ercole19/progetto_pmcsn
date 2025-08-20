##from Simulation import start_simulation
import os
from params import * #parametri del modello
from rng.rng import *
from simulation import *

# Parametri della simulazione
SEED = 123456789 #123456789 #1359796324 # 1161688905
seed_used = [SEED]  # Lista dei seed utilizzati per ogni replica della simulazione (Per ripetibilità)

# ---------------- INFINITE HORIZON SIMULATION ----------------
INFINITE_HORIZON = True
BATCH_DIM = 512  # Campionamento ogni 512 job (b)
BATCH_NUM = 1024  # Numero di batch da eseguire (k)
INFINITE_HORIZON_TIME = BATCH_DIM * BATCH_NUM

# ---------------- FINITE HORIZON SIMULATION ----------------
FINITE_HORIZON = not INFINITE_HORIZON  # Se non è una simulazione a orizzonte finito allora è a orizzonte infinito
FINITE_HORIZON_TIME = 4 * 60  # 4 ore di simulazione
REPLICATION_NUM = 1000
SAMPLING_RATE = 1  # Tempo di campionamento per le statistiche


def finite_horizon_run():
    end_simulation_time = FINITE_HORIZON_TIME

    # Inizializzazione file csv per le statistiche (Crea il file se non esiste o cancella contenuto se esiste)
    directory = DIRECTORY_FINITE_H
    files = [CSV_UTILIZATION, CSV_DELAY, CSV_WAITING_TIME, CSV_END_WORK_TIME_FINITE]

    # Cancella il contenuto del file
    for file in files:
        with open(os.path.join(directory, file), 'w') as f:
            f.write('')

    plantSeeds(SEED)
    # Esecuzione delle repliche
    for ri in range(REPLICATION_NUM):
        print("Starting replica for finite-horizon simulation, seed: ", get_seed())
        # plantSeeds(getSeed())
        start_simulation(end_simulation_time, "finite", SAMPLING_RATE)
        selectStream(0)
        seed_used.append(getSeed())
        print(f"Simulation {ri + 1}/{REPLICATION_NUM} ending seed: {getSeed()}")
    print("fine simulazione")
    for s in seed_used:
        print(s)


def infinite_horizon_run():
    return


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Inizializza il generatore di numeri casuali
    plant_seeds(SEED)

    if INFINITE_HORIZON:
        infinite_horizon_run()

    elif FINITE_HORIZON:
        finite_horizon_run()
    else:
        raise ValueError("Errore: Nessun orizzonte di simulazione selezionato")


