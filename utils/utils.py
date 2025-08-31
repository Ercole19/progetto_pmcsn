from libs.rvgs import *
from libs.rvms import *

def format_queues(queues):
    """
    Formatta le code per la stampa di debug
    :param queues:
    :return:
    """
    formatted_queues = []
    for q in queues:
        formatted_queue = [event.event_time for event in q]  # Estrai solo i tempi da ciascun oggetto evento
        formatted_queues.append(formatted_queue)
    return formatted_queues




def truncate_lognormal(mu, sigma, inf, sup):
    """
    Tronca la distribuzione lognormale tra inf e sup.
    Utilizza le funzioni cdfLognormal e idfLognormal.

    :param mu: Media della distribuzione lognormale (riferita al logaritmo dei dati)
    :param sigma: Deviazione standard della distribuzione lognormale (riferita al logaritmo dei dati)
    :param inf: Valore minimo per il troncamento
    :param sup: Valore massimo per il troncamento
    :return: Un campione dalla distribuzione lognormale troncata
    """
    # Calcola la CDF della lognormale a inf e sup
    alpha = cdfLognormal(mu, sigma, inf)

    beta = cdfLognormal(mu, sigma, sup)

    # Genera un valore uniforme tra alpha e beta
    u = Uniform(alpha, beta)

    # Inversa della CDF (quantile) per ottenere il valore lognormale troncato
    return idfLognormal(mu, sigma, u)