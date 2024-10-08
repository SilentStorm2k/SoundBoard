// components/Login.js
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

function Login({ setIsAuthenticated }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      console.warn(`Backend url :${process.env.REACT_APP_BACKEND_URL}`);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/auth/jwt/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `username=${email}&password=${password}`,
      });
      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        setIsAuthenticated(true);
        navigate('/soundboard');
      } else {
        alert('Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
    }
  };

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">Login</button>
      </form>
      <Link to="/register">Register</Link>
    </div>
  );
}

export default Login;