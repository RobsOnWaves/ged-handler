import React, { useState, useEffect } from "react";
import axios from "axios";
import 'bootstrap/dist/css/bootstrap.css';
import { Container, Row, Col, Form, Button } from 'react-bootstrap';
import { API_BASE_URL } from './config';

import OrgChart from './treeview'
import OrgChart2 from './treeviewd3'
import qs from 'qs';

const LoginForm = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleSubmit = event => {
    event.preventDefault();

    // Authenticate with the API using OAuth 2.0
    axios
      .post(API_BASE_URL + "/token", qs.stringify({
        grant_type: "password",
        username,
        password,
        scope: '',
        client_id: "YOUR_CLIENT_ID",
        client_secret: "YOUR_CLIENT_SECRET"
      }, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }))
      .then(response => {
        // Store the access token in local storage
        localStorage.setItem("access_token", response.data.access_token);
        setIsAuthenticated(true);
      })
      .catch(error => {
        console.error(error);
      });
  };

  if (isAuthenticated) {
    return (
      <React.StrictMode>
        <OrgChart />
        <OrgChart2 />
      </React.StrictMode>
    )
  }

  return (

    <Container fluid>
      <Row className="justify-content-center mt-5">
        <Col md={6} style={{ height: '100%' }}>
          <h2 className="text-center">Login</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <input
                type="text"
                placeholder="Username"
                value={username}
                onChange={event => setUsername(event.target.value)}
              />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={event => setPassword(event.target.value)}
              />
            </div>
            <button variant="primary" type="submit">Login</button>
          </form>
        </Col>
      </Row>
    </Container>
  );
};

export default LoginForm;
