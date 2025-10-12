from django.apps import AppConfig

class TicketsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tickets'

    def ready(self):
        # ⚠️ ELIMINAR la línea: import tickets.signals
        pass # La función ready() ahora no hace nada o puedes eliminarla si está vacía