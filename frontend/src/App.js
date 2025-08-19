import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { useTheme } from './contexts/ThemeContext';
import CssBaseline from '@mui/material/CssBaseline';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Devices from './pages/Devices';
import Credentials from './pages/Credentials';
import Automation from './pages/Automation';

function App() {
  const { mode } = useTheme();
  const theme = createTheme({
    palette: {
      mode: mode,
    },
  });

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router future={{ v7_startTransition: false, v7_relativeSplatPath: false }}>
          <Routes>
            <Route path="/" element={<Login />} />
            <Route path="/dashboard" element={<Dashboard />}>
              <Route path="devices" element={<Devices />} />
              <Route path="credentials" element={<Credentials />} />
              <Route path="automation" element={<Automation />} />
              <Route path="" element={<Devices />} /> {/* Default route under /dashboard */}
            </Route>
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;