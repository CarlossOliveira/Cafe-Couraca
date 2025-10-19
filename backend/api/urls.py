"""
urls.py

Configuração de rotas (URLs) para a API do sistema de reservas.

Este módulo define todos os endpoints disponíveis na API, mapeando URLs
para suas respectivas funções de visualização (views).

Estrutura de endpoints:
    - /admin/login/                             : Login de administradores
    - /admin/logout/                            : Logout de administradores
    - /admin/status/                            : Status da sessão do admin
    - /bookings/create/                         : Criação de reservas
    - /bookings/list/                           : Listagem de reservas
    - /bookings/cancel/<booking_id>/            : Cancelamento de reservas
    - /mesas/create/                            : Criação de mesas
    - /mesas/list/                              : Listagem de mesas
    - /mesas/delete/<mesa_id>/                  : Remoção de mesas
"""

from django.urls import path
from api import views


# ================================================================================================
# CONFIGURAÇÃO DE ROTAS DA API
# ================================================================================================

urlpatterns = [
    # -------------------------------------------------------------------------
    # Autenticação
    # -------------------------------------------------------------------------
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),
    path('admin/status/', views.admin_status, name='admin_status'),

    # -------------------------------------------------------------------------
    # Gestão de Reservas (Bookings)
    # -------------------------------------------------------------------------
    path('bookings/create/', views.create_booking, name='booking_create'),
    path('bookings/list/', views.view_bookings, name='booking_list'),
    path('bookings/cancel/<int:booking_id>/', views.cancel_booking, name='booking_cancel'),

    # -------------------------------------------------------------------------
    # Gestão de Mesas
    # -------------------------------------------------------------------------
    path('mesas/create/', views.create_mesa, name='mesa_create'),
    path('mesas/list/', views.list_mesas, name='mesa_list'),
    path('mesas/delete/<int:mesa_id>/', views.delete_mesa, name='mesa_delete'),
]
