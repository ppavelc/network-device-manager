import React from 'react';
import { Outlet } from 'react-router-dom';
import { Box, Typography } from '@mui/material';

const Dashboard = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4">Network Device Manager</Typography>
      <Outlet />
    </Box>
  );
};

export default Dashboard;