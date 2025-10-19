"""
admin.py

Configuração do painel administrativo Django para o sistema de reservas.
Define as interfaces de administração para os modelos Mesa e Booking.
"""

from django.contrib import admin
from datetime import datetime
from .models import Mesa, Booking
from .views import RESERVATION_DURATION


@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    """
    Configuração da interface administrativa para o modelo Mesa.
    
    Permite visualização, filtragem e busca de mesas no painel admin.
    O campo 'existe_reserva' é calculado automaticamente e não pode ser editado manualmente.
    """
    list_display = ('id', 'lugares', 'existe_reserva')
    list_filter = ('existe_reserva',)
    search_fields = ('id',)
    readonly_fields = ('existe_reserva',)
    
    fieldsets = (
        ('Configuração da Mesa', {
            'fields': ('lugares',)
        }),
        ('Status', {
            'fields': ('existe_reserva',),
            'description': 'Este campo é atualizado automaticamente com base nas reservas ativas.'
        }),
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Configuração da interface administrativa para o modelo Booking (Reserva).
    
    Permite gerenciamento completo de reservas, incluindo:
    - Visualização de todas as reservas com informações detalhadas
    - Filtragem por data e mesa
    - Busca por nome e telefone do cliente
    - Cálculo automático do horário de término (end_time)
    """
    list_display = ('id', 'name', 'phone', 'mesa', 'date', 'start_time', 'end_time', 'number_of_guests', 'notes')
    list_filter = ('date', 'mesa')
    search_fields = ('name', 'phone')
    date_hierarchy = 'date'
    readonly_fields = ('end_time',)
    
    fieldsets = (
        ('Informações do Cliente', {
            'fields': ('name', 'phone'),
            'description': 'Dados pessoais.'
        }),
        ('Detalhes da Reserva', {
            'fields': ('mesa', 'date', 'start_time', 'end_time', 'number_of_guests'),
            'description': 'O horário de término é calculado automaticamente (início + 1h15min).'
        }),
        ('Observações', {
            'fields': ('notes',),
            'description': 'Informações adicionais sobre a reserva (opcional).'
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Sobrescreve o método de salvamento para calcular automaticamente o horário de término.
        
        O end_time é definido como start_time + RESERVATION_DURATION (1 hora e 15 minutos).
        Este cálculo ocorre sempre que uma reserva é criada ou editada.
        
        Args:
            request: Objeto HttpRequest da requisição atual.
            obj: Instância do modelo Booking sendo salva.
            form: Formulário do admin contendo os dados da reserva.
            change: Boolean indicando se é uma edição (True) ou criação (False).
        """
        if obj.start_time:
            # Converte o horário de início para um objeto datetime completo
            start_datetime = datetime.combine(datetime.today(), obj.start_time)
            
            # Adiciona a duração padrão da reserva (1h15min)
            end_datetime = start_datetime + RESERVATION_DURATION
            
            # Extrai apenas o componente de tempo e atribui ao end_time
            obj.end_time = end_datetime.time()
        
        super().save_model(request, obj, form, change)