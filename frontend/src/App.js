import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import Soundboard from './components/Soundboard';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  return (
    <Router>
      <div className="App">
        <h1>Welcome to the Soundboard App!</h1>
        <Routes>
          {/* login route */}
          <Route path="/login" element={<Login setIsAuthenticated={setIsAuthenticated} />} />
          {/* Register Route */}
          <Route path="/register" element={<Register />} />
          {/* Protected Soundboard Route */}
          <Route 
            path="/soundboard" 
            element={
              isAuthenticated ? (
                <Soundboard setIsAuthenticated={setIsAuthenticated} />
              ) : (
                <Navigate to="/login" />
              )
            } 
          />
          {/* Redirect from root ("/") to login */}
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;