from params import *
from entity import *
from distributions.distributions import *
from rng.rng import selectStream
from utils import *

def init(end_time, type_simulation, sampling_rate=0):
    global times, event_list, area_list, accumSum, servers_state, num_client_in_service, queues_num, queues, \
        num_client_in_system, num_client_served, num_sampling, CLOSE_THE_DOOR_TIME, FINITE, INFINITE, SAMPLING_RATE
    CLOSE_THE_DOOR_TIME = end_time

    # Inizializzazione delle variabili globali
    times = Times()  # Tempi di sistema
    event_list = EventList()  # Lista degli eventi del sistema
    area_list = [Area() for _ in range(QUEUES_NUM_AREA_CHECK_IN + QUEUES_NUM_AREA_NORMALE + QUEUES_NUM_AREA_FAST_TRACK)]  # Lista delle aree di interesse per il calcolo delle prestazioni
    accumSum = [AccumSum() for _ in range(SERVER_NUM_AREA_CHECK_IN + SERVER_NUM_AREA_NORMALE + SERVER_NUM_AREA_FAST_TRACK)]  # Accumulatore delle somme per il calcolo delle prestazioni

    # ------------------------------ Variabili per definire lo stato del sistema ------------------------------

    servers_state = [0 for _ in range(SERVER_NUM_AREA_CHECK_IN + SERVER_NUM_AREA_NORMALE + SERVER_NUM_AREA_FAST_TRACK)]  # Array binario: 0 = IDLE, 1 = BUSY
    num_client_in_service = [0 for _ in range(QUEUES_NUM_AREA_CHECK_IN + QUEUES_NUM_AREA_NORMALE + QUEUES_NUM_AREA_FAST_TRACK)]  # Numero di clienti in servizio.
    queues_num = [0 for _ in range(QUEUES_NUM_AREA_CHECK_IN + QUEUES_NUM_AREA_NORMALE + QUEUES_NUM_AREA_FAST_TRACK)]  # Numero di clienti in coda per ogni tipo
    time_slot = 0

    # ------------------------------ Variabili utilizzate  ------------------------------

    queues = [[] for _ in range(QUEUES_NUM_AREA_CHECK_IN + QUEUES_NUM_AREA_NORMALE + QUEUES_NUM_AREA_FAST_TRACK)]  # Una lista di eventi per ogni coda
    num_client_in_system = [0 for _ in range(QUEUES_NUM_AREA_CHECK_IN + QUEUES_NUM_AREA_NORMALE + QUEUES_NUM_AREA_FAST_TRACK)]  # Numero di clienti al momento nel sistema per ogni tipo
    num_client_served = [0 for _ in range(QUEUES_NUM_AREA_CHECK_IN + QUEUES_NUM_AREA_NORMALE + QUEUES_NUM_AREA_FAST_TRACK)]  # Numero di clienti serviti per ogni tipo
    num_sampling = 0

    if type_simulation == "finite":
        FINITE = True
    elif type_simulation == "infinite":
        INFINITE = True
    SAMPLING_RATE = sampling_rate  # Ogni quanto campionare





def print_status():
    """
    Stampa lo stato del sistema
    :return:
    """
    formatted_queues = format_queues(queues)  # Usa la funzione di supporto per formattare le code
    print(f"\n{'=' * 30}\n"
          f"Searching for the next event...\n"
          f"System Timer: {times.current:.4f} | "
          f"Clients in system: {num_client_in_system} | "
          f"Clients in service: {num_client_in_service} | "
          f"Clients served: {num_client_served} | "
          f"Queues: {formatted_queues}\n{'=' * 30}")



def get_next_event():
    """
    Trova l'evento più imminente nella lista degli eventi (Arrivo, Completamento, Sampling)
    :return: Restituisce l'evento più imminente e l'indice del server se esso è un completamento
    """
    event = Event()
    server_index_completed = None

    # Cerca l'evento di arrivo più imminente
    # (Tutti i valori devono essere maggiori di current, altrimenti problema serio)
    for i in range(QUEUES_NUM_AREA_CHECK_IN + QUEUES_NUM_AREA_NORMALE + QUEUES_NUM_AREA_FAST_TRACK):
        if event_list.arrivals[i] is not None:
            if ((event.event_time is None or event_list.arrivals[i] < event.event_time)
                    and event_list.arrivals[i] > times.current):
                event.event_time = event_list.arrivals[i]
                event.op_index = i
                event.event_type = 'A'

    # Cerca l'evento completamento più imminente (Se il valore è 0, non va considerato)
    for i in range(SERVER_NUM_AREA_CHECK_IN + SERVER_NUM_AREA_NORMALE + SERVER_NUM_AREA_FAST_TRACK):
        if event_list.completed[i].event_time is not None and event_list.completed[i].event_time != 0:
            if (event.event_time is None or event_list.completed[i].event_time < event.event_time) and \
                    event_list.completed[i].event_time > times.current:
                event.event_time = event_list.completed[i].event_time
                event.op_index = event_list.completed[i].op_index
                event.serving_time = event_list.completed[i].serving_time
                event.event_type = 'C'
                server_index_completed = i

    # Verifico imminenza dell'evento di sampling
    if event_list.sampling is not None:
        if event.event_time is not None and event_list.sampling < event.event_time:
            event.event_time = event_list.sampling
            event.event_type = 'S'
            event.op_index = None
        elif event.event_time is None:
            event.event_time = event_list.sampling
            event.event_type = 'S'
            event.op_index = None

    if event.event_time is None:
        return None, None

    return event, server_index_completed



def process_next_event():
    """
    Processa l'evento più imminente e aggiorna lo stato del sistema
    :return:
    """
    # 1) Trova evento più imminente
    event, server_index_completed = get_next_event()
    if event is None:
        return
    times.next = event.event_time

    if VERBOSE:
        print(f"\n>>> Next Event: {event.event_type} | Client Type: {event.op_index}, "
              f"Time: {event.event_time:.4f}")

    update_area(area_list)      # Aggiorna le aree di interesse

    # 2) Processa l'evento e aggiorna lo stato del sistema
    if event.event_type == 'A':  # Se l'evento è un arrivo
        process_arrival(event)  # Processa l'arrivo
        times.last[event.op_index] = event.event_time
        generate_new_arrival(event.op_index)  # Genera nuovo evento di arrivo
    elif event.event_type == 'C':  # Se l'evento è un completamento
        process_completion(event, server_index_completed)

    times.current = times.next  # Aggiorno il timer di sistema

    if event.event_type == 'S':  # Se l'evento è di campionamento
        process_sampling()
        generate_sampling_event()




def update_area(area_list):
    """
    Aggiorna le aree di interesse per il calcolo delle prestazioni
    :param area_list:
    :return:
    """
    for i in range(QUEUES_NUM_AREA_CHECK_IN + QUEUES_NUM_AREA_NORMALE + QUEUES_NUM_AREA_FAST_TRACK):
        if num_client_in_system[i] > 0:
            area_list[i].customers += (times.next - times.current) * num_client_in_system[i]
            area_list[i].service += (times.next - times.current) * num_client_in_service[i]
            area_list[i].queue += (times.next - times.current) * (len(queues[i]))
            # Non usiamo num_client_in_system[i] - num_client_in_service[i] perché non è un valore attendibile
            # nella fase di verifica del sistema
            # area_list[i].queue += (times.next - times.current) * (num_client_in_system[i] - num_client_in_service[i])



def start_simulation(end_time, type_simulation, sampling_rate=0, batch_num=0):
    """
    Inizializza la simulazione e gestisce il loop principale
    :return:
    """
    global num_sampling, BATCH_NUM
    BATCH_NUM = batch_num

    init(end_time, type_simulation, sampling_rate, batch_num)


    # Inizializza i tempi di arrivo per ogni tipo di evento
    event_list.arrivals = [0 for _ in range(QUEUES_NUM_AREA_CHECK_IN + QUEUES_NUM_AREA_NORMALE + QUEUES_NUM_AREA_FAST_TRACK)]
    for i in range(QUEUES_NUM_AREA_CHECK_IN + QUEUES_NUM_AREA_NORMALE + QUEUES_NUM_AREA_FAST_TRACK):
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



def generate_interarrival_time(index_type):
    """
    Genera il tempo di arrivo per un cliente di tipo index_type
    :param index_type: Indice del tipo di cliente, rappresenta la tipologia di coda in cui andrà
    :return: Il tempo di interarrivo del cliente
    """
    selectStream(index_type)
    '''if IMPROVED_SIM and LOCKER:
        if index_type == SR_DIFF_STREAM:
            if  ((1 - P_LOCKER) * P_SR * P_DIFF * (1 - P_ON) * LAMBDA) == 0:
                return float('inf')
            return Exponential(1 / ((1 - P_LOCKER) * P_SR * P_DIFF * (1 - P_ON) * LAMBDA))
        elif index_type == SR_STREAM:
            if  ((1 - P_LOCKER) * P_SR * (1 - P_DIFF) * (1 - P_ON) * LAMBDA) == 0:
                return float('inf')
            return Exponential(1 / ((1 - P_LOCKER) * P_SR * (1 - P_DIFF) * (1 - P_ON) * LAMBDA))
        elif index_type == LOCKER_STREAM:
            return Exponential(1 / (P_LOCKER * P_SR * (1 - P_ON) * LAMBDA))'''

    if index_type == CLASSIC_ONLINE_STREAM:
        return Exponential(1 / (P_OC_ON * P_ON * LAMBDA))
    elif index_type == CLASSIC_DIFF_STREAM:
        return Exponential(1 / (P_OC * P_DIFF * (1 - P_ON) * LAMBDA))
    elif index_type == CLASSIC_STREAM:
        return Exponential(1 / (P_OC * (1 - P_DIFF) * (1 - P_ON) * LAMBDA))
    elif index_type == SR_ONLINE_STREAM:
        if (P_SR_ON * P_ON * LAMBDA) == 0:
            return float('inf')
        return Exponential(1 / (P_SR_ON * P_ON * LAMBDA))
    elif index_type == SR_DIFF_STREAM:
        return Exponential(1 / (P_SR * P_DIFF * (1 - P_ON) * LAMBDA))
    elif index_type == SR_STREAM:
        return Exponential(1 / (P_SR * (1 - P_DIFF) * (1 - P_ON) * LAMBDA))
    elif index_type == ATM_DIFF_STREAM:
        return Exponential(1 / (P_ATM * P_DIFF * (1 - P_ON) * LAMBDA))
    elif index_type == ATM_STREAM:
        return Exponential(1 / (P_ATM * (1 - P_DIFF) * (1 - P_ON) * LAMBDA))
    else:
        raise ValueError(f'Tipo di cliente ({index_type}) non valido in GetArrival')






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

