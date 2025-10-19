import ReservationForm from '../components/ReservationForm';
import React from 'react';

function HomePage() {
  const [showForm, setShowForm] = React.useState(false);

  return (
    <div className='mainPage'>
      <h1 className='mainTittle'>Seja bem-vindo ao Café Couraça</h1>
      {!showForm && (
        <div className='mainPage'>
          <h2>✧ O Nosso Menu ✧</h2>
          <iframe src="https://drive.google.com/file/d/131m4TZ-sWUWefIM4nrP54_D--XGAprQ6/preview" style={{borderRadius: '8px'}} width="640" height="480" allow="autoplay"></iframe>
          <p className='mainPageText'>Venha nos Conhecer!</p>
          <button onClick={() => setShowForm(true)} className='mainPageButton'>
          Reservar uma Mesa
        </button>
        </div>
      )}
      {showForm && (
          <ReservationForm className='formContainer' closeForm={() => setShowForm(false)} />
      )}
      <div className='Rodapé'>
        <div className='socialMediaLinks'>
          <a className='socialMediaLink' href='https://maps.app.goo.gl/gFmutm63Curz4k8T8' target='_blank'>
            <img src='/Map Logo.svg' alt='Location' />
            <p style={{ textAlign: "center", justifyContent: "center" }}>Couraça de Lisboa 30, 3000-434 Coimbra</p>
          </a>
          <a className='socialMediaLink' href='tel:+351960153729'>
            <img style={{ width: "24px", height: "24px" }} src='/Phone Logo.svg' alt='phone' />
            <p style={{ textAlign: "center", justifyContent: "center" }}>+351 960 153 729</p>
          </a>
          <a className='socialMediaLink' href='https://www.facebook.com/share/16p7rzV6Ys/?mibextid=wwXIfr' target='_blank'>
            <img src='/Facebook Logo.svg' alt='Facebook' />
          </a>
          <a className='socialMediaLink' href='https://www.instagram.com/cafecouraca?igsh=MWswNTQ5MGR6MnNzMw==' target='_blank'>
            <img src='/Instagram Logo.svg' alt='Instagram' />
          </a>
        </div>
          <div className='copyright'>
          <p style={{ textAlign: "center", position: "relative", bottom: "0" }}>© 2025 Café Couraça. Todos os direitos reservados.</p>
        </div>
      </div>
    </div>

  );
}

export default HomePage;