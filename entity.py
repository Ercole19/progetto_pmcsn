from distributions.distributions import *
from params import *

class Times:
    def __init__(self):
        self.current = 0  # System clock - Avanzamento del tempo solo all'occorrenza di un next event
        self.next = 0  # Occurrence of the next event
        self.last = [0 for _ in range(QUEUES_NUM_AREA_CHECK_IN + QUEUES_NUM_AREA_NORMALE + QUEUES_NUM_AREA_FAST_TRACK)]  # Last arrival time for each flow - NUMBER_OF_QUEUES elements


"""class EventList:
    def __init__(self):
        self.arrivals = []  # Arrival events list, each element is a type of operation
        self.completed = [Event('C') for _ in range(SERVER_NUM_AREA_CHECK_IN + SERVER_NUM_AREA_NORMALE + SERVER_NUM_AREA_FAST_TRACK)]  # Completed events list
        self.sampling = None  # Sampling event"""


class Event:
    def __init__(self, event_type=None):
        self.event_time = None          # Event time
        self.event_type = event_type    # Tipo di evento (Completamento, Arrivo, Cambiamento fascia oraria)
        self.op_index = None            # Operation Index - Tipo di operazione - Da 0 a 7
        self.serving_time = None        # Tempo di servizio


# Struttura dati per mantenere le aree per il calcolo delle medie
class Area:
    def __init__(self):
        self.passengers = 0  # Clienti nel sistema [Area unità di misura: (total passengers) * time]
        self.queue = 0      # Clienti in coda queues [Area unità di misura: (customers in queue) * time]
        self.service = 0    # Clienti in servizio [Area unità di misura: (customers in service) * time]


class AccumSum:
    def __init__(self):
        # accumulated sums of
        self.service = 0          #  Tempo di servizio accumulato
        self.served = 0           #  Numero clienti serviti



import heapq
import random

class Server:
    def __init__(self):
        """
        :param server_id: identificativo del server
        :param service_time_generator: funzione che genera il tempo di servizio
        """
        self.arrivals = []         # lista timestamps arrivi
        self.completed = []        # lista timestamps completamenti
        self.state = 0             # 0 = libero, 1 = occupato
        self.queue = []            # coda dei job (FIFO)
        self.num_in_system = 0     # clienti totali in questo server
        self.total_busy_time = 0.0
        self.last_event_time = 0.0

    def update_busy_time(self, current_time):
        """Aggiorna la statistica del tempo occupato."""
        if self.state == 1:
            self.total_busy_time += (current_time - self.last_event_time)
        self.last_event_time = current_time

    """def handle_arrival(self, event, event_list):
    
        Gestisce un arrivo:
        - se libero → parte subito il servizio
        - se occupato → va in coda
        
        self.arrivals.append(event.event_time)
        self.num_in_system += 1
        self.update_busy_time(event.event_time)

        if self.state == 0:  # server libero
            self.start_service(event, event_list)
        else:
            self.queue.append(event)

    def start_service(self, event, event_list):
        Inizia un servizio e schedula il completamento.
        self.state = 1
        service_time = self.service_time_generator()
        completion_time = event.event_time + service_time
        heapq.heappush(event_list, (completion_time, "C", self.id, event))
        # NB: l'evento originale viene passato per tener traccia del cliente

    def handle_departure(self, event, event_list):
        
        Gestisce un completamento:
        - libera il server
        - se la coda non è vuota, prende il prossimo
        
        self.completed.append(event.event_time)
        self.num_in_system -= 1
        self.update_busy_time(event.event_time)

        if self.queue:  # c'è qualcuno in attesa
            next_event = self.queue.pop(0)
            self.start_service(next_event, event_list)
        else:
            self.state = 0  # diventa libero"""

    def utilization(self, current_time):
        """Ritorna il grado di utilizzo del server (ρ)."""
        total_time = max(1e-9, current_time)  # evita divisione per 0
        return self.total_busy_time / total_time

    def avg_system_time(self):
        """Tempo medio speso da un cliente nel sistema (approssimato)."""
        if not self.completed:
            return 0
        total_time = sum(c - a for a, c in zip(self.arrivals, self.completed))
        return total_time / len(self.completed)

    def queue_length(self):
        """Ritorna la lunghezza attuale della coda."""
        return len(self.queue)

    def getServices(self):
        """Numero totale di clienti serviti finora."""
        return len(self.completed)


class classic_check_in_server(Server):
    def __init__(self):
        super().__init__()
    def get_service(self):
        return lognormal(1.0849, 0.1655)

class bag_drop_check_in_server(Server):
    def __init__(self):
        super().__init__()
    def get_service(self):
        return lognormal(-0.0303, 0.2462)


class turnel_server(Server):
    def __init__(self):
        super().__init__()
    def get_service(self):
        return 3

class security_checks__server(Server):
    def __init__(self):
        super().__init__()
    def get_service(self):
        return lognormal(1.3726, 0.1655)
