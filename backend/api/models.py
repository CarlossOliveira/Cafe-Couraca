"""
models.py

Define os modelos de dados para o sistema de gestão de reservas do Café.
Este módulo contém as entidades principais: Mesa e Booking (Reserva).
"""

from django.db import models


class Mesa(models.Model):
    """
    Representa uma mesa do Café.
    
    Attributes:
        lugares (int): Capacidade máxima de pessoas que a mesa comporta.
        existe_reserva (bool): Indica se a mesa possui pelo menos uma reserva ativa.
    """
    lugares = models.IntegerField()
    existe_reserva = models.BooleanField(default=False)

class Booking(models.Model):
    """
    Representa uma reserva de mesa no Café.
    
    Attributes:
        mesa (ForeignKey): Referência à mesa reservada.
        name (str): Nome completo do cliente que realizou a reserva.
        phone (str): Número de telefone do cliente (8-15 caracteres).
        date (date): Data da reserva.
        start_time (time): Horário de início da reserva.
        end_time (time): Horário de término da reserva (calculado automaticamente como start_time + 1h15min).
        number_of_guests (int): Número de convidados para a reserva.
        notes (str): Observações adicionais sobre a reserva (campo opcional).
    """
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name='reservas')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=12)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    number_of_guests = models.IntegerField()
    notes = models.TextField(blank=True, null=True)