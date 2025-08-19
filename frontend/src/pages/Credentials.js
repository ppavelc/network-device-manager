import React, { useState, useEffect } from 'react';
import { Box, Typography, List, ListItem, ListItemText, Button } from '@mui/material';
import api from '../api';
import CredentialForm from '../components/CredentialForm';

const Credentials = () => {
  const [credentials, setCredentials] = useState([]);
  const [showForm, setShowForm] = useState(false);

  const fetchCredentials = async () => {
    try {
      const response = await api.get('/credentials/list');
      setCredentials(response.data.credentials);
    } catch (error) {
      console.error('Fetch credentials failed:', error);
    }
  };

  useEffect(() => {
    fetchCredentials();
  }, []);

  const handleDelete = async (username) => {
    try {
      await api.delete(`/credentials/delete/${username}`);
      fetchCredentials();
    } catch (error) {
      console.error('Delete credential failed:', error);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>Credentials</Typography>
      <Button variant="contained" onClick={() => setShowForm(!showForm)}>Add Credential</Button>
      {showForm && <CredentialForm onSuccess={() => { setShowForm(false); fetchCredentials(); }} />}
      <List>
        {credentials.map((username) => (
          <ListItem key={username}>
            <ListItemText primary={username} />
            <Button onClick={() => handleDelete(username)}>Delete</Button>
          </ListItem>
        ))}
      </List>
    </Box>
  );
};

export default Credentials;