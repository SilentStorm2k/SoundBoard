import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Switch, Redirect } from 'react-router-dom';
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
        <Switch>
          <Route path="/login" render={(props) => <Login {...props} setIsAuthenticated={setIsAuthenticated} />} />
          <Route path="/register" component={Register} />
          <Route
            path="/soundboard"
            render={(props) =>
              isAuthenticated ? (
                <Soundboard {...props} setIsAuthenticated={setIsAuthenticated} />
              ) : (
                <Redirect to="/login" />
              )
            }
          />
          <Redirect from="/" to="/login" />
        </Switch>
      </div>
    </Router>
  );
}

export default App;