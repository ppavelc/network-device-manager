import React, { useState } from 'react';
import { TextField, Button, Box, Typography, Table, TableBody, TableCell, TableHead, TableRow } from '@mui/material';
import api from '../api';

const AutomationForm = ({ deviceName }) => {
  const [commands, setCommands] = useState('');
  const [output, setOutput] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post(`/devices/execute/${deviceName}`, { commands: commands.split('\n').filter(cmd => cmd.trim()) });
      setOutput(response.data.output);
    } catch (error) {
      console.error('Execute failed:', error);
      setOutput({ error: 'Failed to execute commands' });
    }
  };

  return (
    <Box>
      <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
        <TextField
          label="Commands (one per line)"
          name="commands"
          value={commands}
          onChange={(e) => setCommands(e.target.value)}
          multiline
          rows={4}
          fullWidth
          margin="normal"
        />
        <Button type="submit" variant="contained">Execute</Button>
      </Box>
      {output && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="h6">Output:</Typography>
          {Object.entries(output).map(([cmd, result]) => (
            <Box key={cmd} sx={{ mb: 2 }}>
              <Typography variant="subtitle1">Command: {cmd}</Typography>
              {result.error ? (
                <Typography color="error">{result.error}</Typography>
              ) : result.parsed.table ? (
                <Table>
                  <TableHead>
                    <TableRow>
                      {Object.keys(result.parsed.table[0]).map((header) => (
                        <TableCell key={header}>{header}</TableCell>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {result.parsed.table.map((row, index) => (
                      <TableRow key={index}>
                        {Object.values(row).map((value, i) => (
                          <TableCell key={i}>{value}</TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <pre>{JSON.stringify(result.parsed, null, 2)}</pre>
              )}
              <Typography variant="caption">Raw Output:</Typography>
              <pre>{result.raw}</pre>
            </Box>
          ))}
        </Box>
      )}
    </Box>
  );
};

export default AutomationForm;