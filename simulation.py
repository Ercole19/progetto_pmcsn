from params import *
from entity import *

def init(end_time, type_simulation, sampling_rate=0):
    global times, event_list, area_list, accumSum, servers_state, num_client_in_service, queues_num, queues, \
        num_client_in_system, num_client_served, num_sampling, CLOSE_THE_DOOR_TIME, FINITE, INFINITE, SAMPLING_RATE
    CLOSE_THE_DOOR_TIME = end_time

    # Inizializzazione delle variabili globali
    times = Times()  # Tempi di sistema
    event_list = EventList()  # Lista degli eventi del sistema
    area_list = [Area() for _ in range(QUEUES_NUM)]  # Lista delle aree di interesse per il calcolo delle prestazioni
    accumSum = [AccumSum() for _ in range(SERVER_NUM)]  # Accumulatore delle somme per il calcolo delle prestazioni

    # ------------------------------ Variabili per definire lo stato del sistema ------------------------------

    servers_state = [0 for _ in range(SERVER_NUM)]  # Array binario: 0 = IDLE, 1 = BUSY
    num_client_in_service = [0 for _ in range(QUEUES_NUM)]  # Numero di clienti in servizio.
    queues_num = [0 for _ in range(QUEUES_NUM)]  # Numero di clienti in coda per ogni tipo

    # ------------------------------ Variabili utilizzate  ------------------------------

    queues = [[] for _ in range(QUEUES_NUM)]  # Una lista di eventi per ogni coda
    num_client_in_system = [0 for _ in range(QUEUES_NUM)]  # Numero di clienti al momento nel sistema per ogni tipo
    num_client_served = [0 for _ in range(QUEUES_NUM)]  # Numero di clienti serviti per ogni tipo
    num_sampling = 0

    if type_simulation == "finite":
        FINITE = True
    elif type_simulation == "infinite":
        INFINITE = True
    SAMPLING_RATE = sampling_rate  # Ogni quanto campionare


def start_simulation(end_time, type_simulation, sampling_rate=0, batch_num=0):
    """
    Inizializza la simulazione e gestisce il loop principale
    :return:
    """
    global num_sampling, BATCH_NUM
    BATCH_NUM = batch_num

    init(end_time, type_simulation, sampling_rate=0, batch_num=0)


    # Inizializza i tempi di arrivo per ogni tipo di evento
    event_list.arrivals = [0 for _ in range(QUEUES_NUM)]
    for i in range(QUEUES_NUM):
        generate_new_arrival(i)

    if FINITE:
        event_list.sampling = SAMPLING_RATE     # Inizializza il tempo di campionamento
        while times.current < CLOSE_THE_DOOR_TIME or sum(num_client_in_system) != 0:
            if VERBOSE: print_status()
            process_next_event()  # Processa l'evento più imminente

    elif INFINITE:
        next_job_sampling = SAMPLING_RATE
        while batch_stats.num_batch < batch_num:
            if VERBOSE: print_status()

            process_next_event()  # Processa l'evento più imminente
            if sum(num_client_served) == next_job_sampling and sum(num_client_served) != 0:
                next_job_sampling += SAMPLING_RATE
                process_sampling()
                print(f"Batch {batch_stats.num_batch}/{batch_num}")

    # ------------------ Condizione di terminazione raggiunta --------------------
    # Print delle statistiche finali
    if VERBOSE:
        print("last completion: ", times.current, "\nTempo Totale", format_time(times.current))
        print("num sampling: ", num_sampling)

    if FINITE:
        if not SAVE_SAMPLING: save_stats_finite()
        if VERBOSE: print_final_stats()



def generate_new_arrival(queue_index):
    """
    Genera un nuovo arrivo per il tipo di coda specificato
    :param queue_index: Indice della coda per cui generare un nuovo arrivo
    :return: None
    """

    # TODO
    # p_loss = calculate_p_loss()
    # if random() < p_loss:
    #  return

    """current_time = times.next

    stop = True
    while(stop):
        p_loss = calculate_p_loss()
        if random() < p_loss:
            stop = False
            break"""

    new_time = generate_interarrival_time(queue_index) + times.next  # last[queue_index]
    if new_time <= CLOSE_THE_DOOR_TIME:
        event_list.arrivals[queue_index] = new_time
    else:
        times.last[queue_index] = times.next  # Memorizziamo l'ultimo arrivo
        event_list.arrivals[queue_index] = None