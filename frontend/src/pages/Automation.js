import React, { useState, useEffect } from 'react';
import { Box, Typography, FormControl, InputLabel, Select, MenuItem } from '@mui/material';
import api from '../api';
import AutomationForm from '../components/AutomationForm';

const Automation = () => {
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState('');

  useEffect(() => {
    const fetchDevices = async () => {
      try {
        const response = await api.get('/devices/list');
        setDevices(response.data.devices);
      } catch (error) {
        console.error('Fetch devices failed:', error);
      }
    };
    fetchDevices();
  }, []);

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>Automation</Typography>
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel>Select Device</InputLabel>
        <Select value={selectedDevice} onChange={(e) => setSelectedDevice(e.target.value)}>
          {devices.map((name) => (
            <MenuItem key={name} value={name}>{name}</MenuItem>
          ))}
        </Select>
      </FormControl>
      {selectedDevice && <AutomationForm deviceName={selectedDevice} />}
    </Box>
  );
};

export default Automation;