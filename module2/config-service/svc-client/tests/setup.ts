import { beforeAll, afterAll } from 'vitest';

// Global test setup
beforeAll(async () => {
  // Set default environment variables for tests
  if (!process.env.CONFIG_SERVICE_API_URL) {
    process.env.CONFIG_SERVICE_API_URL = 'http://localhost:8000/api';
  }
  
  // Add any global setup logic here
  console.log('Setting up integration tests...');
  console.log(`API URL: ${process.env.CONFIG_SERVICE_API_URL}`);
});

afterAll(async () => {
  // Add any global cleanup logic here
  console.log('Cleaning up integration tests...');
});
