#  Check-In Tradizionale
# La coda # 0 è per i passeggeri di classe Business
# La coda # 1 è per i passeggeri di classe Premium-Economy
# La coda # 2 è per i passeggeri di classe Economy

#  Check-In Tradizionale
# La coda # 3 per i passeggeri che scelgono l'opzione Flexi-Plus
# La coda # 4 per i passeggeri che scelgono l'opzione Self Bag & Drop
# La coda # 5 per i passeggeri che scelgono l'opzione Bag & Drop

#  Fast - Track
# La coda # 6 è per il Tornello
# La coda # 7 è per la coda per i controlli di sicurezza della zona Fast - Track

#  Normale
# Le code # 8 - 9 - 10 - 11 sono per il Tornello
# La coda # 12 è per la coda per i controlli di sicurezza della zona Normale

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
TORNELLI_NORMALI_SERVER_INDEXES = [15,16,17,18]
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
TORNELLI_NORMALI_INDEXES         = [8, 9, 10, 11]
SICUREZZA_NORMALE_QUEUE          = [12]



# ------------------- Server -------------------------------------------
CLASSIC_SERVER_NUM_AREA_CHECK_IN    = (len(BUSINESS_CLASS_SERVER_INDEX)         +
                              len(PREMIUM_ECONOMY_CLASS_SERVER_INDEX)   +
                              len(ECONOMY_CLASS_MULTI_SERVER_INDEX)     +
                              len(FLEXI_PLUS_SERVER_INDEX)
                                  )

BAG_DROP_CHECK_IN_SERVERS = (len(SELF_BD_MULTI_SERVER_INDEX)           +
                              len(BD_MULTI_SERVER_INDEX)          )

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

# -------------------- Probabilità --------------------

P_T = 0.20              # Probabilità che un passeggero scelga una compagnia Tradizionale
P_L = 0.80              # Probabilità che un passeggero scelga una compagnia Low-Cost

P_T_B = 0.10             # Probabilità che un passeggero scelga la tariffa Business-Class
P_T_PE = 0.20           # Probabilità che un passeggero scelga la tariffa Premium-Economy
P_T_E = 0.45            # Probabilità che un passeggero scelga la tariffa Economy
P_T_OB = 0.25           # Probabilità che un passeggero abbia effettuato check-in online e non abbia il bagaglio da stiva

P_L_OB = 0.70           # Probabilità che un passeggero non abbia il bagaglio da stiva
P_L_NOB = 1 - P_L_OB    # Probabilità che un passeggero richieda servizi aggiuntivi

P_L_FP = 0.05           # Probabilità che un passeggero abbia scelto il servizio Flexi-Plus
P_L_SB_e_D = 0.10       # Probabilità che un passeggero esegue autonomamente l'imbarco del bagaglio da stiva
P_L_B_e_D = 0.85        # Probabilità che un passeggero non esegue autonomamente l'imbarco del bagaglio da stiva

P_FT = 0.20             # Probabilità che un passeggero decida di acquistare il servizio Fast-Track
P_N = 1 - P_FT          # Probabilità che un passeggero non acquisti il servizio Fast-Track

# -------------------- Tempi di Arrivo --------------------

GAMMA = 0.3417                  # Tasso medio complessivo degli arrivi

LAMBDA_A = GAMMA * 0.6          # Tasso medio complessivo degli arrivi alla zona Check-In A
LAMBDA_E = GAMMA * 0.4          # Tasso medio complessivo degli arrivi che usufruiscono della zona Check-In B e C

# -------------------- Check-In tradizionale --------------
LAMBDA_T    = LAMBDA_A * P_T
LAMBDA_BC   = LAMBDA_T * P_T_B      # Tasso medio d'arrivo al centro Business-Class
LAMBDA_PE   = LAMBDA_T * P_T_PE     # Tasso medio d'arrivo al centro Premium-Economy
LAMBDA_ECO  = LAMBDA_T * P_T_E      # Tasso medio d'arrivo al centro Economy
LAMBDA_BM   = LAMBDA_T * P_T_OB     # Tasso medio d'arrivo per Bagaglio a Mano

LAMBDA_2 = LAMBDA_BM + LAMBDA_ECO + LAMBDA_PE

# -------------------- Check-In Low-Cost --------------
LAMBDA_LC       = LAMBDA_A * P_L
LAMBDA_FP       = (LAMBDA_LC * P_L_NOB) * P_L_FP        # Tasso medio d'arrivo al centro Flexi-Plus
LAMBDA_SBD      = (LAMBDA_LC * P_L_NOB) * P_L_SB_e_D    # Tasso medio d'arrivo al centro Self Bag and Drop
LAMBDA_BD       = (LAMBDA_LC * P_L_NOB)  * P_L_B_e_D    # Tasso medio d'arrivo al centro Bag and Drop
LAMBDA_BM_LC    = LAMBDA_LC * P_L_OB                    # Tasso medio d'arrivo per Bagaglio a Mano

LAMBDA_3 = LAMBDA_SBD + LAMBDA_BD + LAMBDA_BM_LC

# -------------------- Ingresso Area di Sicurezza -------------
LAMBDA_4 = LAMBDA_2 + LAMBDA_3
LAMBDA_5 = LAMBDA_4 + LAMBDA_E

# -------------------- Fast-Track --------------------------------
# Valido sia per l'ingresso al tornello che per l'ingresso all'aera di sicurezza riservato all'area Fast-Track
LAMBDA_6 = (LAMBDA_4 * P_FT) + LAMBDA_BC + LAMBDA_FP

# -------------------- Normale --------------------------------
# Valido sia per l'ingresso al tornello che per l'ingresso all'aera di sicurezza riservato all'area Normale
LAMBDA_7 = (LAMBDA_4 * P_N)

# -------------------- Tempi di Servizio -----------------------

# -------------------- Check-In Tradizionale E Low-Cost -Flexi-Plus-   --------------------------
MU_DESK = 1 / 3                         # Tempo di servizio medio 3 minuti
SIGMA_DESK = 0.165                      # Deviazione standard

MU_DESK_LOW_COST_BAG_DROP = 1           # Tempo di servizio medio 1 minuti
SIGMA_DESK_BAG_DROP = 0.242             # Deviazione standard

# -------------------- Tornello (Fast-Track e Normale) -----------------
MU_DESK_LOW_COST = 1 / 3                # Tempo di servizio medio 3 minuti

# -------------------- Controlli Sicurezza -----------------------------
MU_CONTROLLI_SICUREZZA = 1 / 4          # Tempo di servizio medio 4 minuti
SIGMA_CONTROLLI_SICUREZZA = 0.667       # Deviazione standard



# -------------------- CSV FILE NAME --------------------
DIRECTORY_FINITE_H = "./finite_horizon/"
DIRECTORY_INFINITE_H = "./infinite_horizon/"

CSV_UTILIZATION = "utilization.csv"
CSV_DELAY = "delay.csv"       # Tempo di attesa in coda
CSV_WAITING_TIME = "waiting_time.csv"     # Tempo di risposta (Tempo di attesa + Tempo di servizio)
CSV_N_QUEUE = "pop_queue.csv"     # Tempo di risposta (Tempo di attesa + Tempo di servizio)

CSV_END_WORK_TIME_FINITE = "end_work_time_finite.csv"   # Tempo di fine lavoro