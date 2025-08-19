import React, { useState } from 'react';
import { TextField, Button, Box } from '@mui/material';
import api from '../api';

const CredentialForm = ({ onSuccess }) => {
  const [formData, setFormData] = useState({ username: '', password: '' });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/credentials/add/', formData);
      onSuccess();
    } catch (error) {
      console.error('Add credential failed:', error);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
      <TextField label="Username" name="username" value={formData.username} onChange={handleChange} fullWidth margin="normal" />
      <TextField label="Password" name="password" type="password" value={formData.password} onChange={handleChange} fullWidth margin="normal" />
      <Button type="submit" variant="contained">Add Credential</Button>
    </Box>
  );
};

export default CredentialForm;