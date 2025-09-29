/**
 * Main application entry point
 */

// Import all components to register them
import './components/base/BaseComponent';
import './components/base/ComponentRegistry';
import './components/routing/AppRouter';
import './components/layout/AppMain';
import './components/application/ApplicationList';
import './components/application/ApplicationForm';
import './components/configuration/ConfigurationList';
import './components/configuration/ConfigurationForm';

// Import services
import './services/BaseService';
import './services/ApplicationService';
import './services/ConfigurationService';

// Import types
import './types/domain';

// Initialize the application
function initializeApp(): void {
  // Wait for DOM to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
    return;
  }

  // Create and mount the main application component
  const appRoot = document.getElementById('app');
  if (appRoot) {
    appRoot.innerHTML = '<app-router></app-router>';
  } else {
    console.error('App root element not found. Make sure you have an element with id="app" in your HTML.');
  }
}

// Start the application
initializeApp();