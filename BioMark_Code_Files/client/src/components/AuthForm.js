import React, { useState } from 'react';
import { api } from '../api';

export default function AuthForm({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (endpoint) => {
    setError('');
    try {
      const response = await api.post(`/auth/${endpoint}`, { email, password });
      if (response.data.token) {
        localStorage.setItem('token', response.data.token);
        onLogin(response.data.token);
      } else {
        setError('Login/signup failed');
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Error occurred');
    }
  };

  const handleGuest = async () => {
    try {
        const response = await api.post('/auth/guest');
        if (response.data.token) {
            localStorage.setItem('token', response.data.token);
            onLogin(response.data.token);
        }
    } catch (err) {
        setError('Guest login failed');
    }
};


  return (
    <div>
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button onClick={() => handleSubmit('login')}>Login</button>
      <button onClick={() => handleSubmit('signup')}>Sign up</button>
      <button onClick={handleGuest}>Continue as Guest</button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}
