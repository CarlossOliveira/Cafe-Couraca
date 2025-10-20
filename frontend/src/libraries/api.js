const BACKEND_URL = 'https://localhost:8000'; // Alternative: Use 'http://localhost:5173' to route through Vite proxy (WARNING: Proxy method requires CSRF token configuration in Django (currently not implemented))

// ================================================================================================
// FUNÇÕES PÚBLICAS (Não requerem autenticação)
// ================================================================================================

async function list_mesas() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/mesas/list/`, {
      method: "GET",
      credentials: "include",
    });

    const data = await res.json();
    console.log(data);
    return data;
  } catch (error) {
    console.error("Erro:", error);
    return -1;
  }
}

async function view_bookings() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/bookings/list/`, {
      method: "GET",
      credentials: "include",
    });
    const data = await res.json();
    console.log(data);
    return data;
  } catch (error) {
    console.error("Erro:", error);
    return -1;
  }
}

async function create_booking(name, phone, date, time, number_of_guests, notes = "") {
  if (!name || !phone || !date || !time || !number_of_guests) {
    console.error("Erro: Parâmetros obrigatórios não fornecidos.");
    return -1;
  }
  try {
    const res = await fetch(`${BACKEND_URL}/api/bookings/create/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: name,
        phone: phone,
        date: date,
        time: time,
        number_of_guests: number_of_guests,
        notes: notes,
      }),
    });

    // Verifica se houve erro na criação da reserva
    if (res.status === 400 || res.status === 500) {
      return -1;
    }

    // Retorna os dados da reserva criada
    const data = await res.json();
    console.log(data);
    return data;
  } catch (error) {
    console.error("Erro:", error);
    return -1;
  }
}

// ================================================================================================
// FUNÇÕES DE AUTENTICAÇÃO
// ================================================================================================

async function admin_login(username, password) {
  if (!username || !password) {
    console.error("Erro: Username e password são obrigatórios.");
    return { success: false, error: "Parâmetros obrigatórios não fornecidos" };
  }
  try {
    const res = await fetch(`${BACKEND_URL}/api/admin/login/`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();

    if (res.ok) {
      console.log("Login bem-sucedido:", data);
      return { success: true, ...data };
    } else {
      console.error("Login falhou:", data);
      return { success: false, error: data.detail || "Erro no login" };
    }
  } catch (error) {
    console.error("Erro na requisição de login:", error);
    return { success: false, error: "Erro de conexão" };
  }
}

async function admin_logout() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/admin/logout/`, {
      method: "POST",
      credentials: "include",
    });
    const data = await res.json();
    console.log("Logout:", data);
    return { success: res.ok, ...data };
  } catch (error) {
    console.error("Erro no logout:", error);
    return { success: false, error: "Erro de conexão" };
  }
}

async function admin_status() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/admin/status/`, {
      method: "GET",
      credentials: "include",
    });

    if (res.ok) {
      const data = await res.json();
      return { authenticated: true, ...data };
    } else {
      return { authenticated: false };
    }
  } catch (error) {
    console.error("Erro ao verificar status:", error);
    return { authenticated: false };
  }
}

// ================================================================================================
// FUNÇÕES ADMINISTRATIVAS (Requerem autenticação via sessão)
// ================================================================================================

async function create_mesa(n_lugares) {
  if (!n_lugares) {
    console.error("Erro: Número de lugares é obrigatório.");
    return -1;
  }
  try {
    const res = await fetch(`${BACKEND_URL}/api/mesas/create/`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lugares: n_lugares }),
    });
    const data = await res.json();

    if (res.ok) {
      console.log("Mesa criada:", data);
      return data;
    } else {
      console.error("Erro ao criar mesa:", data);
      return { error: data.detail || "Erro ao criar mesa" };
    }
  } catch (error) {
    console.error("Erro:", error);
    return -1;
  }
}

async function delete_mesa(mesa_id) {
  if (!mesa_id) {
    console.error("Erro: ID da mesa é obrigatório.");
    return -1;
  }
  try {
    const res = await fetch(`${BACKEND_URL}/api/mesas/delete/${mesa_id}/`, {
      method: "DELETE",
      credentials: "include",
    });
    const data = await res.json();

    if (res.ok) {
      console.log("Mesa removida:", data);
      return data;
    } else {
      console.error("Erro ao remover mesa:", data);
      return { error: data.detail || "Erro ao remover mesa" };
    }
  } catch (error) {
    console.error("Erro:", error);
    return -1;
  }
}

async function cancel_booking(booking_id) {
  if (!booking_id) {
    console.error("Erro: ID do booking é obrigatório.");
    return -1;
  }
  try {
    const res = await fetch(
      `${BACKEND_URL}/api/bookings/cancel/${booking_id}/`,
      {
        method: "DELETE",
        credentials: "include",
      }
    );
    const data = await res.json();

    if (res.ok) {
      console.log("Booking cancelado:", data);
      return data;
    } else {
      console.error("Erro ao cancelar booking:", data);
      return { error: data.detail || "Erro ao cancelar booking" };
    }
  } catch (error) {
    console.error("Erro:", error);
    return -1;
  }
}

export {
  list_mesas,
  view_bookings,
  create_booking,
  admin_login,
  admin_logout,
  admin_status,
  create_mesa,
  delete_mesa,
  cancel_booking,
};
