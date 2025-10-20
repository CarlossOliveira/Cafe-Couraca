import React from "react";
import "../../css/styles.css";
import { create_booking } from "../libraries/api";

function ReservationForm({ closeForm }) {
  // Dados padrão do formulário
  const default_formData = {
    name: "",
    phone: "",
    date: "",
    time: "",
    number_of_guests: "",
    notes: "",
  };

  // Estado para armazenar os dados do formulário
  const [formData, setFormData] = React.useState(default_formData);
  const [reservationSuccess, setReservationSuccess] = React.useState(false);
  const [showForm, setShowForm] = React.useState(true);

  // Atualiza o estado com os dados dos inputs
  const handleChange = (input) => {
    // Pega o nome e valor do input que foi alterado
    const inputName = input.target.name;
    const inputValue = input.target.value;

    // Cria uma cópia dos dados atuais e atualiza apenas o campo alterado
    const newFormData = { ...formData }; // Faz Deep Copy do formData
    newFormData[inputName] = inputValue;
    setFormData(newFormData);
  };

  // Função para submeter o formulário
  const handleSubmit = async (event) => {
    event.preventDefault(); // Evitar comportamento padrão de envio

    if (
      formData.name !== "" &&
      formData.phone !== "" &&
      formData.date !== "" &&
      formData.time !== "" &&
      formData.number_of_guests !== ""
    ) {
      // Validação do nome: apenas letras, espaços, hífens, apóstrofos e acentos
      const namePattern = /^[a-zA-ZÀ-ÿ\s'\-]+$/; // Validação Regex
      if (!namePattern.test(formData.name.trim())) {
        alert("Nome inválido. Use apenas letras, espaços, hífens e apóstrofos.");
        return;
      }

      // Validação do comprimento do nome
      if (formData.name.trim().length > 100) {
        alert("O nome não pode ter mais de 100 caracteres.");
        return;
      }

      // Validação do telefone: apenas dígitos e alguns caracteres especiais
      const phoneNumber = formData.phone.replace(/\D/g, ""); // Remove todos os caracteres não numéricos
      if (phoneNumber.length < 9 || phoneNumber.length > 15) {
        alert("Número de telefone inválido.");
        return;
      }

      // Validação do número de pessoas
      const guests = parseInt(formData.number_of_guests, 10);
      if (guests < 1 || guests > 100) {
        alert("Número de pessoas inválido.");
        return;
      }

      // Validação das notas (opcional, mas se preenchido deve ter tamanho válido)
      if (formData.notes.trim().length > 1000) {
        alert("As notas não podem ter mais de 1000 caracteres.");
        return;
      }

      const notesPattern = /^[a-zA-Z0-9À-ÿ\s\.\,\!\?\:\;\'\"\-\(\)]+$/; // Validação Regex
      if (formData.notes.trim() !== "" && !notesPattern.test(formData.notes.trim())) {
        alert("Notas inválidas. Use apenas caracteres alfanuméricos e pontuação comum.");
        return;
      }

      console.log("Form data submitted:", formData);

      // Tenta criar a reserva
      const result = await create_booking(
        formData.name.trim(),
        phoneNumber,
        formData.date,
        formData.time,
        String(guests),
        formData.notes.trim()
      );

      // Verifica se a reserva foi bem-sucedida
      if (result !== -1) {
        setReservationSuccess(true);
        setShowForm(false);
      } else {
        setReservationSuccess(false);
        setShowForm(false);
      }
    }
  };

  // Renderiza o formulário de reserva
  if (showForm) {
    return (
      <form className="form_AT_ReservationForm">
        <h2 className="title_AT_ReservationForm">Fazer uma Reserva</h2>
        <label>
          Nome
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="Introduza o seu nome completo"
            maxLength={100}
            required
          />
        </label>

        <label>
          Telefone
          <input
            type="tel"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            placeholder="+351 912 345 678"
            minLength={9}
            maxLength={16}
            required
          />
        </label>

        <label>
          Data
          <input
            type="date"
            name="date"
            value={formData.date}
            onChange={handleChange}
            required
          />
        </label>

        <label>
          Hora
          <input
            type="time"
            name="time"
            value={formData.time}
            onChange={handleChange}
            required
          />
        </label>

        <label>
          Número de Pessoas
          <input
            type="number"
            name="number_of_guests"
            value={formData.number_of_guests}
            onChange={handleChange}
            placeholder="Quantas pessoas?"
            required
          />
        </label>

        <label>
          Notas de Reserva (Opcional)
          <textarea
            name="notes"
            value={formData.notes}
            onChange={handleChange}
            placeholder="Alguma restrição alimentar ou ocasião especial?"
            maxLength={1000}
          />
        </label>

        <button
          type="submit"
          onClick={handleSubmit}
          className="submitFormButton_AT_ReservationForm"
        >
          Confirmar Reserva
        </button>

        <button
          type="button"
          className="resetFormButton_AT_ReservationForm"
          onClick={() => setFormData(default_formData)}
        >
          Limpar Formulário
        </button>
      </form>
    );
  }

  // Se a reserva foi bem-sucedida, renderiza mensagem de sucesso
  if (reservationSuccess) {
    return (
      <div className="successContainer">
        <h1 className="successTitle">✓ Reserva Confirmada!</h1>
        <p className="successSubtitle">Detalhes da sua reserva:</p>
        <div className="successDetails">
          <p>
            <strong>Nome:</strong> {formData.name}
          </p>
          <p>
            <strong>Telefone:</strong> {formData.phone}
          </p>
          <p>
            <strong>Data:</strong> {formData.date}
          </p>
          <p>
            <strong>Hora:</strong> {formData.time}
          </p>
          <p>
            <strong>Número de Pessoas:</strong> {formData.number_of_guests}
          </p>
          {formData.notes && (
            <p>
              <strong>Notas de Reserva:</strong> {formData.notes}
            </p>
          )}
        </div>
        <p className="successSubtitle" style={{ marginTop: "20px" }}>
          Estamos ansiosos para recebê-lo!
        </p>
        <button
          className="submitFormButton_AT_ReservationForm"
          onClick={() => {
            closeForm();
            setFormData(default_formData);
          }}
        >
          Voltar à Página Inicial
        </button>
      </div>
    );
  } else {
    return (
      <div className="successContainer">
        <h1 className="successTitle" style={{ color: "#dc3545" }}>
          Lamentamos!
        </h1>
        <p className="successSubtitle">
          O nosso Café está totalmente reservado para {formData.date} às {formData.time}.
          Por favor, tente novamente mais tarde ou entre em contato conosco diretamente para mais informações.
        </p>
        <button
          className="submitFormButton_AT_ReservationForm"
          onClick={() => {
            setShowForm(true);
            setFormData(default_formData);
          }}
        >
          Fazer Outra Reserva
        </button>
        <button
          className="resetFormButton_AT_ReservationForm"
          onClick={() => {
            closeForm();
            setFormData(default_formData);
          }}
        >
          Voltar à Página Inicial
        </button>
      </div>
    );
  }
}

export default ReservationForm;
