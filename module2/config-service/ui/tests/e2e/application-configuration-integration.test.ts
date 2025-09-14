import { test, expect } from '@playwright/test';

test.describe('Application and Configuration Integration Tests', () => {
  test('should create application and multiple configurations end-to-end', async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    await expect(page.locator('app-root')).toBeVisible();
    await expect(page.locator('h1')).toContainText('Config Service Admin');

    // Create a new application
    const appName = `Integration Test App ${Date.now()}`;
    await page.click('button:has-text("Create Application")');
    await page.fill('input[name="name"]', appName);
    await page.fill('textarea[name="comments"]', 'Application for integration testing');
    await page.click('button:has-text("Create Application")');
    
    // Verify application was created
    await expect(page.locator(`text=${appName}`)).toBeVisible();
    
    // Navigate to configurations
    await page.click('button:has-text("View Configs")');
    await expect(page.locator('h2:has-text("Configurations")')).toBeVisible();
    
    // Create first configuration - Database config
    await page.click('button:has-text("Create Configuration")');
    await page.fill('input[name="name"]', 'database-config');
    await page.fill('textarea[name="configuration"]', JSON.stringify({
      host: "localhost",
      port: 5432,
      database: "myapp",
      username: "admin",
      ssl: true
    }, null, 2));
    await page.fill('textarea[name="comment"]', 'Database connection configuration');
    await page.click('button:has-text("Create Configuration")');
    
    // Verify first configuration was created
    await expect(page.locator('text=database-config')).toBeVisible();
    
    // Create second configuration - API config
    await page.click('button:has-text("Create Configuration")');
    await page.fill('input[name="name"]', 'api-config');
    await page.fill('textarea[name="configuration"]', JSON.stringify({
      baseUrl: "https://api.example.com",
      timeout: 30000,
      retries: 3,
      authentication: {
        type: "bearer",
        tokenEndpoint: "/auth/token"
      }
    }, null, 2));
    await page.fill('textarea[name="comment"]', 'API client configuration');
    await page.click('button:has-text("Create Configuration")');
    
    // Verify second configuration was created
    await expect(page.locator('text=api-config')).toBeVisible();
    
    // Create third configuration - Feature flags
    await page.click('button:has-text("Create Configuration")');
    await page.fill('input[name="name"]', 'feature-flags');
    await page.fill('textarea[name="configuration"]', JSON.stringify({
      enableNewUI: true,
      enableBetaFeatures: false,
      maxUploadSize: 10485760,
      supportedFormats: ["jpg", "png", "pdf"]
    }, null, 2));
    await page.fill('textarea[name="comment"]', 'Feature flag configuration');
    await page.click('button:has-text("Create Configuration")');
    
    // Verify third configuration was created
    await expect(page.locator('text=feature-flags')).toBeVisible();
    
    // Verify all three configurations are visible
    await expect(page.locator('text=database-config')).toBeVisible();
    await expect(page.locator('text=api-config')).toBeVisible();
    await expect(page.locator('text=feature-flags')).toBeVisible();
    
    // Edit one of the configurations
    await page.locator('text=api-config').locator('..').locator('button:has-text("Edit")').click();
    await page.fill('input[name="name"]', 'api-client-config');
    await page.fill('textarea[name="comment"]', 'Updated API client configuration');
    await page.click('button:has-text("Update Configuration")');
    
    // Verify the configuration was updated
    await expect(page.locator('text=api-client-config')).toBeVisible();
    await expect(page.locator('text=Updated API client configuration')).toBeVisible();
    await expect(page.locator('text=api-config')).not.toBeVisible();
    
    // Navigate back to applications
    await page.click('text=Applications');
    await expect(page.locator('h2:has-text("Applications")')).toBeVisible();
    
    // Verify the application still exists
    await expect(page.locator(`text=${appName}`)).toBeVisible();
    
    // Navigate back to configurations to verify they're still there
    await page.click('button:has-text("View Configs")');
    await expect(page.locator('text=database-config')).toBeVisible();
    await expect(page.locator('text=api-client-config')).toBeVisible();
    await expect(page.locator('text=feature-flags')).toBeVisible();
  });

  test('should handle application deletion with configurations', async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    await expect(page.locator('app-root')).toBeVisible();

    // Create a new application
    const appName = `Delete Test App ${Date.now()}`;
    await page.click('button:has-text("Create Application")');
    await page.fill('input[name="name"]', appName);
    await page.fill('textarea[name="comments"]', 'Application to be deleted');
    await page.click('button:has-text("Create Application")');
    
    // Verify application was created
    await expect(page.locator(`text=${appName}`)).toBeVisible();
    
    // Navigate to configurations and create one
    await page.click('button:has-text("View Configs")');
    await page.click('button:has-text("Create Configuration")');
    await page.fill('input[name="name"]', 'temp-config');
    await page.fill('textarea[name="configuration"]', '{"temporary": true}');
    await page.click('button:has-text("Create Configuration")');
    
    // Verify configuration was created
    await expect(page.locator('text=temp-config')).toBeVisible();
    
    // Navigate back to applications
    await page.click('text=Applications');
    
    // Set up dialog handler for confirmation
    page.on('dialog', dialog => dialog.accept());
    
    // Delete the application
    await page.locator(`text=${appName}`).locator('..').locator('button:has-text("Delete")').click();
    
    // Verify application was deleted
    await expect(page.locator(`text=${appName}`)).not.toBeVisible();
  });

  test('should handle multiple applications with configurations', async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    await expect(page.locator('app-root')).toBeVisible();

    // Create first application
    const app1Name = `Multi App 1 ${Date.now()}`;
    await page.click('button:has-text("Create Application")');
    await page.fill('input[name="name"]', app1Name);
    await page.fill('textarea[name="comments"]', 'First application');
    await page.click('button:has-text("Create Application")');
    
    // Create configuration for first app
    await page.click('button:has-text("View Configs")');
    await page.click('button:has-text("Create Configuration")');
    await page.fill('input[name="name"]', 'app1-config');
    await page.fill('textarea[name="configuration"]', '{"app": 1}');
    await page.click('button:has-text("Create Configuration")');
    
    // Verify first app configuration
    await expect(page.locator('text=app1-config')).toBeVisible();
    
    // Navigate back to applications
    await page.click('text=Applications');
    
    // Create second application
    const app2Name = `Multi App 2 ${Date.now()}`;
    await page.click('button:has-text("Create Application")');
    await page.fill('input[name="name"]', app2Name);
    await page.fill('textarea[name="comments"]', 'Second application');
    await page.click('button:has-text("Create Application")');
    
    // Create configuration for second app
    await page.click('button:has-text("View Configs")');
    await page.click('button:has-text("Create Configuration")');
    await page.fill('input[name="name"]', 'app2-config');
    await page.fill('textarea[name="configuration"]', '{"app": 2}');
    await page.click('button:has-text("Create Configuration")');
    
    // Verify second app configuration
    await expect(page.locator('text=app2-config')).toBeVisible();
    
    // Navigate back to applications
    await page.click('text=Applications');
    
    // Verify both applications exist
    await expect(page.locator(`text=${app1Name}`)).toBeVisible();
    await expect(page.locator(`text=${app2Name}`)).toBeVisible();
    
    // Check first app configurations
    await page.locator(`text=${app1Name}`).locator('..').locator('button:has-text("View Configs")').click();
    await expect(page.locator('text=app1-config')).toBeVisible();
    await expect(page.locator('text=app2-config')).not.toBeVisible();
    
    // Navigate back and check second app configurations
    await page.click('text=Applications');
    await page.locator(`text=${app2Name}`).locator('..').locator('button:has-text("View Configs")').click();
    await expect(page.locator('text=app2-config')).toBeVisible();
    await expect(page.locator('text=app1-config')).not.toBeVisible();
  });

  test('should handle configuration operations across application navigation', async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    await expect(page.locator('app-root')).toBeVisible();

    // Create application
    const appName = `Navigation Test App ${Date.now()}`;
    await page.click('button:has-text("Create Application")');
    await page.fill('input[name="name"]', appName);
    await page.click('button:has-text("Create Application")');
    
    // Navigate to configurations
    await page.click('button:has-text("View Configs")');
    
    // Create initial configuration
    await page.click('button:has-text("Create Configuration")');
    await page.fill('input[name="name"]', 'nav-test-config');
    await page.fill('textarea[name="configuration"]', '{"initial": true}');
    await page.click('button:has-text("Create Configuration")');
    
    // Navigate away and back multiple times
    await page.click('text=Applications');
    await expect(page.locator('h2:has-text("Applications")')).toBeVisible();
    
    await page.click('button:has-text("View Configs")');
    await expect(page.locator('text=nav-test-config')).toBeVisible();
    
    // Edit configuration after navigation
    await page.click('button:has-text("Edit")');
    await page.fill('textarea[name="configuration"]', '{"initial": false, "updated": true}');
    await page.fill('textarea[name="comment"]', 'Updated after navigation');
    await page.click('button:has-text("Update Configuration")');
    
    // Verify update persisted
    await expect(page.locator('text=Updated after navigation')).toBeVisible();
    
    // Navigate away and back again
    await page.click('text=Applications');
    await page.click('button:has-text("View Configs")');
    
    // Verify configuration is still updated
    await expect(page.locator('text=nav-test-config')).toBeVisible();
    await expect(page.locator('text=Updated after navigation')).toBeVisible();
  });

  test('should handle error scenarios in integrated workflow', async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    await expect(page.locator('app-root')).toBeVisible();

    // Create application
    const appName = `Error Test App ${Date.now()}`;
    await page.click('button:has-text("Create Application")');
    await page.fill('input[name="name"]', appName);
    await page.click('button:has-text("Create Application")');
    
    // Navigate to configurations
    await page.click('button:has-text("View Configs")');
    
    // Try to create configuration with invalid JSON
    await page.click('button:has-text("Create Configuration")');
    await page.fill('input[name="name"]', 'error-config');
    await page.fill('textarea[name="configuration"]', '{invalid: json}');
    await page.click('button:has-text("Create Configuration")');
    
    // Verify error handling
    await expect(page.locator('text=Configuration must be valid JSON')).toBeVisible();
    
    // Fix the JSON and submit
    await page.fill('textarea[name="configuration"]', '{"valid": "json"}');
    await page.click('button:has-text("Create Configuration")');
    
    // Verify successful creation after error
    await expect(page.locator('text=error-config')).toBeVisible();
    
    // Try to create duplicate configuration name
    await page.click('button:has-text("Create Configuration")');
    await page.fill('input[name="name"]', 'error-config');
    await page.fill('textarea[name="configuration"]', '{"duplicate": true}');
    await page.click('button:has-text("Create Configuration")');
    
    // Verify uniqueness error
    await expect(page.locator('text=Configuration name must be unique within the application')).toBeVisible();
    
    // Cancel the form
    await page.click('button:has-text("Cancel")');
    
    // Verify only one configuration exists
    const configCount = await page.locator('text=error-config').count();
    expect(configCount).toBe(1);
  });
});
