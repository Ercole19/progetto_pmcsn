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
        self.check_in_done = False


# -------------------- Passenger & Event --------------------
class PassengerType:
    def __init__(self, name, server_pool, next_center=None):
        self.name = name
        self.server_pool = server_pool
        self.next_center = next_center

class Times:
    def __init__(self):
        self.current = 0.0
        self.next = 0.0