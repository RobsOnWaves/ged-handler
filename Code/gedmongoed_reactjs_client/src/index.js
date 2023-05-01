import React from 'react';
import ReactDOM from 'react-dom/client';
import './App.css';
import App from './App';
import LoginForm from './login';
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(

  <div className="page-body">
    <header>
      <h1>Mon application</h1>
    </header>
    <main>
      <div className="my-component">
        <LoginForm />
      </div>
    </main>
    <footer>
      <p>Tous droits réservés</p>
    </footer>
  </div>

);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
