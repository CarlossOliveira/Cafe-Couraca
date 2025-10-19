"""
views.py

API REST para o sistema de gestão de reservas do Café.
Implementa endpoints para gerenciamento de reservas (bookings), mesas e autenticação.

Este módulo utiliza Django REST Framework para fornecer uma API RESTful completa,
incluindo operações CRUD e autenticação via sessões.
"""

from rest_framework.decorators import api_view, permission_classes, throttle_classes # Decoradores para views
from rest_framework.permissions import AllowAny, IsAdminUser # Permissões de acesso
from rest_framework.response import Response # Respostas HTTP
from rest_framework import status # Códigos de status HTTP
from .models import Booking as BookingTable, Mesa as MesaTable # Bases de dados
from django.contrib.auth import authenticate, login, logout # Autenticação de usuários
from datetime import datetime, timedelta # Manipulação de datas e horas 
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle # API Rate Limiting
import re # Regex para validação de input

# ================================================================================================
# CONSTANTES DE CONFIGURAÇÃO
# ================================================================================================

# Duração padrão de cada reserva (1 hora e 15 minutos)
RESERVATION_DURATION = timedelta(hours=1, minutes=15)

# Período após o qual reservas passadas são consideradas expiradas e removidas do sistema
BOOKING_EXPIERY_DAYS = 16

# ================================================================================================
# ENDPOINTS - GESTÃO DE RESERVAS (BOOKINGS)
# ================================================================================================

@api_view(['POST'])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
@permission_classes([AllowAny])
def create_booking(request):
    """
    Cria uma nova reserva no sistema.
    
    Este endpoint realiza um processo completo de validação e criação de reservas:
    1. Remove reservas expiradas do sistema
    2. Valida todos os parâmetros recebidos
    3. Verifica disponibilidade de mesas adequadas
    4. Detecta conflitos de horário
    5. Cria a reserva e atualiza o status da mesa
    
    Permissions:
        AllowAny - Endpoint público, não requer autenticação.
    
    Request Body (JSON):
        {
            "name": str - Nome completo do cliente (obrigatório),
            "phone": str - Telefone (8-15 caracteres, obrigatório),
            "date": str - Data da reserva no formato "YYYY-MM-DD" (obrigatório),
            "time": str - Horário de início no formato "HH:MM" (obrigatório),
            "number_of_guests": str|int - Número de convidados (obrigatório),
            "notes": str - Observações adicionais (opcional)
        }
    
    Returns:
        Response:
            - 201 CREATED: Reserva criada com sucesso
            - 400 BAD REQUEST: Parâmetros inválidos, conflito de horário ou mesa indisponível
            - 500 INTERNAL SERVER ERROR: Erro ao salvar a reserva no banco de dados
    
    Rules:
        - Não permite reservas em datas/horários passados
        - Reservas têm duração fixa de 1h15min
        - Sistema seleciona automaticamente a mesa mais adequada
        - Detecta e previne conflitos de horário entre reservas
    """
    
    # -------------------------------------------------------------------------
    # FASE 1: Validação inicial dos parâmetros obrigatórios
    # -------------------------------------------------------------------------
    # Verifica presença e tipo de todos os parâmetros obrigatórios
    required_fields = ["number_of_guests", "name", "phone", "date", "time"]
    for field in required_fields:
        value = request.data.get(field)
        
        # Valida existência e não-vazio
        if value is None or str(value).strip() == "":
            return Response(
                {"detail": f"Parâmetros inválidos ou insuficientes. Campo '{field}' é obrigatório."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Valida tipo de dado (deve ser string)
        if type(value) is not str:
            return Response(
                {"detail": f"Parâmetros inválidos. Campo '{field}' deve ser uma string."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Extrai valores dos parâmetros
    try:
        name = request.data.get("name").strip()
        date =  datetime.strptime(request.data.get("date"), "%Y-%m-%d").date()
        time = datetime.strptime(request.data.get("time"), "%H:%M").time()
        horario_reserva = datetime.combine(date, time)
        raw_phone = request.data.get("phone", "")
        number_of_guests = int(request.data.get("number_of_guests"))
        notes = request.data.get("notes", "").strip() if request.data.get("notes") else ""
    except (ValueError, TypeError, AttributeError):
        return Response(
            {"detail": "Requisição inválida. Verifique o formato da data (YYYY-MM-DD) e hora (HH:MM)."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # -------------------------------------------------------------------------
    # FASE 2: Validação de segurança de Input (prevenção de XSS e DoS)
    # -------------------------------------------------------------------------
    
    # Validação de tamanho dos campos (prevenção de DoS)
    if len(name) > 200:
        return Response(
            {"detail": "Nome muito longo. Máximo de 200 caracteres."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(notes) > 1000:
        return Response(
            {"detail": "Notas muito longas. Máximo de 1000 caracteres."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validação de caracteres permitidos no nome (prevenção de XSS), permite letras (incluindo acentuadas), espaços, hífens e apóstrofos
    if not re.match(r"^[a-zA-ZÀ-ÿ\s\'\-]+$", name):
        return Response(
            {"detail": "Nome contém caracteres inválidos. Use apenas letras, espaços, hífens e apóstrofos."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Normaliza o telefone para conter apenas dígitos
    phone = re.sub(r"\D+", "", raw_phone)
    
    # Valida o campo 'notes' se fornecido
    if notes is not None and type(notes) is not str:
        return Response(
            {"detail": "Parâmetros inválidos. Campo 'notes' deve ser uma string."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validação de caracteres permitidos nas notas (prevenção de XSS), permite caracteres alfanuméricos, pontuação comum e acentuados
    if notes and not re.match(r"^[a-zA-Z0-9À-ÿ\s\.\,\!\?\:\;\'\"\-\(\)]+$", notes):
        return Response(
            {"detail": "Notas contêm caracteres inválidos."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # -------------------------------------------------------------------------
    # FASE 3: Validação das regras de negócio
    # -------------------------------------------------------------------------
    # Valida comprimento do telefone (9-15 caracteres)
    if len(phone) < 9 or len(phone) > 15:
        return Response(
            {"detail": "Telefone inválido. Deve conter entre 9 e 15 caracteres."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Valida data e horário (não pode ser no passado)
    if horario_reserva < datetime.now():
        return Response(
            {"detail": "Data e horário inválidos. Não é possível criar reservas no passado."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Valida horário de funcionamento (08:30 às 00:30, exceto domingos)
    if datetime.strptime("00:30", "%H:%M").time() < horario_reserva.time() < datetime.strptime("08:30", "%H:%M").time() or horario_reserva.date().weekday() == 6:
        return Response(
            {"detail": "Horário inválido. O horário de funcionamento do café é todos os dias menos domingo, das 08:30 às 00:30."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Valida número mínimo de convidados (deve ser pelo menos 1)
    if number_of_guests < 1:
        return Response(
            {"detail": "Número de convidados inválido. Deve ser no mínimo 1."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # -------------------------------------------------------------------------
    # FASE 4: Cálculo do intervalo de tempo da reserva
    # -------------------------------------------------------------------------
    # Define início e término com base na duração padrão (1h15min)
    end_time = horario_reserva + RESERVATION_DURATION
    
    # -------------------------------------------------------------------------
    # FASE 5: Verificação de duplicidade de reserva
    # -------------------------------------------------------------------------
    # Impede a duplicidade de reservas para o mesmo telefone na mesma data e horário
    reservas_existentes = BookingTable.objects.filter(date=date)

    if reservas_existentes.filter(phone=phone, start_time=time).exists():
        return Response(
            {"detail": "Já existe uma reserva registrada para este telefone na data solicitada e horário."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # -------------------------------------------------------------------------
    # FASE 6: Busca de mesa disponível
    # -------------------------------------------------------------------------
    # Procura mesas com capacidade adequada, priorizando match exato
    mesas_disponiveis = []
    
    # Prioridade 1: Mesa com capacidade exata
    if MesaTable.objects.filter(lugares=number_of_guests).exists():
        mesas_disponiveis = MesaTable.objects.filter(lugares=number_of_guests)
    else:
        # Prioridade 2: Mesa com capacidade maior que a necessária
        mesas_disponiveis = MesaTable.objects.filter(lugares__gte=number_of_guests)

    # -------------------------------------------------------------------------
    # FASE 7: Verificação de conflitos de horário
    # -------------------------------------------------------------------------
    # Itera sobre mesas candidatas para encontrar uma sem conflitos
    mesa_adequada = None
    
    for mesa in mesas_disponiveis:
        # Obtém todas as reservas existentes para esta mesa na data solicitada
        reservas_mesa = reservas_existentes.filter(mesa=mesa)
        conflito_encontrado = False
        
        # Verifica sobreposição de horários com cada reserva existente
        for reserva in reservas_mesa:
            reserva_start = datetime.combine(reserva.date, reserva.start_time)
            reserva_end = datetime.combine(reserva.date, reserva.end_time)
            
            # Detecta sobreposição: nova reserva começa antes do fim da existente
            # E termina depois do início da existente
            if horario_reserva < reserva_end and end_time > reserva_start:
                conflito_encontrado = True
                break
        
        # Se não houver conflito, esta mesa pode ser utilizada
        if not conflito_encontrado:
            mesa_adequada = mesa
            break

    # Retorna erro se nenhuma mesa disponível foi encontrada
    if not mesa_adequada:
        return Response(
            {"detail": "Não há mesas disponíveis para o horário e capacidade solicitados."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # -------------------------------------------------------------------------
    # FASE 8: Criação da reserva
    # -------------------------------------------------------------------------
    # Prepara os dados da nova reserva
    booking_data = {
        "mesa": mesa_adequada,
        "name": name,
        "phone": phone,
        "date": date,
        "start_time": time,
        "end_time": end_time.time(),
        "number_of_guests": number_of_guests,
        "notes": request.data.get("notes", "")
    }

    # Persiste a reserva no banco de dados com tratamento de exceções
    try:
        BookingTable.objects.create(**booking_data)
    except Exception as e:
        return Response(
            {"detail": f"Erro ao criar reserva no banco de dados: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # -------------------------------------------------------------------------
    # FASE 9: Limpeza de reservas expiradas e atualização do status das mesas
    # -------------------------------------------------------------------------
    # Limpa reservas expiradas e atualiza o status das mesas
    update_expired_objects()

    # -------------------------------------------------------------------------
    # FASE 10: Atualização do status da mesa
    # -------------------------------------------------------------------------
    # Marca a mesa como tendo reservas ativas
    mesa_adequada.existe_reserva = True
    mesa_adequada.save()

    return Response(
        {"detail": "Reserva criada com sucesso."}, 
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
@permission_classes([AllowAny])
def view_bookings(request):
    """
    Lista reservas do sistema com controle de acesso baseado em permissões.
    
    Comportamento diferenciado por tipo de usuário:
    - Administradores: Visualizam todas as reservas com informações completas
    - Usuários não autenticados: Visualizam apenas informações básicas de mesas ocupadas
    
    Permissions:
        AllowAny - Endpoint acessível publicamente, mas com dados limitados para não-admins.
    
    Returns:
        Response (200 OK):
            Para administradores (autenticados com is_staff=True):
                Array de objetos com todos os campos da reserva:
                [
                    {
                        "id": int,
                        "mesa": int,
                        "name": str,
                        "phone": str,
                        "date": str,
                        "start_time": str,
                        "end_time": str,
                        "number_of_guests": int,
                        "notes": str
                    }
                ]
            
            Para usuários públicos:
                Array de objetos com informações limitadas:
                [
                    {
                        "mesa": int,
                        "date": str,
                        "end_time": str
                    }
                ]
    """
    
    user = request.user
    bookings_data = []

    # Administradores têm acesso completo a todas as reservas
    if user.is_authenticated and user.is_staff:
        bookings = BookingTable.objects.all()
        
        for booking in bookings:
            bookings_data.append({
                "id": booking.id,
                "mesa": booking.mesa.id,
                "name": booking.name,
                "phone": booking.phone,
                "date": booking.date,
                "start_time": booking.start_time,
                "end_time": booking.end_time,
                "number_of_guests": booking.number_of_guests,
                "notes": booking.notes
            })
    else:
        # Usuários públicos visualizam apenas informações básicas de mesas ocupadas
        bookings = BookingTable.objects.filter(mesa__existe_reserva=True)
        
        for booking in bookings:
            bookings_data.append({
                "mesa": booking.mesa.id,
                "date": booking.date,
                "end_time": booking.end_time
            })
    
    # Limpa reservas expiradas e atualiza o status das mesas
    update_expired_objects()

    return Response(bookings_data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
@permission_classes([IsAdminUser])
def cancel_booking(request, booking_id):
    """
    Cancela uma reserva existente no sistema.
    
    Remove a reserva especificada e atualiza o status da mesa caso não haja
    outras reservas associadas a ela.
    
    Permissions:
        IsAdminUser - Apenas administradores autenticados podem cancelar reservas.
    
    URL Parameters:
        booking_id (int): Identificador único da reserva a ser cancelada.
    
    Returns:
        Response:
            - 204 NO CONTENT: Reserva cancelada com sucesso
            - 400 BAD REQUEST: ID da reserva não fornecido
            - 404 NOT FOUND: Reserva não encontrada no sistema
    
    Side Effects:
        - Remove a reserva do banco de dados
        - Atualiza mesa.existe_reserva para False se for a última reserva da mesa
    """
    
    # Validação do parâmetro obrigatório
    if booking_id is None:
        return Response(
            {'detail': 'ID da reserva não fornecido.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Busca a reserva no banco de dados
    try:
        booking = BookingTable.objects.get(id=booking_id)
    except BookingTable.DoesNotExist:
        return Response(
            {'detail': 'Reserva não encontrada no sistema.'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    # Verifica se esta é a única reserva da mesa
    # Se sim, marca a mesa como disponível
    if BookingTable.objects.filter(mesa=booking.mesa).count() == 1:
        booking.mesa.existe_reserva = False
        booking.mesa.save()
    
    # Remove a reserva do sistema
    booking.delete()
    
    # Limpa reservas expiradas e atualiza o status das mesas
    update_expired_objects()

    return Response(
        {'detail': 'Reserva cancelada com sucesso.'}, 
        status=status.HTTP_204_NO_CONTENT
    )


# ================================================================================================
# ENDPOINTS - GESTÃO DE MESAS
# ================================================================================================

@api_view(['POST'])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
@permission_classes([IsAdminUser])
def create_mesa(request):
    """
    Cria uma nova mesa no sistema do Café.
    
    Permite que administradores adicionem mesas ao Café, especificando
    sua capacidade de lugares.
    
    Permissions:
        IsAdminUser - Apenas administradores autenticados podem criar mesas.
    
    Request Body (JSON):
        {
            "lugares": int - Capacidade da mesa (número de assentos)
        }
    
    Returns:
        Response:
            - 201 CREATED: Mesa criada com sucesso (retorna id e lugares)
            - 400 BAD REQUEST: Parâmetro 'lugares' não fornecido
    """
    
    # Validação do parâmetro obrigatório
    if request.data.get("lugares") is None:
        return Response(
            {"detail": "Número de lugares não fornecido."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Cria a nova mesa no banco de dados
    new_mesa = MesaTable.objects.create(lugares=request.data.get("lugares"))
    
    # Limpa reservas expiradas e atualiza o status das mesas
    update_expired_objects()
    
    return Response(
        {
            "detail": "Mesa criada com sucesso.",
            "mesa": {
                "id": new_mesa.id,
                "lugares": new_mesa.lugares
            }
        }, 
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
@permission_classes([AllowAny])
def list_mesas(request):
    """
    Lista todas as mesas cadastradas no sistema.
    
    Retorna informações completas de todas as mesas do Café,
    incluindo capacidade e status de reserva.
    
    Permissions:
        AllowAny - Endpoint público, acessível sem autenticação.
    
    Returns:
        Response (200 OK):
            Array de objetos representando mesas:
            [
                {
                    "id_mesa": int,
                    "lugares": int,
                    "existe_reserva": bool
                }
            ]
    """

    lista_mesas = []
    mesas = MesaTable.objects.all()
    
    for mesa in mesas:
        data_mesa = {
            "id_mesa": mesa.id,
            "lugares": mesa.lugares,
            "existe_reserva": mesa.existe_reserva
        }
        lista_mesas.append(data_mesa)

    # Limpa reservas expiradas e atualiza o status das mesas
    update_expired_objects()
    
    return Response(lista_mesas, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
@permission_classes([IsAdminUser])
def delete_mesa(request, mesa_id):
    """
    Remove uma mesa do sistema do Café.
    
    Permite que administradores excluam mesas do sistema. Por segurança,
    não é permitido excluir mesas que possuem reservas ativas.
    
    Permissions:
        IsAdminUser - Apenas administradores autenticados podem excluir mesas.
    
    URL Parameters:
        mesa_id (int): Identificador único da mesa a ser removida.
    
    Returns:
        Response:
            - 204 NO CONTENT: Mesa removida com sucesso
            - 400 BAD REQUEST: ID não fornecido ou mesa possui reservas ativas
            - 404 NOT FOUND: Mesa não encontrada no sistema
    
    Business Rules:
        - Não permite exclusão de mesas com existe_reserva=True
        - Garante integridade referencial das reservas existentes
    """
    
    # Validação do parâmetro obrigatório
    if mesa_id is None:
        return Response(
            {'detail': 'ID da mesa não fornecido.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Busca a mesa no banco de dados
    try:
        mesa = MesaTable.objects.get(id=mesa_id)
    except MesaTable.DoesNotExist:
        return Response(
            {'detail': 'Mesa não encontrada no sistema.'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    # Verifica se a mesa possui reservas ativas
    if mesa.existe_reserva:
        return Response(
            {'detail': 'Não é possível remover uma mesa com reservas ativas.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Remove a mesa do sistema
    mesa.delete()
    
    # Limpa reservas expiradas e atualiza o status das mesas
    update_expired_objects()
    
    return Response(
        {'detail': 'Mesa removida com sucesso.'}, 
        status=status.HTTP_204_NO_CONTENT
    )


# ================================================================================================
# ENDPOINTS - AUTENTICAÇÃO
# ================================================================================================

@api_view(['POST'])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
@permission_classes([AllowAny])
def admin_login(request):
    """
    Autentica um usuário administrador via sessão.
    
    Valida credenciais de login e cria uma sessão para o usuário.
    
    Permissions:
        AllowAny - Endpoint público para permitir login.
    
    Request Body (JSON):
        {
            "username": str - Nome de usuário,
            "password": str - Senha do usuário
        }
    
    Returns:
        Response:
            - 200 OK: Autenticação bem-sucedida
                {
                    "detail": "Login realizado com sucesso",
                    "username": str,
                    "is_staff": bool
                }
            - 400 BAD REQUEST: Parâmetros insuficientes
            - 401 UNAUTHORIZED: Credenciais inválidas ou usuário não é admin
    """
    username = request.data.get('username')
    password = request.data.get('password')

    # Validação de parâmetros obrigatórios
    if not username or not password:
        return Response(
            {"detail": "Parâmetros insuficientes. 'username' e 'password' são obrigatórios."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Tenta autenticar o usuário com as credenciais fornecidas
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        # Verifica se o usuário é admin/staff
        if not user.is_staff:
            return Response(
                {"detail": "Acesso negado. Apenas administradores podem fazer login."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Cria sessão para o usuário
        login(request, user)
        
        data = {
            'detail': 'Login realizado com sucesso.',
            'username': user.username,
            'Session Timeout': request.session.get_expiry_age(),
        }
        return Response(data, status=status.HTTP_200_OK)

    # Credenciais inválidas
    return Response(
        {"detail": "Credenciais inválidas. Verifique username e password."}, 
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['POST'])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
@permission_classes([IsAdminUser])
def admin_logout(request):
    """
    Encerra a sessão do administrador.
    
    Permissions:
        IsAdminUser - Apenas administradores autenticados podem fazer logout.
    
    Returns:
        Response:
            - 200 OK: Logout realizado com sucesso
    """
    logout(request)
    return Response(
        {"detail": "Logout realizado com sucesso."}, 
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
@permission_classes([IsAdminUser])
def admin_status(request):
    """
    Verifica o status de autenticação do administrador.
    
    Permissions:
        IsAdminUser - Apenas administradores autenticados.
    
    Returns:
        Response:
            - 200 OK: Usuário autenticado
                {
                    "authenticated": true,
                    "username": str,
                    "is_staff": bool
                }
    """
    return Response(
        {
            "authenticated": True,
            "username": request.user.username,
            "Session Timeout": request.session.get_expiry_age(),
        }, 
        status=status.HTTP_200_OK
    )

# ================================================================================================
# FUNÇÕES AUXILIARES
# ================================================================================================

def update_expired_objects():
    """
    Remove reservas expiradas do sistema e atualiza o status das mesas.
    
    Esta função identifica reservas cuja data é anterior à data atual menos
    BOOKING_EXPIERY_DAYS e as remove do banco de dados. Após a remoção,
    verifica cada mesa associada para atualizar o campo 'existe_reserva'.
    """
    # Remove do sistema todas as reservas cujo término já ultrapassou o período de expiração
    for booking in BookingTable.objects.all():
        booking_end_datetime = datetime.combine(booking.date, booking.end_time)
        expiration_threshold = booking_end_datetime + timedelta(days=BOOKING_EXPIERY_DAYS)

        if expiration_threshold < datetime.now():
            booking.delete()
            print(f"[INFO] A reserva {booking.id} (detalhes da reserva: {booking.mesa}, {booking.name}, {booking.date}, {booking.start_time}, {booking.end_time}, {booking.number_of_guests}, {booking.notes}) expirada removida do sistema.")
    
    for mesa in MesaTable.objects.all():
        # Se a mesa não tiver mais reservas associadas, marca como sem reserva
        if not BookingTable.objects.filter(mesa=mesa).exists():
            mesa.existe_reserva = False
            mesa.save()

# ================================================================================================
# DOCUMENTAÇÃO DA API - RESUMO DE ENDPOINTS
# ================================================================================================

"""
RESUMO COMPLETO DOS ENDPOINTS DA API REST
==========================================

┌─────────────────────────┬──────────────────────────────────────────┬────────────┬───────────────────┐
│ FUNÇÃO                  │ ENDPOINT                                 │ MÉTODO     │ AUTENTICAÇÃO      │
├─────────────────────────┼──────────────────────────────────────────┼────────────┼───────────────────┤
│ GESTÃO DE MESAS                                                                                     │
├─────────────────────────┼──────────────────────────────────────────┼────────────┼───────────────────┤
│ list_mesas              │ /api/mesas/list/                         │ GET        │ AllowAny          │
│ create_mesa             │ /api/mesas/create/                       │ POST       │ IsAdminUser       │
│ delete_mesa             │ /api/mesas/delete/<int:mesa_id>/         │ DELETE     │ IsAdminUser       │
├─────────────────────────┼──────────────────────────────────────────┼────────────┼───────────────────┤
│ GESTÃO DE RESERVAS                                                                                  │
├─────────────────────────┼──────────────────────────────────────────┼────────────┼───────────────────┤
│ view_bookings           │ /api/bookings/list/                      │ GET        │ AllowAny*         │
│ create_booking          │ /api/bookings/create/                    │ POST       │ AllowAny          │
│ cancel_booking          │ /api/bookings/cancel/<int:booking_id>/   │ DELETE     │ IsAdminUser       │
├─────────────────────────┼──────────────────────────────────────────┼────────────┼───────────────────┤
│ AUTENTICAÇÃO                                                                                        │
├─────────────────────────┼──────────────────────────────────────────┼────────────┼───────────────────┤
│ admin_login             │ /api/admin/login/                        │ POST       │ AllowAny          │
│ admin_logout            │ /api/admin/logout/                       │ POST       │ IsAdminUser       │
│ admin_status            │ /api/admin/status/                       │ GET        │ IsAdminUser       │
└─────────────────────────┴──────────────────────────────────────────┴────────────┴───────────────────┘

* view_bookings retorna dados completos para admins e limitados para usuários públicos


DETALHAMENTO DE REQUISIÇÕES
============================

create_booking:
    Body: {
        "name": str (obrigatório),
        "phone": str 9-15 caracteres (obrigatório),
        "date": "YYYY-MM-DD" (obrigatório),
        "time": "HH:MM" (obrigatório),
        "number_of_guests": str|int (obrigatório),
        "notes": str (opcional)
    }

create_mesa:
    Body: {"lugares": int}
    Requer: Cookie de sessão (autenticação via Django)

admin_login:
    Body: {"username": str, "password": str}
    Retorna: Cookie de sessão

admin_logout / admin_status / cancel_booking / delete_mesa:
    Requer: Cookie de sessão (autenticação via Django)


CÓDIGOS HTTP DE RESPOSTA
=========================
    200 OK              - Requisição bem-sucedida
    201 CREATED         - Recurso criado com sucesso
    204 NO CONTENT      - Recurso removido com sucesso
    400 BAD REQUEST     - Parâmetros inválidos ou regra de negócio violada
    401 UNAUTHORIZED    - Credenciais inválidas ou não autenticado
    403 FORBIDDEN       - Sem permissões suficientes
    404 NOT FOUND       - Recurso não encontrado
    500 INTERNAL SERVER - Erro no servidor
"""