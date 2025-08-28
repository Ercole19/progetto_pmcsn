import heapq
from collections import deque
from distributions.distributions import exponential, lognormal
from params import *
from rng.rng import *
from rng.computeBatchMeans import *

# -------------------- Server --------------------
class Server:
    def __init__(self, name, service_time_generator, debug=True):
        self.start_time = 0
        self.name = name
        self.service_time_generator = service_time_generator
        self.state = 0  # 0=free, 1=busy
        self.arrivals = []
        self.completed = []
        self.queue_waits = []
        self.response_times = []
        self.num_in_system = 0
        self.total_busy_time = 0.0
        self.debug = debug

    def reset_server(self):
        self.state = 0
        self.arrivals = []
        self.completed = []
        self.num_in_system = 0
        self.total_busy_time = 0.0
        self.start_time = 0.0
        self.queue_waits = []
        self.response_times = []

    def start_service(self, event, event_list, times, queue_time=0):
        self.state = 1
        service_time = max(1e-3, self.service_time_generator())
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
        self.completed.append(completion_time)
        self.num_in_system -= 1
        self.state = 0

        # 🔑 aggiorna busy time qui
        service_duration = completion_time - event.start_service_time
        self.total_busy_time += service_duration

        self.response_times.append(event.queue_time + event.service_time)

        if self.debug:
            print(f"t={completion_time:.2f} | DEPARTURE | {self.name} finished {event.op_index}")

        pool.start_next(event_list, times)

        next_center_name = getattr(event, "next_center", None)
        if next_center_name is not None:
            new_event = Event(completion_time, "A", next_center_name)
            heapq.heappush(event_list, (new_event.event_time, "A", new_event))

    def utilization(self, current_time):
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

# -------------------- Specialized Servers --------------------
class ClassicCheckInServer(Server):
    def __init__(self, name):
        super().__init__(name, lambda: exponential(180))

class BagDropCheckInServer(Server):
    def __init__(self, name):
        super().__init__(name, lambda: exponential(60))

class TurnstileServer(Server):
    def __init__(self, name):
        super().__init__(name, lambda: 3)

class SecurityCheckServer(Server):
    def __init__(self, name):
        super().__init__(name, lambda: exponential(60))


# -------------------- Server Pool --------------------
class ServerPool:
    def __init__(self, servers, debug=True):
        self.servers = servers
        self.queue = deque()  # shared queue for all servers in this pool
        self.debug = debug

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

    def avg_utilization(self, current_time):
        return sum(s.utilization(current_time) for s in self.servers) / len(self.servers)


# -------------------- Passenger & Event --------------------
class PassengerType:
    def __init__(self, name, server_pool, next_center=None):
        self.name = name
        self.server_pool = server_pool
        self.next_center = next_center

class Event:
    def __init__(self, event_time=0.0, event_type='A', op_index=None):
        self.event_time = event_time
        self.event_type = event_type
        self.op_index = op_index
        self.next_center = None
        self.exogenous = False
        self.arrival_time = None
        self.start_service_time = None
        self.service_time = None
        self.queue_time = None

class Times:
    def __init__(self):
        self.current = 0.0
        self.next = 0.0

# -------------------- Airport Simulation --------------------
class AirportSimulation:
    def __init__(self, end_time, sampling_rate, type_simulation, batch_num = 0):
        self.end_time = end_time
        self.sampling_rate = sampling_rate
        self.batch_num = batch_num
        self.processed_batch = 0
        self.type_simulation = type_simulation
        self.times = Times()
        self.event_list = []
        self.servers = []
        self.server_pools = {}
        self.completed_jobs = 0
        self.passenger_routing = {}
        self.metrics = {
            "business": [],
            "premium_economy": [],
            "economy": [],
            "flexi_plus": [],
            "self_bd": [],
            "bd": [],
            "fast_track_turnstile": [],
            "fast_track_security_area": [],
            "turnstiles": [],
            "security_area": [],
        }
        self.last_arrival_time = {}
        self.current_slot = None
        self.time_slots = [
            (0, 359*60          , "night"),
            (360*60, 539*60     , "morning"),
            (540*60, 719*60     , "late_morning"),
            (720*60, 899*60     , "early_afternoon"),
            (900*60, 1139*60    , "late_afternoon"),
            (1140*60, 1319*60   , "evening"),
            (1320*60, 1440*60   , "late_evening"),
        ]
        self.lambdas = {
            "business": LAMBDA_BC,
            "premium_economy": LAMBDA_PE,
            "economy": LAMBDA_ECO,
            "flexi_plus": LAMBDA_FP,
            "self_bd": LAMBDA_SBD,
            "bd": LAMBDA_BD,
            "turnstile_area": LAMBDA_4,
            "exogenous": LAMBDA_E,
            "fast_track_turnstile": LAMBDA_6,
            "security_area": LAMBDA_7,
            "fast_track_security_area": LAMBDA_6,
        }
        self.percent = {
            "night": 0.066,
            "morning": 0.165,
            "late_morning": 0.165,
            "early_afternoon": 0.165,
            "late_afternoon": 0.196,
            "evening": 0.165,
            "late_evening": 0.078
        }
        self.next_sampling = self.sampling_rate
        self.init_servers_and_pools()
        self.init_time_slot_events()

    def reset_sistem(self):
        for pool in self.server_pools.values():
            pool.reset_pool()
        self.completed_jobs = 0
        #self.metrics = []
        self.event_list.clear()
        self.times.current = 0
        self.times.next = 0.0

    # -------------------- Time slots --------------------
    def init_time_slot_events(self):
        for start, end, name in self.time_slots:
            if start <= self.end_time:
                heapq.heappush(self.event_list, (start, "H", name))
        self.update_current_slot(0)

    def update_current_slot(self, current_time):
        for start, end, name in self.time_slots:
            if start <= current_time < end:
                self.current_slot = name
                break
        print(f"  [TIME SLOT] Current time slot: {self.current_slot}")

    # -------------------- Servers & Pools --------------------
    def init_servers_and_pools(self):
        if self.type_simulation == "infinite":
            # Se è attiva la procedura Verify, consideriamo questa configurazione del sistema
            self.server_pools = {
                "business":                 ServerPool([ClassicCheckInServer("business_0")]),
                "premium_economy":          ServerPool([ClassicCheckInServer("premium_economy_0")]),
                "economy":                  ServerPool([ClassicCheckInServer(f"economy_{index}") for index in range(1)]),
                "flexi_plus":               ServerPool([ClassicCheckInServer("flexi_plus_0")]),
                "self_bd":                  ServerPool([BagDropCheckInServer(f"self_bd_{index}") for index in range(1)]),
                "bd":                       ServerPool([BagDropCheckInServer(f"bd_{index}") for index in range(1)]),
                "fast_track_turnstile":     ServerPool([TurnstileServer("fast_track_turnstile_0")]),
                "fast_track_security_area": ServerPool([SecurityCheckServer(f"fast_track_sec_{index}") for index in range(1)]),
                "turnstiles":               ServerPool([TurnstileServer(f"turnstile_{index}") for index in range(4)]),
                "security_area":            ServerPool([SecurityCheckServer(f"security_{index}") for index in range(2)])
            }

        else:
            self.server_pools = {
                "business":                 ServerPool([ClassicCheckInServer("business_0")]),
                "premium_economy":          ServerPool([ClassicCheckInServer("premium_economy_0")]),
                "economy":                  ServerPool([ClassicCheckInServer(f"economy_{index}") for index in range(3)]),
                "flexi_plus":               ServerPool([ClassicCheckInServer("flexi_plus_0")]),
                "self_bd":                  ServerPool([BagDropCheckInServer(f"self_bd_{index}") for index in range(2)]),
                "bd":                       ServerPool([BagDropCheckInServer(f"bd_{index}") for index in range(4)]),
                "fast_track_turnstile":     ServerPool([TurnstileServer("fast_track_turnstile_0")]),
                "fast_track_security_area": ServerPool([SecurityCheckServer(f"fast_track_sec_{index}") for index in range(2)]),
                "turnstiles":               ServerPool([TurnstileServer(f"turnstile_{index}") for index in range(4)]),
                "security_area":            ServerPool([SecurityCheckServer(f"security_{index}") for index in range(6)])
            }

        for pool in self.server_pools.values():
            self.servers.extend(pool.servers)

        self.passenger_routing = {
            "business":                 PassengerType("Business",           self.server_pools["business"],              next_center="fast_track_turnstile"),
            "premium_economy":          PassengerType("PremiumEconomy",     self.server_pools["premium_economy"],       next_center="turnstile_area"),
            "economy":                  PassengerType("Economy",            self.server_pools["economy"],               next_center="turnstile_area"),
            "flexi_plus":               PassengerType("FlexiPlus",          self.server_pools["flexi_plus"],            next_center="fast_track_turnstile"),
            "self_bd":                  PassengerType("SelfBD",             self.server_pools["self_bd"],               next_center="turnstile_area"),
            "bd":                       PassengerType("BD",                 self.server_pools["bd"],                    next_center="turnstile_area"),
            "fast_track_turnstile":     PassengerType("FastTrackTurnstile", self.server_pools["fast_track_turnstile"],  next_center="fast_track_security_area"),
            "fast_track_security_area": PassengerType("FastTrackSecurity",  self.server_pools["fast_track_security_area"]),
            "turnstile":                PassengerType("Turnstile",          self.server_pools["turnstiles"],            next_center="security_area"),
            "security_area":            PassengerType("Security",           self.server_pools["security_area"])
        }

    # -------------------- Interarrival --------------------
    def generate_interarrival_time(self, op_index):

        multiplier = None

        if self.type_simulation == "verify":
            slot_multiplier = {k: v / 1 for k, v in self.percent.items()}
            multiplier = slot_multiplier.get("late_afternoon")

        elif self.type_simulation == "finite" or self.type_simulation == "infinite":
            slot_multiplier = {k: v / 1 for k, v in self.percent.items()}
            multiplier = slot_multiplier.get("night")

        lambda_rescaled = self.lambdas[op_index] * multiplier
        return exponential(1 / lambda_rescaled)

    # -------------------- Arrival processing --------------------
    def process_arrival(self, event):
        op = event.op_index
        print(f"t={event.event_time:.2f} | ARRIVAL   | {op}")

        input_flow_zone_a = [
            "business",
            "premium_economy",
            "economy",
            "flexi_plus",
            "self_bd",
            "bd",
            "turnstile_area"
        ]
        if op in input_flow_zone_a:
            self.generate_new_arrival(op)

        if op == "turnstile_area":
            select_stream(20)
            r = random()
            fast_track_or_no = "fast" if r < 0.2 else "normal"

            if fast_track_or_no == "fast":
                pool = self.server_pools["fast_track_turnstile"]
                event.next_center = "fast_track_security_area"
                event.op_index = "fast_track_turnstile"
            else:
                pool = self.server_pools["turnstiles"]
                event.next_center = "security_area"
                event.op_index = "turnstile"

            print(f"  [ROUTING] {op} passenger → {fast_track_or_no} priority")
            pool.assign_event(event, self.event_list, self.times)
            return

        ptype = self.passenger_routing[op]
        pool = ptype.server_pool
        pool.assign_event(event, self.event_list, self.times)

        if ptype.next_center:
            event.next_center = ptype.next_center

    # -------------------- Generate new arrivals --------------------
    def generate_new_arrival(self, op_index=None):
        if op_index is None:
            select_stream(0)
            airline_type = "traditional" if random() < 0.2 else "lowcost"
            if airline_type == "traditional":
                select_stream(1)
                r = random()
                if r < 0.1: op_index = "business"
                elif r < 0.3: op_index = "premium_economy"
                elif r < 0.75: op_index = "economy"
                else: op_index = "turnstile_area"
            else:
                select_stream(2)
                r = random()
                if r < 0.7: op_index = "turnstile_area"
                else:
                    select_stream(3)
                    r2 = random()
                    if r2 < 0.05: op_index = "flexi_plus"
                    elif r2 < 0.15: op_index = "self_bd"
                    else: op_index = "bd"

        select_stream({
            "business": 10, "premium_economy": 11, "economy": 12,
            "flexi_plus": 13, "self_bd": 14, "bd": 15,
            "turnstile_area": 16
        }[op_index])
        interarrival = self.generate_interarrival_time(op_index)
        event_time = max(self.last_arrival_time.get(op_index, 0.0) + interarrival, self.times.next + interarrival)

        self.last_arrival_time[op_index] = event_time
        if event_time <= self.end_time:
            heapq.heappush(self.event_list, (event_time, "A", Event(event_time, "A", op_index)))
            print(f"  [SCHEDULE] New {op_index} at t={event_time:.2f}")

    # -------------------- Exogenous arrivals --------------------
    def generate_exogenous_arrival(self):
        select_stream(30)
        op_index = "exogenous"
        interarrival = self.generate_interarrival_time(op_index)
        event_time = max(self.last_arrival_time.get("exogenous", 0.0) + interarrival, self.times.next + interarrival)
        self.last_arrival_time["exogenous"] = event_time
        if event_time <= self.end_time:
            arrival_time = event_time + self.transit_time_exogenous()
            event = Event(arrival_time, "E", "turnstile_area")
            event.exogenous = True
            heapq.heappush(self.event_list, (arrival_time, "E", event))
            print(f"  [SCHEDULE] Exogenous B+C passenger at t={arrival_time:.2f} (generated at {event_time:.2f})")

    @staticmethod
    def transit_time_exogenous():
        return lognormal(5.1895, 0.08319)

    # -------------------- Process next event --------------------
    def process_next_event(self):
        if not self.event_list:
            return None, None

        item = heapq.heappop(self.event_list)

        if len(item) == 3:
            time_event, event_type, event = item
            server = None
        else:
            time_event, event_type, server, event = item

        self.times.next = time_event

        if event_type in ["A", "E"]:
            self.process_arrival(event)
        elif event_type == "C" and server is not None:
            ptype = self.passenger_routing.get(event.op_index)
            pool = ptype.server_pool if ptype else None
            server.handle_departure(event, self.event_list, pool=pool, times=self.times)
            if ptype and ptype.name == "Security" or ptype.name == "FastTrackSecurity":
                self.completed_jobs += 1
        elif event_type == "H":
            self.update_current_slot(time_event)
            print(f"t={self.times.next:.2f} | TIME SLOT CHANGE → {self.current_slot}")

        if event and self.times.next >= getattr(self, "next_sampling", 0) and self.type_simulation == "finite":
            self.collect_metrics()
            self.next_sampling = self.times.next + self.sampling_rate

        return event_type, event

    # -------------------- Metrics --------------------
    def collect_metrics(self):
        """
        Raccoglie snapshot e metriche aggregate per ogni pool (caso finito).
        Deve essere chiamato periodicamente durante la simulazione a tempo finito.
        """
        current_time = self.times.next

        for pool_name, pool in self.server_pools.items():
            queue_total = 0
            response_total = 0

            for s in pool.servers:
                queue_total += s.avg_wait_time()
                response_total += s.avg_response_time()

            avg_queue = queue_total / len(pool.servers)
            avg_resp = response_total / len(pool.servers)

            snapshot = {
                "time": current_time,
                "queue_length": len(pool.queue),
                "in_system": pool.total_in_system(),
                "avg_utilization": pool.avg_utilization(current_time),
                "avg_waiting_time": avg_queue,
                "avg_response_time": avg_resp,
            }

            self.metrics[pool_name].append(snapshot)

            print(
                f'[METRICS-FINITE] t={current_time:.2f} '
                f'Pool={pool_name} '
                f'Queue_len={snapshot["queue_length"]} '
                f'InSystem={snapshot["in_system"]} '
                f'Util={snapshot["avg_utilization"]:.2f} '
                f'Wait={snapshot["avg_waiting_time"]:.2f} '
                f'Resp={snapshot["avg_response_time"]:.2f}'
            )

    def collect_metrics_infinite(self):
        """
        Raccoglie snapshot e metriche aggregate per ogni pool.
        Deve essere chiamato periodicamente (a ogni evento o step).
        """
        current_time = self.times.next

        for pool_name, pool in self.server_pools.items():
            queue_total = 0
            response_total = 0

            for s in pool.servers:
                queue_total += s.avg_wait_time()
                response_total += s.avg_response_time()

            avg_queue = queue_total / len(pool.servers)
            avg_resp = response_total / len(pool.servers)

            if self.type_simulation == "verify":
                slot_multiplier = {k: v / 1 for k, v in self.percent.items()}
                multiplier = slot_multiplier.get("late_afternoon")

            else:
                slot_multiplier = {k: v / 1 for k, v in self.percent.items()}
                multiplier = slot_multiplier.get("night")

            if pool_name == "turnstiles" or pool_name == "fast_track_turnstile":
                lambda_to_choose = "turnstile_area"
                lambda_rescaled = self.lambdas[lambda_to_choose] * multiplier
            else : lambda_rescaled = self.lambdas[pool_name] * multiplier


            snapshot = {
                "time": current_time,
                "queue_length": len(pool.queue),
                "in_system": pool.total_in_system(),
                "avg_utilization": pool.avg_utilization(current_time),
                "avg_waiting_time": avg_queue,
                "avg_response_time": avg_resp,
                "avg_queue_population": lambda_rescaled * avg_queue,
                "avg_system_population": lambda_rescaled * avg_resp,
            }

            self.metrics[pool_name].append(snapshot)


            print(
                f'[METRICS] t={current_time:.2f} '
                f'Pool={pool_name} '
                f'Queue_len={snapshot['queue_length']} '
                f'InSystem={snapshot['in_system']} '
                f'Util={snapshot['avg_utilization']:.2f} '
                f'Wait={snapshot['avg_waiting_time']:.2f} '
                f'Resp={snapshot['avg_response_time']:.2f}'
                f'Avg_queue_population={snapshot['avg_queue_population']:.2f} '
                f'Avg_system_population={snapshot['avg_system_population']:.2f} '
                )

    # -------------------- Run --------------------
    def run(self):
        #self.next_sampling = self.sampling_rate da levare se tutto funziona
        #self.generate_new_arrival()
        #self.generate_exogenous_arrival()

        self.last_arrival_time = {k: 0.0 for k in
                                  ["business", "premium_economy", "economy", "flexi_plus", "self_bd", "bd",
                                   "turnstile_area", "exogenous"]}

        # Genera un arrivo iniziale per ogni centro (tipo di passeggero)
        for op_index in ["business", "premium_economy", "economy", "flexi_plus", "self_bd", "bd", "turnstile_area"]:
            self.generate_new_arrival(op_index)
        self.generate_exogenous_arrival()

        if self.type_simulation == "finite":
            while self.event_list and self.times.next <= self.end_time:
                event_type, event = self.process_next_event()
                if event and getattr(event, "exogenous", False):
                    self.generate_exogenous_arrival()

        elif self.type_simulation == "verify":
            while self.event_list and self.times.next <= self.end_time:
                event_type, event = self.process_next_event()
                if event and getattr(event, "exogenous", False):
                    self.generate_exogenous_arrival()

        else :
            while self.processed_batch < self.batch_num:
                #if VERBOSE: print_status()
                event_type, event = self.process_next_event()
                if event and getattr(event, "exogenous", False):
                    self.generate_exogenous_arrival()

                if self.completed_jobs == self.sampling_rate and self.completed_jobs != 0:
                    self.collect_metrics_infinite()
                    self.processed_batch += 1
                    #self.next_sampling = self.completed_jobs + self.sampling_rate
                    print(f"Batch {self.processed_batch}/{self.batch_num}")

                    self.reset_sistem()  # ⬅️ Resetta tutto

                    self.last_arrival_time = {k: 0.0 for k in [
                        "business", "premium_economy", "economy", "flexi_plus", "self_bd", "bd",
                        "turnstile_area", "exogenous"
                    ]}
                    # Riavvia il sistema con nuovi arrivi
                    for op_index in ["business", "premium_economy", "economy", "flexi_plus", "self_bd", "bd",
                                     "turnstile_area"]:
                        self.generate_new_arrival(op_index)
                    self.generate_exogenous_arrival()
            for key in self.metrics.keys():
                print(f"Computing area {key}")
                compute_batch_means_cis(self.metrics[key])
        return self.metrics