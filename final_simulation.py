from utils.computeBatchMeans import *
from lambda_scaler import *
from entity.Pool import *
from entity.Server import *

# -------------------- Airport Simulation --------------------
class AirportSimulation:
    def __init__(self, end_time, sampling_rate, type_simulation, model_type, batch_num = 0):
        self.end_time = end_time
        self.metrics = {}
        self.sampling_rate = sampling_rate
        self.batch_num = batch_num
        self.processed_batch = 0
        self.type_simulation = type_simulation
        self.model_type = model_type
        self.times = Times()
        self.event_list = []
        self.servers = []
        self.server_pools = {}
        self.completed_jobs = 0
        self.arrivals = 0
        self.passenger_routing = {}
        self.counter = 0
        self.last_arrival_time = {}
        self.current_slot = None
        self.time_slots = [
            (0, 359*60 + 59         , "night"),
            (360*60, 539*60 +59     , "morning"),
            (540*60, 719*60   +59  , "late_morning"),
            (720*60, 899*60  +59   , "early_afternoon"),
            (900*60, 1139*60 +59   , "late_afternoon"),
            (1140*60, 1319*60 +59  , "evening"),
            (1320*60, 1440*60 +59  , "late_evening"),
         ]
        self.lambdas = {}
        self.next_sampling = self.sampling_rate
        self.init_servers_and_pools()
        self.init_time_slot_events()

    def reset_sistem(self):
        for pool in self.server_pools.values():
            pool.reset_pool()
        self.completed_jobs = 0
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
                lambda_scaler = LambdaScaler()
                if self.type_simulation == "finite":
                    self.lambdas = lambda_scaler.return_new_lambdas(self.current_slot, self.model_type)
                else : self.lambdas = lambda_scaler.return_new_lambdas("late_afternoon", self.model_type)
                break
        print(f"  [TIME SLOT] Current time slot: {self.current_slot}")

    # -------------------- Servers & Pools --------------------
    def init_servers_and_pools(self):

        match self.model_type:
            case "full_improved":
                self.server_pools = {
                        "business":                 MultiServerSingleQueuePool([ClassicCheckInServer(f"business_{index}") for index in range(1)]),
                        "premium_economy":          MultiServerSingleQueuePool([ClassicCheckInServer(f"premium_economy_{index}") for index in range(1)]),
                        "economy":                  MultiServerSingleQueuePool([ClassicCheckInServer(f"economy_{index}") for index in range(5)]),
                        "flexi_plus":               MultiServerSingleQueuePool([ClassicCheckInServer(f"flexi_plus_{index}") for index in range(1)]),
                        "self_bd":                  MultiServerSingleQueuePool([BagDropCheckInServer(f"self_bd_{index}") for index in range(1)]),
                        "bd":                       MultiServerSingleQueuePool([BagDropCheckInServer(f"bd_{index}") for index in range(5)]),
                        "fast_track_turnstile":     MultiServerSingleQueuePool([TurnstileServer("fast_track_turnstile_0")]),
                        "fast_track_security_area": MultiServerMultiQueuesPool([SecurityCheckServer(f"fast_track_sec_{index}") for index in range(3)]),
                        "fast_track_security_fast": MultiServerMultiQueuesPool([FastSecurityCheckServer(f"fast_track_sec_fast_{index}") for index in range(1)]),
                        "turnstiles":               MultiServerMultiQueuesPool([TurnstileServer(f"turnstile_{index}") for index in range(4)]),
                        "security_area":            MultiServerMultiQueuesPool([SecurityCheckServer(f"security_{index}") for index in range(9)]),
                        "security_area_fast":       MultiServerMultiQueuesPool([FastSecurityCheckServer(f"security_fast_{index}") for index in range(3)]),
                        "tsa_security":             MultiServerMultiQueuesPool([TsaSecurityCheckServer(f"tsa_security_{index}") for index in range(7)]),
                        "tsa_turnstile":            MultiServerMultiQueuesPool([TsaTurnstile(f"tsa_turnstile_{index}") for index in range(2)]),

                }

                self.passenger_routing = {
                    "business": PassengerType("Business", self.server_pools["business"], next_center="fast_track_turnstile"),
                    "premium_economy": PassengerType("PremiumEconomy", self.server_pools["premium_economy"], next_center="turnstile_area"),
                    "economy": PassengerType("Economy", self.server_pools["economy"], next_center="turnstile_area"),
                    "flexi_plus": PassengerType("FlexiPlus", self.server_pools["flexi_plus"], next_center="fast_track_turnstile"),
                    "self_bd": PassengerType("SelfBD", self.server_pools["self_bd"], next_center="turnstile_area"),
                    "bd": PassengerType("BD", self.server_pools["bd"], next_center="turnstile_area"),
                    "fast_track_turnstile": PassengerType("FastTrackTurnstile", self.server_pools["fast_track_turnstile"], next_center="fast_track_security_area"),
                    "fast_track_security_area": PassengerType("FastTrackSecurity", self.server_pools["fast_track_security_area"]),
                    "fast_track_security_fast": PassengerType("FastTrackSecurity", self.server_pools["fast_track_security_fast"]),
                    "turnstile": PassengerType("Turnstile", self.server_pools["turnstiles"], next_center="security_area"),
                    "security_area": PassengerType("Security", self.server_pools["security_area"]),
                    "security_area_fast": PassengerType("Security", self.server_pools["security_area_fast"]),
                    "tsa_security": PassengerType("Security", self.server_pools["tsa_security"]),
                    "tsa_turnstile": PassengerType("Turnstile", self.server_pools["tsa_turnstile"], next_center="tsa_security"),
                }

            case "semi_improved":
                self.server_pools = {
                    "business": MultiServerSingleQueuePool([ClassicCheckInServer(f"business_{index}") for index in range(1)]),
                    "premium_economy": MultiServerSingleQueuePool([ClassicCheckInServer(f"premium_economy_{index}") for index in range(1)]),
                    "economy": MultiServerSingleQueuePool([ClassicCheckInServer(f"economy_{index}") for index in range(5)]),
                    "flexi_plus": MultiServerSingleQueuePool([ClassicCheckInServer(f"flexi_plus_{index}") for index in range(1)]),
                    "self_bd": MultiServerSingleQueuePool([BagDropCheckInServer(f"self_bd_{index}") for index in range(1)]),
                    "bd": MultiServerSingleQueuePool([BagDropCheckInServer(f"bd_{index}") for index in range(5)]),
                    "fast_track_turnstile": MultiServerSingleQueuePool([TurnstileServer("fast_track_turnstile_0")]),
                    "fast_track_security_area": MultiServerMultiQueuesPool([SecurityCheckServer(f"fast_track_sec_{index}") for index in range(4)]),
                    "turnstiles": MultiServerMultiQueuesPool([TurnstileServer(f"turnstile_{index}") for index in range(4)]),
                    "security_area": MultiServerMultiQueuesPool([SecurityCheckServer(f"security_{index}") for index in range(12)]),
                    "tsa_security": MultiServerMultiQueuesPool([TsaSecurityCheckServer(f"tsa_security_{index}") for index in range(7)]),
                    "tsa_turnstile": MultiServerMultiQueuesPool([TsaTurnstile(f"tsa_turnstile_{index}") for index in range(2)]),

                }

                self.passenger_routing = {
                    "business": PassengerType("Business", self.server_pools["business"], next_center="fast_track_turnstile"),
                    "premium_economy": PassengerType("PremiumEconomy", self.server_pools["premium_economy"], next_center="turnstile_area"),
                    "economy": PassengerType("Economy", self.server_pools["economy"], next_center="turnstile_area"),
                    "flexi_plus": PassengerType("FlexiPlus", self.server_pools["flexi_plus"],  next_center="fast_track_turnstile"),
                    "self_bd": PassengerType("SelfBD", self.server_pools["self_bd"], next_center="turnstile_area"),
                    "bd": PassengerType("BD", self.server_pools["bd"], next_center="turnstile_area"),
                    "fast_track_turnstile": PassengerType("FastTrackTurnstile", self.server_pools["fast_track_turnstile"], next_center="fast_track_security_area"),
                    "fast_track_security_area": PassengerType("FastTrackSecurity", self.server_pools["fast_track_security_area"]),
                    "turnstile": PassengerType("Turnstile", self.server_pools["turnstiles"], next_center="security_area"),
                    "security_area": PassengerType("Security", self.server_pools["security_area"]),
                    "tsa_security": PassengerType("Security", self.server_pools["tsa_security"]),
                    "tsa_turnstile": PassengerType("Turnstile", self.server_pools["tsa_turnstile"], next_center="tsa_security"),
                }
            case _:
                self.server_pools = {
                    "business": MultiServerSingleQueuePool([ClassicCheckInServer(f"business_{index}") for index in range(1)]),
                    "premium_economy": MultiServerSingleQueuePool([ClassicCheckInServer(f"premium_economy_{index}") for index in range(1)]),
                    "economy": MultiServerSingleQueuePool([ClassicCheckInServer(f"economy_{index}") for index in range(5)]),
                    "flexi_plus": MultiServerSingleQueuePool([ClassicCheckInServer(f"flexi_plus_{index}") for index in range(1)]),
                    "self_bd": MultiServerSingleQueuePool([BagDropCheckInServer(f"self_bd_{index}") for index in range(1)]),
                    "bd": MultiServerSingleQueuePool([BagDropCheckInServer(f"bd_{index}") for index in range(5)]),
                    "fast_track_turnstile": MultiServerSingleQueuePool([TurnstileServer("fast_track_turnstile_0")]),
                    "fast_track_security_area": MultiServerSingleQueuePool([SecurityCheckServer(f"fast_track_sec_{index}") for index in range(2)]),
                    "turnstiles": MultiServerSingleQueuePool([TurnstileServer(f"turnstile_{index}") for index in range(4)]),
                    "security_area": MultiServerSingleQueuePool([SecurityCheckServer(f"security_{index}") for index in range(7)])
                }

                self.passenger_routing = {
                    "business": PassengerType("Business", self.server_pools["business"], next_center="fast_track_turnstile"),
                    "premium_economy": PassengerType("PremiumEconomy", self.server_pools["premium_economy"], next_center="turnstile_area"),
                    "economy": PassengerType("Economy", self.server_pools["economy"], next_center="turnstile_area"),
                    "flexi_plus": PassengerType("FlexiPlus", self.server_pools["flexi_plus"], next_center="fast_track_turnstile"),
                    "self_bd": PassengerType("SelfBD", self.server_pools["self_bd"], next_center="turnstile_area"),
                    "bd": PassengerType("BD", self.server_pools["bd"], next_center="turnstile_area"),
                    "fast_track_turnstile": PassengerType("FastTrackTurnstile", self.server_pools["fast_track_turnstile"], next_center="fast_track_security_area"),
                    "fast_track_security_area": PassengerType("FastTrackSecurity", self.server_pools["fast_track_security_area"]),
                    "turnstile": PassengerType("Turnstile", self.server_pools["turnstiles"], next_center="security_area"),
                    "security_area": PassengerType("Security", self.server_pools["security_area"])
                }

        for pool_name, pool in self.server_pools.items():
            if isinstance(pool, MultiServerSingleQueuePool):
                # pool con più code → una sola lista di metriche
                self.metrics[pool_name] = []
            else:
                # pool con più server distinti → un dict per server
                self.metrics[pool_name] = {srv.name: [] for srv in pool.servers}

    # -------------------- Interarrival --------------------
    def generate_interarrival_time(self, op_index):
      lambda_rescaled = self.lambdas[op_index]
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
            "turnstile_area_external"
        ]
        if op in input_flow_zone_a:
            self.arrivals += 1
            self.generate_new_arrival(op)

        if op == "turnstile_area_external":
            op = "turnstile_area"


        if op == "turnstile_area_exogenous":
            op = "turnstile_area"
            self.arrivals += 1

        if op == "turnstile_area":
            if self.model_type != "no_improved":
                select_stream(20)
                r1 = random()
                # tre scelte con probabilità 15%, 15%, 70%
                if r1 < 0.10:
                    choice = "fast"
                elif r1 < 0.45:  # da 0.15 a 0.30 = 15%
                    choice = "tsa"
                else:  # da 0.30 a 1.00 = 70%
                    choice = "normal"
            else:
                select_stream(92)
                r2 = random()
                choice = "fast" if r2 < 0.2 else "normal"

            if choice == "fast":
                pool = self.server_pools["fast_track_turnstile"]
                if event.check_in_done:
                    event.next_center = "fast_track_security_fast"
                else:
                    event.next_center = "fast_track_security_area"
                event.op_index = "fast_track_turnstile"

            elif choice == "tsa":
                pool = self.server_pools["tsa_turnstile"]
                event.next_center = "tsa_security"

                event.op_index = "tsa_turnstile"

            else:  # normal
                pool = self.server_pools["turnstiles"]
                if event.check_in_done:
                    event.next_center = "security_area_fast"
                else:
                    event.next_center = "security_area"
                event.op_index = "turnstile"

            print(f"  [ROUTING] {op} passenger → {choice} priority")
            pool.assign_event(event, self.event_list, self.times)
            return

        if op == "bd":
            ptype = self.passenger_routing[op]
            pool = ptype.server_pool
            new_ptype = self.passenger_routing["self_bd"]
            new_pool = new_ptype.server_pool
            if len(pool.queue) > 15 and len(new_pool.queue) < 10:
                new_pool.assign_event(event, self.event_list, self.times)
            else :
                pool.assign_event(event, self.event_list, self.times)
            if ptype.next_center:
                event.next_center = ptype.next_center

        elif op == "economy":
            ptype = self.passenger_routing[op]
            pool = ptype.server_pool
            new_ptype = self.passenger_routing["premium_economy"]
            new_pool = new_ptype.server_pool
            if len(pool.queue) > 10 and  len(new_pool.queue) < 5:
                new_pool.assign_event(event, self.event_list, self.times)
            else :
                pool.assign_event(event, self.event_list, self.times)

            if ptype.next_center:
                event.next_center = ptype.next_center
        else :
            ptype = self.passenger_routing[op]
            pool = ptype.server_pool
            pool.assign_event(event, self.event_list, self.times)
            if ptype.next_center:
                event.next_center = ptype.next_center

    # -------------------- Generate new arrivals --------------------
    def generate_new_arrival(self, op_index=None):
        select_stream({
            "business": 10, "premium_economy": 11, "economy": 12,
            "flexi_plus": 13, "self_bd": 14, "bd": 15,
            "turnstile_area_external": 16
        }[op_index])
        interarrival = self.generate_interarrival_time(op_index)
        #event_time = max(self.last_arrival_time.get(op_index, 0.0) + interarrival, self.times.next + interarrival)

        event_time = self.last_arrival_time[op_index] + interarrival

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
            arrival_time = event_time
            event = Event(arrival_time, "E", "turnstile_area_exogenous")

            if self.model_type == "full_improved":
                select_stream(77)
                r = random()
                delay_or_no = "check" if r < 0.5 else "no_check"
                if delay_or_no == "check":
                    event.check_in_done = True
                else:
                    event.check_in_done = False
            event.exogenous = True
            heapq.heappush(self.event_list, (arrival_time, "E", event))
            print(f"  [SCHEDULE] Exogenous B+C passenger at t={arrival_time:.2f} (generated at {event_time:.2f})")

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
            if event.event_type == "E":
                event.exogenous = False
            ptype = self.passenger_routing.get(event.op_index)
            pool = ptype.server_pool if ptype else None
            server.handle_departure(event, self.event_list, model_type = self.model_type, pool=pool, times=self.times)
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
        current_time = self.times.next

        for pool_name, pool in self.server_pools.items():
            if pool_name in ("turnstiles", "fast_track_turnstile"):
                lambda_rescaled = self.lambdas["turnstile_area_external"]
            else:
                lambda_rescaled = self.lambdas[pool_name]

            # ------------------- Metrics per server (solo tornelli) -------------------
            if isinstance(pool, MultiServerMultiQueuesPool):
                for s in pool.servers:
                    completed = len(s.completed)
                    if completed > 0:
                        avg_queue_s = s.avg_wait_time()
                        avg_service_s = (s.total_busy_time / completed) if completed > 0 else 0.0
                        avg_resp_s = avg_queue_s + avg_service_s
                        snapshot_s = {
                            "time": current_time,
                            "queue_length": len(s.queue),
                            "in_system": s.num_in_system,
                            "avg_utilization": s.utilization(current_time),
                            "avg_waiting_time": avg_queue_s,
                            "avg_response_time": avg_resp_s,
                            "avg_queue_population": lambda_rescaled * avg_queue_s,
                            "avg_system_population": lambda_rescaled * avg_resp_s,
                            "passengers_completed": self.completed_jobs,
                        }
                        self.metrics[pool_name][s.name].append(snapshot_s)

                        print(
                            f"  [SERVER METRICS] t={current_time:.2f} "
                            f"Server={s.name} "
                            f"InSystem={snapshot_s['in_system']} "
                            f"Util={snapshot_s['avg_utilization']:.2f} "
                            f"Wait={snapshot_s['avg_waiting_time']:.2f} "
                            f"Resp={snapshot_s['avg_response_time']:.2f} "
                           f"Avg_queue_population={snapshot_s['avg_queue_population']:.2f} "
                            f"Avg_system_population={snapshot_s['avg_system_population']:.2f}"
                        )
            else :
                # ------------------- Pool metrics -------------------
                queue_total = 0.0
                service_total = 0.0
                total_completed = 0

                for s in pool.servers:
                    completed = len(s.completed)
                    total_completed += completed
                    queue_total += s.avg_wait_time()
                    service_total += (s.total_busy_time / completed) if completed > 0 else 0.0

                if total_completed > 0:

                    avg_queue = queue_total
                    avg_service = service_total / len(pool.servers) if len(pool.servers) > 0 else 0
                    avg_resp = avg_queue + avg_service

                    # --- Lunghezza coda ---
                    if isinstance(pool, MultiServerMultiQueuesPool):
                        queue_len = sum(len(s.queue) for s in pool.servers)
                    else:
                        queue_len = len(pool.queue)

                    # --- Snapshot pool ---
                    snapshot = {
                        "time": current_time,
                        "queue_length": queue_len,
                        "in_system": pool.total_in_system(),
                        "avg_utilization": pool.avg_utilization(current_time),
                        "avg_waiting_time": avg_queue,
                        "avg_response_time": avg_resp,
                        "avg_queue_population": lambda_rescaled * avg_queue,
                        "avg_system_population": lambda_rescaled * avg_resp,
                        "passengers_completed": self.completed_jobs,
                    }

                    self.metrics[pool_name].append(snapshot)

                    print(
                        f"[METRICS] t={current_time:.2f} "
                        f"Pool={pool_name} "
                        f"InSystem={snapshot['in_system']} "
                        f"Util={snapshot['avg_utilization']:.2f} "
                        f"Wait={snapshot['avg_waiting_time']:.2f} "
                        f"Resp={snapshot['avg_response_time']:.2f} "
                        f"Avg_queue_population={snapshot['avg_queue_population']:.2f} "
                        f"Avg_system_population={snapshot['avg_system_population']:.2f}"
                    )

    # -------------------- Run --------------------
    def run(self):
        _, _ = self.process_next_event()

        self.last_arrival_time = {k: 0.0 for k in
                                  ["business", "premium_economy", "economy", "flexi_plus", "self_bd", "bd",
                                   "turnstile_area_external", "exogenous"]}

        # Genera un arrivo iniziale per ogni centro (tipo di passeggero)
        for op_index in ["business", "premium_economy", "economy", "flexi_plus", "self_bd", "bd", "turnstile_area_external"]:
            self.generate_new_arrival(op_index)
        self.generate_exogenous_arrival()

        if self.type_simulation == "finite":
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
                    self.collect_metrics()
                    self.processed_batch += 1
                    #self.next_sampling = self.completed_jobs + self.sampling_rate
                    print(f"Batch {self.processed_batch}/{self.batch_num}")

                    self.reset_sistem()  # Resetta tutto

                    self.last_arrival_time = {k: 0.0 for k in [
                        "business", "premium_economy", "economy", "flexi_plus", "self_bd", "bd",
                        "turnstile_area_external", "exogenous"
                    ]}
                    # Riavvia il sistema con nuovi arrivi
                    for op_index in ["business", "premium_economy", "economy", "flexi_plus", "self_bd", "bd",
                                     "turnstile_area_external"]:
                        self.generate_new_arrival(op_index)
                    self.generate_exogenous_arrival()
            for key, value in self.metrics.items():
                print(f"\nComputing area {key}")
                if key != "daily_percentile_90_wait":
                    # Se è un pool "normale" (lista di snapshot)
                    if isinstance(value, list):
                        compute_batch_means_cis(value)

                    # Se è un pool con server separati (es. turnstiles)
                    elif isinstance(value, dict):
                        for server_name, server_metrics in value.items():
                            print(f"  Server: {server_name}")
                            compute_batch_means_cis(server_metrics)

        total_queues = []
        for pool_name, pool in self.server_pools.items():
            for server in pool.servers:
                if isinstance(server, ClassicCheckInServer) or isinstance(server, BagDropCheckInServer) :
                    total_queues += server.queue_waits
        percentile_90 = np.percentile(total_queues, 90)
        print(f"90th percentile global: {percentile_90:.2f} seconds")
        self.metrics["daily_percentile_90_wait"] = percentile_90
        return self.metrics