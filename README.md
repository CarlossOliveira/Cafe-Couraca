# Café Couraça - Sistema de Reservas

## Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Instalação](#instalação)
  - [Com Docker (Recomendado)](#com-docker-recomendado)
  - [Instalação Local](#instalação-local)
    - [Backend (Django)](#backend-django)
    - [Frontend (React + Vite)](#frontend-react--vite)
- [Acesso ás Interfaces Gráficas](#acesso-às-interfaces-gráficas)
- [Mais Informações Relevantes](#mais-informações-relevantes)
  - [Funcionalidades Adicionais](#funcionalidades-adicionais)
  - [Regras de Reserva Aplicadas](#regras-de-reserva-aplicadas)
  - [API Endpoints](#api-endpoints)
  - [API Rate Limiting](#api-rate-limiting)
  - [Modelos de Dados](#modelos-de-dados)
  - [Autenticação](#autenticação)
- [Notas do Desenvolvedor](#notas-do-desenvolvedor)

## Sobre o Projeto

Sistema de gestão de reservas para o Café Couraça, desenvolvido como desafio técnico para a jeKnowledge. Permite aos clientes fazer reservas online e aos administradores gerir mesas e visualizar reservas.

**⚠️ Projeto em desenvolvimento**: Configurações apenas para ambiente de desenvolvimento local.

## Tecnologias Utilizadas

### Backend

- Python 3.13
- Django 5.2.7
- Django REST Framework 3.15.2
- django-extensions 3.2.3
- SQLite3

### Frontend

- React 19
- Vite 6
- React Router 7
- CSS3

### Infraestrutura

- Docker Compose
- SSL auto-assinado para HTTPS local
- CORS/CSRF protection

## Instalação

### Com Docker (Recomendado)

1. **Clone o repositório e navegue até à pasta do projeto**:

   ```bash
   git clone <url-do-repositório>
   cd "Café Couraça"
   ```

2. **Inicie os serviços**:

   ```bash
   docker-compose up -d
   ```

3. **Crie um superutilizador para aceder ao painel de administração**:
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

#### Gestão de Volumes e Containers Docker (Comandos Úteis)

**Listar containers (Em execução e Parados)**:

```bash
docker ps -a
```

**Parar containers**:

```bash
docker-compose down
```

**Remover containers**:

```bash
docker rm -f <id_do_container>
```

**A base de dados está montada como bind mount. Para gerir:**

**Listar volumes**:

```bash
docker volume ls
```

**Remover volume** (apaga todos os dados):

```bash
docker volume rm <nome_do_volume>
```

### Instalação Local

**Clone o repositório e navegue até à pasta do projeto**:

```bash
git clone <url-do-repositório>
cd "Café Couraça"
```

#### Backend (Django)

1. **Navegue até à pasta do backend**:

   ```bash
   cd backend
   ```

2. **Crie um ambiente virtual**:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instale as dependências**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Execute as migrações**:

   ```bash
   python manage.py migrate
   ```

5. **Crie um superutilizador**:

   ```bash
   python manage.py createsuperuser
   ```

6. **Inicie o servidor Django com SSL**:
   ```bash
   python manage.py runserver_plus --cert-file certs/dev-cert.pem --key-file certs/dev-key.pem
   ```

#### Frontend (React + Vite)

1. **Abra um novo terminal e navegue até à pasta do frontend**:

   ```bash
   cd frontend
   ```

2. **Instale as dependências**:

   ```bash
   npm install
   ```

3. **Inicie o servidor de desenvolvimento**:
   ```bash
   npm run dev
   ```

## **Acesso às Interfaces Gráficas**:

- **Frontend**: http://localhost:5173
- **Backend API**: https://localhost:8000/api/
- **Painel Admin**: http://localhost:5173/admin/ (ou via backend diretamente em https://localhost:8000/admin/)

**Nota sobre certificados SSL**: O navegador irá avisar sobre certificado auto-assinado. Aceite o risco para continuar.

## Mais Informações Relevantes

### Funcionalidades Adicionais

#### Backend

1. **Lógica de remoção automática de reservas passadas**
2. **Conteinarização dos servidores de backend e frontend usando Docker**
3. **Comunicação entre os servidores de frontend e backend via https com certificados autoassinados**
4. **Reverse proxy da interface administrativa do Django (página do Staff)**
5. **Rate Limiting das APIs criadas**
6. **Hot Reload usando Vite**
7. **CORS e CSRF**

#### Frontend

1. **iframe com menu oficial do Café Couraça**
2. **Links para as redes socias, localização e contactos do Café Couraça**

### Regras de Reserva Aplicadas

- Reservas com mais de 16 dias são automaticamente removidas
- Não é possível reservar a mesma mesa para horários sobrepostos
- Duração fixa de 1h15min por reserva
- As reservas só podem ser marcadas para intervalos de tampo dentro do horário de funcionamento disponibilizado no google à data de 19/10/2025.

### API Endpoints

Todas as rotas da API estão sob o prefixo `/api/`.

| Endpoint                | Método | Autenticação | Descrição                                   |
| ----------------------- | ------ | ------------ | ------------------------------------------- |
| `/api/bookings/create/` | POST   | Não          | Criar nova reserva                          |
| `/api/bookings/view/`   | GET    | Sim (Sessão) | Listar todas as reservas (admin)            |
| `/api/bookings/view/`   | GET    | Não          | Listar horários e mesas ocupadas            |
| `/api/bookings/cancel/` | POST   | Sim (Sessão) | Cancelar reserva existente (admin)          |
| `/api/mesas/list/`      | GET    | Não          | Listar todas as mesas disponíveis           |
| `/api/mesas/create/`    | POST   | Sim (Sessão) | Criar nova mesa (admin)                     |
| `/api/mesas/delete/`    | POST   | Sim (Sessão) | Eliminar mesa (admin)                       |
| `/api/admin/login/`     | POST   | Não          | Login de administrador (cria sessão Django) |
| `/api/admin/logout/`    | POST   | Sim (Sessão) | Logout de administrador (termina sessão)    |
| `/api/admin/status/`    | GET    | Sim (Sessão) | Verificar estado de autenticação            |

### API Rate Limiting

- **Utilizadores autenticados**: 15 requisições/minuto
- **Utilizadores anónimos**: 10 requisições/minuto

### Modelos de Dados

#### Mesa

- `id`: ID único (autogerado)
- `lugares`: Capacidade (número de lugares)
- `existe_reserva`: Boolean - indica se tem reserva ativa no momento

#### Booking (Reserva)

- `id`: ID único (autogerado)
- `mesa`: Foreign Key para Mesa
- `name`: Nome do cliente (validado: apenas letras, acentos, espaços, hífens, apóstrofos)
- `phone`: Telefone (normalizado: 9-15 dígitos, sem formatação)
- `date`: Data da reserva
- `start_time`: Hora de início
- `end_time`: Hora de término (calculada automaticamente: `start_time + 1h15min`)
- `number_of_guests`: Número de convidados (1-100)
- `notes`: Observações opcionais

### Autenticação

O sistema usa **autenticação por sessão Django**. Após login bem-sucedido em `/api/admin/login/`, o Django cria uma sessão com duração de 2 horas. As credenciais são enviadas automaticamente via cookies em requisições subsequentes.

## Notas do Desenvolvedor:

Com um conhecimento inicial predominantemente teórico na área de desenvolvimento web, nos últimos dias, fui motivado a adquirir competências práticas em diversas linguagens e frameworks essenciais para a execução deste projeto. Nesse sentido, é importante destacar que o desenvolvimento foi amplamente baseado em tutoriais, modelos de linguagem (LLMs) e na documentação oficial das tecnologias presentes na stack adotada. Da mesma forma, tanto a documentação técnica como os comentários no código foram, em grande parte, elaborados ou otimizados com o auxílio de LLMs, com o objetivo de assegurar uma estrutura de documentação clara, coesa e de fácil entendimento ao longo de todo o projeto.

Tenho plena consciência que desenvolvi um número considerável de APIs que, na versão final do projeto, acabaram por não ter aplicação prática. Tal deveu-se ao facto de, a meio do processo de desenvolvimento, me ter sido transmitida uma orientação que recomendava a utilização da interface de administração por defeito do Django como solução adequada para a gestão das operações administrativas descritas no enunciado do projeto, em detrimento da criação de uma interface personalizada para esse efeito.

Considerei também pertinente a adopção de Docker, tendo em conta a natureza do projeto, uma vez que esta ferramenta acrescenta um nível significativo de simplificação ao processo de configuração e execução da aplicação. Acresce ainda a sua versatilidade e escalabilidade, permitindo inclusivamente a integração com soluções como Kubernetes, algo que se revela particularmente relevante no contexto do desenvolvimento web moderno.

Adicionei igualmente uma reverse proxy utilizando o Vite, com o objetivo de expor a interface do painel de administração através do frontend, limitando, assim, as conexões diretas ao servidor backend.

Como entusiasta da área de cibersegurança, desenvolvi esta plataforma com o objetivo de adotar uma arquitetura tão robusta quanto possível, considerando o seu uso em ambiente de desenvolvimento. No entanto, reconheço que algumas decisões de implementação, nomeadamente, a utilização do reverse proxy do Vite, que expõe diretamente a interface do backend ao público, oa a escolha de servir o backend com certificados através do "runserver_plus", em vez de utilizar um reverse proxy dedicado para assegurar a comunicação entre o frontend e o backend, não são adequadas para ambientes de produção e podem introduzir vulnerabilidades relevantes. Este projeto foi concebido exclusivamente com fins de desenvolvimento e aprendizagem, procurando integrar o maior número possível de conceitos e funcionalidades que domino atualmente. Ao mesmo tempo, tentando manter a complexidade do projeto dentro de limites controlados, de forma a não comprometer o foco na tarefa principal proposta.

Por fim, estou ciente de que, apesar de o projeto ter sido disponibilizado através de um repositório no GitHub, não existe um registo completo e estruturado de commits desde o início do desenvolvimento. Esta situação resulta do facto de me encontrar numa fase inicial de aprendizagem, o que implicou múltiplas reformulações do repositório (incluindo a sua eliminação e recriação) tornando o histórico de versões intermédias pouco representativo e desorganizado. Face a isto, optei por disponibilizar apenas a versão final, estável e funcional, neste repositório.

---

**Desenvlvido Por:** Carlos Oliveira
