from datetime import timedelta
from django.utils import timezone
from apps.automatizacion.models import ReglaAutomatizacion
from apps.dispositivos.models import Dispositivo
from apps.ocupacion.models import EventoOcupacion
from apps.control.models import Comando

def evaluar_reglas():
    """
    Evalúa todas las reglas activas y genera comandos si se cumplen las condiciones.
    Retorna el número de comandos generados.
    """
    reglas = ReglaAutomatizacion.objects.filter(activa=True)
    comandos_generados = 0
    ahora = timezone.now()

    for regla in reglas:
        if regla.condicion == 'inactividad_minutos':
            umbral_tiempo = ahora - timedelta(minutes=regla.valor_umbral)
            
            dispositivos = Dispositivo.objects.all()
            for disp in dispositivos:
                ultimo_evento = EventoOcupacion.objects.filter(dispositivo=disp).order_by('-registrado_en').first()
                
                # Si no hay evento reciente o el último evento fue "desocupado" o el último "ocupado" fue hace mucho
                # Asumimos inactividad. Pero seamos precisos:
                # Si el último evento fue hace más del umbral_tiempo y no hay un comando de apagado pendiente
                if ultimo_evento and ultimo_evento.registrado_en < umbral_tiempo:
                    # Verificar si ya mandamos este comando recientemente para no spammear
                    comando_reciente = Comando.objects.filter(
                        dispositivo=disp,
                        tipo_accion=regla.accion_a_ejecutar,
                        estado='pendiente'
                    ).exists()
                    
                    if not comando_reciente:
                        Comando.objects.create(
                            dispositivo=disp,
                            tipo_accion=regla.accion_a_ejecutar
                        )
                        comandos_generados += 1

    return comandos_generados
