import React, { useState } from 'react';
import { TextField, Button, Box } from '@mui/material';
import api from '../api';

const DeviceForm = ({ onDeviceAdded }) => {
  const [name, setName] = useState('');
  const [ip, setIp] = useState('');
  const [deviceType, setDeviceType] = useState('generic');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/devices/add/', { name, ip, device_type: deviceType, username, password });
      onDeviceAdded();
      setName('');
      setIp('');
      setDeviceType('generic');
      setUsername('');
      setPassword('');
    } catch (error) {
      console.error('Add device failed:', error);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
      <TextField label="Name" value={name} onChange={(e) => setName(e.target.value)} fullWidth margin="normal" />
      <TextField label="IP Address" value={ip} onChange={(e) => setIp(e.target.value)} fullWidth margin="normal" />
      <TextField label="Device Type" value={deviceType} onChange={(e) => setDeviceType(e.target.value)} fullWidth margin="normal" />
      <TextField label="Username" value={username} onChange={(e) => setUsername(e.target.value)} fullWidth margin="normal" />
      <TextField label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} fullWidth margin="normal" />
      <Button type="submit" variant="contained">Add Device</Button>
    </Box>
  );
};

export default DeviceForm;