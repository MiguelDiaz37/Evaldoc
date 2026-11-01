import time


def reintentar(funcion, intentos=3, espera_base=0.5, factor=2.0, es_reintentable=None,
               dormir=time.sleep, al_reintentar=None):
    ultimo_error = None
    for intento in range(1, intentos + 1):
        try:
            return funcion()
        except Exception as e:
            ultimo_error = e
            if es_reintentable and not es_reintentable(e):
                raise
            if intento == intentos:
                break
            espera = espera_base * factor ** (intento - 1)
            if al_reintentar:
                al_reintentar(intento, espera, e)
            dormir(espera)
    raise ultimo_error
