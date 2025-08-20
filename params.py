#  Check-In Tradizionale
# La coda # 1 è per i passeggeri di classe Business
# La coda # 2 è per i passeggeri di classe Premium-Economy
# La coda # 3 è per i passeggeri di classe Economy

#  Check-In Tradizionale
# La coda # 4 per i passeggeri che scelgono l'opzione Flexi-Plus
# La coda # 5 per i passeggeri che scelgono l'opzione Self Bag & Drop
# La coda # 6 per i passeggeri che scelgono l'opzione Bag & Drop

#  Fast - Track
# La coda # 7 è per il Tornello
# La coda # 8 è per la coda per i controlli di sicurezza della zona Fast - Track

#  Normale
# Le code # 9 - 10 - 11 - 12 sono per il Tornello
# La coda # 13 è per la coda per i controlli di sicurezza della zona Normale

# ---------------------------------------------- #

# I Passeggeri si suddividono in:
    # Tradizionali -> 20% di probabilità, così suddivisi:
            # Business - Class -> 10% di probabilità
            # Premium - Economy -> 20% di probabilità
            # Economy -> 45% di probabilità
            # Bagaglio a mano -Direttamente ai controlli di sicurezza- -> 25% di probabilità
    # Low-Cost -> 80% di probabilità, così suddivisi:
            # Bagaglio a mano -Direttamente ai controlli di sicurezza- -> 70% di probabilità
            # Scelta servizi opzionali -> 30% di probabilità, così definite:
                # Flexi - Plus -> 5% di probabilità
                # Self Bag & Drop -imbarco bagaglio da stiva- -> 10% di probabilità
                # BAg & Drop -imbarco bagaglio da stiva- -> 85% di probabilità

# Superata la zona di Check - In, i passeggeri si recano alla zona dei controlli di sicurezza dove:
#   I passeggeri che hanno acquistato la Business-Class o il servizio Flexi-Plus accedono direttamente all'area Fast-Track -inclusa nel loro servizio-
#   I restanti passeggeri possono scegliere di acquistare in Aeroporto il servizio Fast-Track, con le rispettive probabilità:
#       Fast - Track -> 20% di probabilità
#       Normali -> 80% di probabilità



# -------------------- PARAMETRI DI CONFIGURAZIONE --------------------
VERBOSE = False

#  -------------------- PARAMETRI DI SIMULAZIONE (dipendenti da parametri di configurazione) --------------------

# -------------------- Indici dei serventi Check-In --------------------
BUSINESS_CLASS_SERVER_INDEX             = [0]
PREMIUM_ECONOMY_CLASS_SERVER_INDEX      = [1]
ECONOMY_CLASS_MULTI_SERVER_INDEX        = [2, 3, 4]
FLEXI_PLUS_SERVER_INDEX                 = [5]
SELF_BD_MULTI_SERVER_INDEX              = [6, 7]
BD_MULTI_SERVER_INDEX                   = [8, 9, 10, 11]

# -------------------- Indici dei serventi Fast-Track --------------------
TORNELLO_FAST_TRACK_SERVER_INDEX        = [12]
SICUREZZA_FAST_TRACK_SERVER_INDEX       = [13, 14]

# -------------------- Indici dei serventi Normali --------------------
TORNELLO_NORMALE_1_SERVER_INDEX         = [15]
TORNELLO_NORMALE_2_SERVER_INDEX         = [16]
TORNELLO_NORMALE_3_SERVER_INDEX         = [17]
TORNELLO_NORMALE_4_SERVER_INDEX         = [18]
SICUREZZA_NORMALE_SERVER_INDEX          = [19, 20, 21, 22, 23, 24]

# -------------------- Indici delle code Check-In --------------------
BUSINESS_CLASS_QUEUE             = [0]
PREMIUM_ECONOMY_CLASS_QUEUE      = [1]
ECONOMY_CLASS_MULTI_QUEUE        = [2]

FLEXI_PLUS_SERVER_QUEUE          = [3]
SELF_BD_MULTI_SERVER_QUEUE       = [4]
BD_MULTI_SERVER_QUEUE            = [5]

# -------------------- Indici dei code Fast-Track --------------------
TORNELLO_FAST_TRACK_QUEUE        = [6]
SICUREZZA_FAST_TRACK_QUEUE       = [7]

# -------------------- Indici dei code Normali --------------------
TORNELLO_NORMALE_1_QUEUE         = [8]
TORNELLO_NORMALE_2_QUEUE         = [9]
TORNELLO_NORMALE_3_QUEUE         = [10]
TORNELLO_NORMALE_4_QUEUE         = [11]
SICUREZZA_NORMALE_QUEUE          = [12]


# ------------------- Server -------------------------------------------
SERVER_NUM_AREA_CHECK_IN    = (len(BUSINESS_CLASS_SERVER_INDEX)         +
                              len(PREMIUM_ECONOMY_CLASS_SERVER_INDEX)   +
                              len(ECONOMY_CLASS_MULTI_SERVER_INDEX)     +
                              len(FLEXI_PLUS_SERVER_INDEX)              +
                              len(SELF_BD_MULTI_SERVER_INDEX)           +
                              len(BD_MULTI_SERVER_INDEX)                )

SERVER_NUM_AREA_FAST_TRACK = (len(TORNELLO_FAST_TRACK_SERVER_INDEX)     +
                              len(SICUREZZA_FAST_TRACK_SERVER_INDEX)    )

SERVER_NUM_AREA_NORMALE     = (len(TORNELLO_NORMALE_1_SERVER_INDEX)     +
                              len(TORNELLO_NORMALE_2_SERVER_INDEX)      +
                              len(TORNELLO_NORMALE_3_SERVER_INDEX)      +
                              len(TORNELLO_NORMALE_4_SERVER_INDEX)      +
                              len(SICUREZZA_NORMALE_SERVER_INDEX)       )

# ------------------- Code -------------------------------------------
QUEUES_NUM_AREA_CHECK_IN    = (len(BUSINESS_CLASS_QUEUE)                +
                               len(PREMIUM_ECONOMY_CLASS_QUEUE)         +
                               len(ECONOMY_CLASS_MULTI_QUEUE)           +
                               len(FLEXI_PLUS_SERVER_QUEUE)             +
                               len(SELF_BD_MULTI_SERVER_QUEUE)          +
                               len(BD_MULTI_SERVER_QUEUE)               )

QUEUES_NUM_AREA_FAST_TRACK = (len(TORNELLO_FAST_TRACK_QUEUE)            +
                              len(SICUREZZA_FAST_TRACK_QUEUE)           )

QUEUES_NUM_AREA_NORMALE     = (len(TORNELLO_NORMALE_1_QUEUE)            +
                              len(TORNELLO_NORMALE_2_QUEUE)             +
                              len(TORNELLO_NORMALE_3_QUEUE)             +
                              len(TORNELLO_NORMALE_4_QUEUE)             +
                              len(SICUREZZA_NORMALE_QUEUE)              )


# -------------------- Tempi di Arrivo --------------------

LAMBDA_G = 1 / 1.5     # Tempo di inter-arrivo medio 1.5 minuti (misurazione di 50 persone in 40 minuti -> 1 persona ogni 0.8 minuti)
LAMBDA_ON = 1 / 10     # Tempo di inter-arrivo medio 10 minuti prenotazioni Online

# CALCOLO DEL TEMPO DI ARRIVO
LAMBDA = LAMBDA_G + LAMBDA_ON
P_ON = LAMBDA_ON / LAMBDA

# -------------------- Tempi di Servizio --------------------
# Base campana: μ±3σ (99.7% dei valori)

MU_OC = 1 / 15      # Tempo di servizio medio 15 minuti PV Sportello
SIGMA_OC = 5 / 3    # Deviazione standard 5 minuti PV Sportello

MU_SR = 1 / 4.5     # Tempo di servizio medio 4.5 minuti
SIGMA_SR = 2 / 3    # Deviazione standard 2 minuti

MU_ATM = 1 / 2.5    # Tempo di servizio medio 2.5 minuti PV ATM
SIGMA_ATM = 1 / 3   # Deviazione standard 1 minuto PV ATM

MU_LOCKER = 1 / 1       # Tempo di servizio medio 1 minuto Locker
SIGMA_LOCKER = 0.5 / 3  # Deviazione standard 0.5 minuti Locker
# -------------------- Stream Index --------------------

# Stream Associati agli arrivi
CLASSIC_ONLINE_STREAM = 0
CLASSIC_DIFF_STREAM = 1
CLASSIC_STREAM = 2

SR_ONLINE_STREAM = 3
SR_STREAM = 5
SR_DIFF_STREAM = 4

ATM_DIFF_STREAM = 6
ATM_STREAM = 7

LOCKER_STREAM = 8

# Stream Associati ai servizi
CLASSIC_SERVICE_STREAM = 9  # I multi-server
SR_SERVICE_STREAM = 10      # Il server Spedizioni e Ritiri
ATM_SERVICE_STREAM = 11     # Lo sportello ATM

if IMPROVED_SIM:
    LOCKER_SERVICE_STREAM = 12  # Il locker

# -------------------- Probabilità --------------------

P_DIFF = 0.15  # Probabilità di persona in difficoltà

# Probabilità di scelta dell'operazione
P_OC = 0.45      # Probabilità di Operazione Classica
P_SR = 0.2     # Probabilità di Spedizione e Ritiri
P_ATM = 0.35    # Probabilità di ATM

# Probabilità di scelta dell'operazione online
P_OC_ON = 0.6  # Probabilità di Operazione Classica online
P_SR_ON = 0.4  # Probabilità di Spedizione e Ritiri online


# -------------------- CSV FILE NAME --------------------
DIRECTORY_FINITE_H = "./finite_horizon/"
DIRECTORY_INFINITE_H = "./infinite_horizon/"

CSV_UTILIZATION = "utilization.csv"
CSV_DELAY = "delay.csv"       # Tempo di attesa in coda
CSV_WAITING_TIME = "waiting_time.csv"     # Tempo di risposta (Tempo di attesa + Tempo di servizio)
CSV_N_QUEUE = "pop_queue.csv"     # Tempo di risposta (Tempo di attesa + Tempo di servizio)

CSV_END_WORK_TIME_FINITE = "end_work_time_finite.csv"   # Tempo di fine lavoro