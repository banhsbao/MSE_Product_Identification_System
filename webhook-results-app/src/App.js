import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Container,
  Typography,
  Button,
  Stepper,
  Step,
  StepLabel,
  Paper,
  Box,
  CircularProgress,
  Collapse,
  IconButton,
  Grid
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';

function App() {
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [expandedStep, setExpandedStep] = useState(null);

  const fetchResult = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.get('http://localhost:5005/status');
      setResult(response.data);
    } catch (err) {
      setError('Please start the detection!');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResult(); // Fetch immediately when component mounts
    const intervalId = setInterval(fetchResult, 5000); // Set up polling every 5 seconds

    return () => clearInterval(intervalId); // Cleanup interval on component unmount
  }, []);

  // Prepare steps for Stepper component
  const steps = [
    { label: 'Nhãn', data: result?.body?.step1 },
    { label: 'Mặt A', data: result?.body?.step2 },
    { label: 'Mặt B', data: result?.body?.step3 },
    { label: 'Mặt C', data: result?.body?.step4 },
    { label: 'Mặt D', data: result?.body?.step5 }
  ];

  const handleStepClick = (index) => {
    setExpandedStep(expandedStep === index ? null : index);
  };

  const startDetection = async () => {
    setLoading(true);
    setError('');
    try {
      await axios.get('http://localhost:5005/start_detection');
      await fetchResult(); // Fetch result after starting detection
    } catch (err) {
      setError("Server already started!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" style={{ padding: '20px' }}>
      <Typography variant="h4" align="center" gutterBottom>
        Verify Product Quality
      </Typography>

      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Typography variant="h6" align="center" gutterBottom>
            Live Video Check
          </Typography>
          <img
            src="http://localhost:5005/video_feed"
            alt="Verify Product Quality"
            style={{ width: '100%', borderRadius: '8px', marginBottom: '16px' }}
          />
        </Grid>

        <Grid item xs={12} container direction="row" justifyContent="center" alignItems="center">
          <Button
            variant="contained"
            color="primary"
            onClick={startDetection}
            disabled={loading}
            style={{ marginBottom: '16px', marginRight: '16px' }}
          >
            {loading ? <CircularProgress size={24} /> : 'Start Detection'}
          </Button>
        </Grid>
        <Grid item xs={12} container direction="row" justifyContent="center" alignItems="center">
          {error && (
            <Typography color="error" align="center">
              {error}
            </Typography>
          )}
        </Grid>
      </Grid>
      {result && (
        <Paper elevation={3} style={{ padding: '20px', marginTop: '20px' }}>
          <Typography variant="h6" align="center">Kết quả</Typography>
          <Stepper activeStep={result.step - 1} alternativeLabel>
            {steps.map((step, index) => (
              <Step key={index} onClick={() => handleStepClick(index)} style={{ cursor: 'pointer' }}>
                <StepLabel>{step.label}</StepLabel>
              </Step>
            ))}
          </Stepper>
          <Box mt={2}>
            {steps.map((step, index) => (
              <Collapse key={index} in={expandedStep === index}>
                <Paper elevation={1} style={{ padding: '10px', marginTop: '10px' }}>
                  <Typography variant="h6">{step.label}</Typography>
                  <Typography variant="body1"><strong>Status:</strong> {step.data?.status}</Typography>
                  {step.data?.note && <Typography variant="body1"><strong>Note:</strong> {step.data?.note}</Typography>}
                  {step.data?.caps !== undefined && (
                    <>
                      <Typography variant="body1"><strong>Caps:</strong> {step.data.caps}</Typography>
                      <Typography variant="body1"><strong>Label:</strong> {step.data.label}</Typography>
                      <Typography variant="body1"><strong>Screws:</strong> {step.data.screws}</Typography>
                    </>
                  )}
                  {step.data?.image && (
                    <Box mt={2}>
                      <Typography variant="body1"><strong>Image:</strong></Typography>
                      <img
                        src={`data:image/jpeg;base64,${step.data.image}`}
                        alt={`${step.label} step`}
                        style={{ width: '100%', maxHeight: '400px', objectFit: 'contain', marginTop: '10px' }}
                      />
                    </Box>
                  )}
                  <Box mt={2}>
                    <IconButton onClick={() => handleStepClick(index)} aria-label="toggle-expand">
                      {expandedStep === index ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                    </IconButton>
                  </Box>
                </Paper>
              </Collapse>
            ))}
          </Box>
          <Box mt={2}>
            <pre style={{ background: '#f5f5f5', padding: '10px', borderRadius: '5px', overflowX: 'auto' }}>
              {JSON.stringify(result, null, 2)}
            </pre>
          </Box>
        </Paper>
      )}
    </Container>
  );
}

export default App;
