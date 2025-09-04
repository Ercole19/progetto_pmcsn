from collections import deque
from abc import ABC, abstractmethod

class ServerPool(ABC):
    def __init__(self, servers, debug=True):
        self.servers = servers
        self.debug = debug

    @abstractmethod
    def reset_pool(self):
        pass

    @abstractmethod
    def assign_event(self, event, event_list, times):
        pass

    @abstractmethod
    def start_next(self, *args, **kwargs):
        pass

    @abstractmethod
    def total_in_system(self):
        pass

    def avg_utilization(self, current_time):
        return sum(s.utilization(current_time) for s in self.servers) / len(self.servers)


class MultiServerSingleQueuePool(ServerPool):
    def __init__(self, servers):
        super().__init__(servers)  # 30 s - 5 min
        self.queue = deque()

    def reset_pool(self):
        self.queue.clear()
        for s in self.servers:
            s.reset_server()

    def assign_event(self, event, event_list, times):
        free_server = next((s for s in self.servers if s.state == 0), None)
        if free_server:
            event.arrival_time = times.next
            free_server.start_service(event, event_list, times)
            free_server.arrivals.append(times.next)
            free_server.num_in_system += 1
        else:
            event.arrival_time = times.next
            self.queue.append(event)
            if self.debug:
                print(f"  [QUEUEING] No free server in pool for '{event.op_index}' → queued (length={len(self.queue)})")

    def start_next(self, event_list, times):
        while self.queue:
            free_server = next((s for s in self.servers if s.state == 0), None)
            if not free_server:
                break
            next_event = self.queue.popleft()


            queue_time = times.next - next_event.arrival_time


            free_server.start_service(next_event, event_list, times, queue_time)
            next_event.event_time = times.next
            free_server.arrivals.append(next_event.event_time)
            free_server.num_in_system += 1
    def total_in_system(self):
        return sum(s.num_in_system for s in self.servers) + len(self.queue)



class MultiServerMultiQueuesPool(ServerPool):
    def __init__(self, servers):
        super().__init__(servers)  # 30 s - 5 min

    def reset_pool(self):
        for s in self.servers:
            s.reset_server()
            s.queue.clear()

    def assign_event(self, event, event_list, times):
        # 1. Controlla se c’è un tornello libero
        for s in self.servers:
            if s.state == 0:
                event.arrival_time = times.next
                s.start_service(event, event_list, times)
                s.arrivals.append(times.next)
                s.num_in_system += 1
                return

        # 2. Tutti occupati → scegli quello con la coda più corta
        chosen = min(self.servers, key=lambda s: len(s.queue))
        event.arrival_time = times.next
        chosen.queue.append(event)
        if self.debug:
            print(f"  [QUEUEING] '{event.op_index}' → {chosen.name} (queue len={len(chosen.queue)})")

    def start_next(self, server, event_list, times):
        """Chiamato quando un tornello finisce il servizio"""
        if server.queue:
            next_event = server.queue.popleft()
            queue_time = times.next - next_event.arrival_time
            server.start_service(next_event, event_list, times, queue_time)
            next_event.event_time = times.next
            server.arrivals.append(next_event.event_time)
            server.num_in_system += 1

    def total_in_system(self):
        return sum(s.num_in_system + len(s.queue) for s in self.servers)

    def avg_utilization(self, current_time):
        return sum(s.utilization(current_time) for s in self.servers) / len(self.servers)