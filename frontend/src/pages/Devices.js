import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Box, Typography, Table, TableBody, TableCell, TableHead, TableRow, Dialog, DialogTitle, DialogContent, DialogActions, TextField } from '@mui/material';
import api from '../api';

const Devices = () => {
  const [devices, setDevices] = useState([]);
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({ name: '', ip: '', device_type: '', username: '', password: '' });
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDevices = async () => {
      try {
        const response = await api.get('/devices/list');
        console.log('Devices response:', response.data); // Debug log
        setDevices(response.data.devices);
      } catch (error) {
        console.error('Error fetching devices:', error);
        if (error.response && error.response.status === 401) {
          navigate('/');
        }
      }
    };
    fetchDevices();
  }, [navigate]);

  const handleOpen = () => setOpen(true);
  const handleClose = () => {
    setOpen(false);
    setFormData({ name: '', ip: '', device_type: '', username: '', password: '' });
  };

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/devices/add/', formData);
      handleClose();
      const response = await api.get('/devices/list');
      setDevices(response.data.devices);
    } catch (error) {
      console.error('Error adding device:', error);
    }
  };

  const handleDelete = async (deviceId) => {
    try {
      await api.delete(`/devices/${deviceId}`);
      const response = await api.get('/devices/list');
      setDevices(response.data.devices);
    } catch (error) {
      console.error('Error deleting device:', error);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>Devices</Typography>
      <Button variant="contained" onClick={handleOpen} sx={{ mb: 2 }}>
        Add Device
      </Button>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>IP</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Username</TableCell>
            <TableCell>Identified Type</TableCell>
            <TableCell>Model</TableCell>
            <TableCell>Version</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {devices.map((device) => (
            <TableRow key={device.device_id}>
              <TableCell>{device.name}</TableCell>
              <TableCell>{device.ip}</TableCell>
              <TableCell>{device.device_type}</TableCell>
              <TableCell>{device.username}</TableCell>
              <TableCell>{device.identified_type}</TableCell>
              <TableCell>{device.model}</TableCell>
              <TableCell>{device.version}</TableCell>
              <TableCell>
                <Button color="error" onClick={() => handleDelete(device.device_id)}>
                  Delete
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>Add Device</DialogTitle>
        <DialogContent>
          <TextField
            label="Name"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            fullWidth
            margin="normal"
          />
          <TextField
            label="IP Address"
            name="ip"
            value={formData.ip}
            onChange={handleInputChange}
            fullWidth
            margin="normal"
          />
          <TextField
            label="Device Type"
            name="device_type"
            value={formData.device_type}
            onChange={handleInputChange}
            fullWidth
            margin="normal"
          />
          <TextField
            label="Username"
            name="username"
            value={formData.username}
            onChange={handleInputChange}
            fullWidth
            margin="normal"
          />
          <TextField
            label="Password"
            name="password"
            type="password"
            value={formData.password}
            onChange={handleInputChange}
            fullWidth
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">Add</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Devices;