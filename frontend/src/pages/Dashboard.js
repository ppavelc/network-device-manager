import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { Box, Typography } from '@mui/material';

const Dashboard = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4">Network Device Manager</Typography>
      <Box sx={{ mt: 2 }}>
        <Link to="devices">Devices</Link> | <Link to="credentials">Credentials</Link> | <Link to="automation">Automation</Link>
      </Box>
      <Outlet />
    </Box>
  );
};

export default Dashboard;