class LambdaScaler:
    def __init__(self):
        self.total_daily_passengers = 29522

        self.P_T = 0.20              # Probabilità che un passeggero scelga una compagnia Tradizionale
        self.P_L = 0.80              # Probabilità che un passeggero scelga una compagnia Low-Cost

        self.P_T_B = 0.10             # Probabilità che un passeggero scelga la tariffa Business-Class
        self.P_T_PE = 0.20           # Probabilità che un passeggero scelga la tariffa Premium-Economy
        self.P_T_E = 0.45            # Probabilità che un passeggero scelga la tariffa Economy
        self.P_T_OB = 0.25           # Probabilità che un passeggero abbia effettuato check-in online e non abbia il bagaglio da stiva

        self.P_L_OB = 0.70           # Probabilità che un passeggero non abbia il bagaglio da stiva
        self.P_L_NOB = 1 - self.P_L_OB    # Probabilità che un passeggero richieda servizi aggiuntivi

        self.P_L_FP = 0.05           # Probabilità che un passeggero abbia scelto il servizio Flexi-Plus
        self.P_L_SB_e_D = 0.10       # Probabilità che un passeggero esegue autonomamente l'imbarco del bagaglio da stiva
        self.P_L_B_e_D = 0.85        # Probabilità che un passeggero non esegue autonomamente l'imbarco del bagaglio da stiva

        self.P_FT = 0.20             # Probabilità che un passeggero decida di acquistare il servizio Fast-Track
        self.P_N = 1 - self.P_FT          # Probabilità che un passeggero non acquisti il servizio Fast-Track


        self.slots_duration = {
            "night" : 360*60,
            "morning" : 180*60,
            "late_morning" : 180*60,
            "early_afternoon" : 180*60,
            "late_afternoon" : 240*60,
            "evening" : 180*60,
            "late_evening" : 120*60
        }
        self.lambdas = {
            "business": 0.0,
            "premium_economy": 0.0,
            "economy": 0.0,
            "flexi_plus": 0.0,
            "self_bd": 0.0,
            "bd": 0.0,
            "turnstile_area": 0.0,
            "exogenous": 0.0,
            "fast_track_turnstile": 0.0,
            "security_area": 0.0,
            "fast_track_security_area": 0.0,
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

    def return_new_lambdas(self, time_slot):
        num_of_passenger_in_slot = self.total_daily_passengers * (self.percent.get(time_slot)) #Passeggeri che arrivano in quella fascia oraria
        lambda_total_slot = num_of_passenger_in_slot / (self.slots_duration[time_slot]) #Tasso globale in ingresso al sistema in quella fascia oraria
        self.calculate_lambdas(lambda_total_slot)
        return self.lambdas


    def calculate_lambdas(self, lambda_total):
        GAMMA = lambda_total  # Tasso medio complessivo degli arrivi

        LAMBDA_A = GAMMA * 0.6  # Tasso medio complessivo degli arrivi alla zona Check-In A
        LAMBDA_E = GAMMA * 0.4  # Tasso medio complessivo degli arrivi che usufruiscono della zona Check-In B e C

        # -------------------- Check-In tradizionale --------------
        LAMBDA_T = LAMBDA_A * self.P_T  # 0.041004
        LAMBDA_BC = LAMBDA_T * self.P_T_B  # Tasso medio d'arrivo al centro Business-Class
        LAMBDA_PE = LAMBDA_T * self.P_T_PE  # Tasso medio d'arrivo al centro Premium-Economy
        LAMBDA_ECO = LAMBDA_T * self.P_T_E  # Tasso medio d'arrivo al centro Economy
        LAMBDA_BM = LAMBDA_T * self.P_T_OB  # Tasso medio d'arrivo per Bagaglio a Mano

        LAMBDA_2 = LAMBDA_BM + LAMBDA_ECO + LAMBDA_PE

        # -------------------- Check-In Low-Cost --------------
        LAMBDA_LC = LAMBDA_A * self.P_L
        LAMBDA_FP = (LAMBDA_LC * self.P_L_NOB) * self.P_L_FP  # Tasso medio d'arrivo al centro Flexi-Plus
        LAMBDA_SBD = (LAMBDA_LC * self.P_L_NOB) * self.P_L_SB_e_D  # Tasso medio d'arrivo al centro Self Bag and Drop
        LAMBDA_BD = (LAMBDA_LC * self.P_L_NOB) * self.P_L_B_e_D  # Tasso medio d'arrivo al centro Bag and Drop
        LAMBDA_BM_LC = LAMBDA_LC * self.P_L_OB  # Tasso medio d'arrivo per Bagaglio a Mano

        LAMBDA_BM_TOT = LAMBDA_BM + LAMBDA_BM_LC

        LAMBDA_3 = LAMBDA_SBD + LAMBDA_BD + LAMBDA_BM_LC

        # -------------------- Ingresso Area di Sicurezza -------------
        LAMBDA_4 = LAMBDA_2 + LAMBDA_3
        LAMBDA_5 = LAMBDA_4 + LAMBDA_E

        # -------------------- Fast-Track --------------------------------
        # Valido sia per l'ingresso al tornello che per l'ingresso all'aera di sicurezza riservato all'area Fast-Track
        LAMBDA_6 = (LAMBDA_4 * self.P_FT) + LAMBDA_BC + LAMBDA_FP

        # -------------------- Normale --------------------------------
        # Valido sia per l'ingresso al tornello che per l'ingresso all'aera di sicurezza riservato all'area Normale
        LAMBDA_7 = (LAMBDA_4 * self.P_N)

        self.lambdas = {"business": LAMBDA_BC, "premium_economy": LAMBDA_PE, "economy": LAMBDA_ECO,
                        "flexi_plus": LAMBDA_FP, "self_bd": LAMBDA_SBD, "bd": LAMBDA_BD,
                        "turnstile_area_external": LAMBDA_BM_TOT, "exogenous": LAMBDA_E, "fast_track_turnstile": LAMBDA_6,
                        "security_area": LAMBDA_7, "fast_track_security_area": LAMBDA_6, }



