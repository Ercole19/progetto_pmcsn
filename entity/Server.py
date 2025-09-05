import heapq
from abc import ABC, abstractmethod
from entity.Pool import MultiServerMultiQueuesPool
from entity.Entity import *
from utils.utils import truncate_lognormal
from collections import deque


class Server(ABC):
    def __init__(self, name, debug=True):
        self.start_time = 0
        self.name = name
        self.state = 0  # 0=free, 1=busy
        self.arrivals = []
        self.completed = []
        self.queue_waits = []
        self.response_times = []
        self.num_in_system = 0
        self.total_busy_time = 0.0
        self.debug = debug
        self.last_event_time = 0.0   #traccia l'ultimo istante in cui ho aggiornato il busy time

    def reset_server(self):
        self.state = 0
        self.arrivals = []
        self.completed = []
        self.num_in_system = 0
        self.total_busy_time = 0.0
        self.start_time = 0.0
        self.queue_waits = []
        self.response_times = []
        self.last_event_time = 0.0

    def update_busy_time(self, current_time):
        """Aggiorna il busy time fino al current_time"""
        if self.state == 1:  # se era occupato fino a ora
            self.total_busy_time += current_time - self.last_event_time
        self.last_event_time = current_time

    def start_service(self, event, event_list, times, queue_time=0):
        # aggiorna busy time prima di cambiare stato
        self.update_busy_time(times.next)
        self.state = 1

        service_time = max(1e-3, self.get_service())
        self.start_time = times.next
        event.start_service_time = self.start_time
        event.service_time = service_time
        event.queue_time = queue_time
        self.queue_waits.append(queue_time)

        if self.debug:
            print(f"t={self.start_time:.2f} | START | {self.name} serving {event.op_index} "
                  f"(completion at {self.start_time + service_time:.2f})")

        heapq.heappush(event_list, (self.start_time + service_time, "C", self, event))

    def handle_departure(self, event, event_list, pool=None, times=None):
        completion_time = times.next

        # aggiorna busy time prima di liberare il server
        self.update_busy_time(completion_time)

        self.completed.append(completion_time)
        self.num_in_system -= 1
        self.state = 0

        self.response_times.append(event.queue_time + event.service_time)

        if self.debug:
            print(f"t={completion_time:.2f} | DEPARTURE | {self.name} finished {event.op_index}")

        if isinstance(pool, MultiServerMultiQueuesPool):
            # this is a turnstile pool
            pool.start_next(self, event_list, times)
        else:
            pool.start_next(event_list, times)


        next_center_name = getattr(event, "next_center", None)
        if next_center_name is not None:
            new_event = Event(completion_time, "A", next_center_name)
            #new_event.check_in_done = True
            heapq.heappush(event_list, (new_event.event_time, "A", new_event))

    def utilization(self, current_time):
        #prima di calcolare, aggiorna il busy time fino a current_time
        self.update_busy_time(current_time)
        return self.total_busy_time / max(1e-9, current_time)


    def avg_wait_time(self):
        queue_total = sum(qt for qt in self.queue_waits)
        if len(self.queue_waits) > 0:
            return queue_total / len(self.queue_waits)
        else : return 0

    def avg_response_time(self):
        resp_total = sum(qt for qt in self.response_times)
        if len(self.response_times) > 0:
            return resp_total / len(self.response_times)
        else:
            return 0

    @abstractmethod
    def get_service(self):
        pass


class ClassicCheckInServer(Server):
    def __init__(self, name):
        super().__init__(name)
    def get_service(self):
        return truncate_lognormal(5.1895, 0.05, 40, 250)

class BagDropCheckInServer(Server):
    def __init__(self, name):
        super().__init__(name)
    def get_service(self):
        return truncate_lognormal(4.5, 0.15, 40, 140)

class TurnstileServer(Server):
    def __init__(self, name):
        super().__init__(name)  # costante
        self.queue = deque()
    def get_service(self):
        return 5


class SecurityCheckServer(Server):
    def __init__(self, name):
        super().__init__(name)  # 30 s - 5 min
        self.queue = deque()
    def get_service(self):
        return truncate_lognormal(4.09, 0.091, 30, 150)

class TsaSecurityCheckServer(Server):
    def __init__(self, name):
        super().__init__(name)  # 30 s - 5 min
        self.queue = deque()
    def get_service(self):
        return truncate_lognormal(3.7, 0.1, 15, 60)  # Media ≈ 40s

class FastSecurityCheckServer(Server):
    def __init__(self, name):
        super().__init__(name)  # target ≈ 30 s
        self.queue = deque()
    def get_service(self):
        # lognormal con media ≈ 30 secondi (senza troncamento)
        return truncate_lognormal(3.40, 0.10, 15, 60)

class TsaTurnstile(Server):
    def __init__(self, name):
        super().__init__(name)  # 30 s - 5 min
        self.queue = deque()
    def get_service(self):
        return 10


class TsaSecurity(Server):
    def __init__(self, name):
        super().__init__(name)  # 30 s - 5 min
        self.queue = deque()

    def get_service(self):
        return truncate_lognormal(4.09, 0.091, 30, 150)


# -------------------- Specialized Servers --------------------
"""class ClassicCheckInServer(Server):
    def __init__(self, name):
        super().__init__(name, lambda: exponential(180))

class BagDropCheckInServer(Server):
    def __init__(self, name):
        super().__init__(name, lambda: exponential(90))

class TurnstileServer(Server):
    def __init__(self, name):
        super().__init__(name, lambda: exponential(5))
        self.queue = deque()

class SecurityCheckServer(Server):
    def __init__(self, name):
        super().__init__(name, lambda: exponential(60))
        self.passenger_exit = 0
"""