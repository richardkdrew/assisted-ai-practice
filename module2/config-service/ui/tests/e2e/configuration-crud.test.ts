import { test, expect } from '@playwright/test';

test.describe('Configuration CRUD Operations', () => {
  let testApplicationId: string;
  let testApplicationName: string;

  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    
    // Wait for the application to load
    await expect(page.locator('app-root')).toBeVisible();
    await expect(page.locator('h1')).toContainText('Config Service Admin');

    // Create a test application for configuration tests
    testApplicationName = `Test App ${Date.now()}`;
    await page.click('button:has-text("Create Application")');
    await page.fill('input[name="name"]', testApplicationName);
    await page.fill('textarea[name="comments"]', 'Test application for configuration tests');
    await page.click('button:has-text("Create Application")');
    
    // Wait for creation to complete
    await expect(page.locator(`text=${testApplicationName}`)).toBeVisible();
    
    // Navigate to configurations view
    await page.click('button:has-text("View Configs")');
    await expect(page.locator('h2:has-text("Configurations")')).toBeVisible();
  });

  test('should display configurations list for application', async ({ page }) => {
    // Check that we're on the configurations view
    await expect(page.locator('h2')).toContainText('Configurations');
    
    // Check breadcrumb navigation
    await expect(page.locator('text=Applications > Configurations')).toBeVisible();
    
    // Check for the create button
    await expect(page.locator('button:has-text("Create Configuration")')).toBeVisible();
  });

  test('should create a new configuration with minimal data', async ({ page }) => {
    // Click create configuration button
    await page.click('button:has-text("Create Configuration")');
    
    // Wait for form to appear
    await expect(page.locator('h3:has-text("Create Configuration")')).toBeVisible();
    
    // Fill in minimal required fields
    await page.fill('input[name="name"]', 'test-config');
    await page.fill('textarea[name="configuration"]', '{"key": "value"}');
    
    // Submit the form
    await page.click('button:has-text("Create Configuration")');
    
    // Wait for the form to disappear and check for success
    await expect(page.locator('h3:has-text("Create Configuration")')).not.toBeVisible();
    
    // Check that the new configuration appears in the list
    await expect(page.locator('text=test-config')).toBeVisible();
  });

  test('should create a new configuration with all fields', async ({ page }) => {
    // Click create configuration button
    await page.click('button:has-text("Create Configuration")');
    
    // Wait for form to appear
    await expect(page.locator('h3:has-text("Create Configuration")')).toBeVisible();
    
    // Fill in all fields
    await page.fill('input[name="name"]', 'full-test-config');
    await page.fill('textarea[name="configuration"]', '{"database": {"host": "localhost", "port": 5432}, "features": {"enabled": true}}');
    await page.fill('textarea[name="comment"]', 'This is a comprehensive test configuration');
    
    // Submit the form
    await page.click('button:has-text("Create Configuration")');
    
    // Wait for the form to disappear and check for success
    await expect(page.locator('h3:has-text("Create Configuration")')).not.toBeVisible();
    
    // Check that the new configuration appears in the list
    await expect(page.locator('text=full-test-config')).toBeVisible();
    await expect(page.locator('text=This is a comprehensive test configuration')).toBeVisible();
  });

  test('should edit an existing configuration', async ({ page }) => {
    // First create a configuration to edit
    await page.click('button:has-text("Create Configuration")');
    await page.fill('input[name="name"]', 'edit-test-config');
    await page.fill('textarea[name="configuration"]', '{"original": "value"}');
    await page.fill('textarea[name="comment"]', 'Original comment');
    await page.click('button:has-text("Create Configuration")');
    
    // Wait for creation to complete
    await expect(page.locator('text=edit-test-config')).toBeVisible();
    
    // Click edit button for the configuration
    await page.click('button:has-text("Edit")');
    
    // Wait for edit form to appear
    await expect(page.locator('h3:has-text("Edit Configuration")')).toBeVisible();
    
    // Modify the form
    await page.fill('input[name="name"]', 'updated-test-config');
    await page.fill('textarea[name="configuration"]', '{"updated": "value", "new_field": 123}');
    await page.fill('textarea[name="comment"]', 'Updated comment');
    
    // Submit the form
    await page.click('button:has-text("Update Configuration")');
    
    // Wait for the form to disappear and check for updates
    await expect(page.locator('h3:has-text("Edit Configuration")')).not.toBeVisible();
    
    // Check that the configuration was updated
    await expect(page.locator('text=updated-test-config')).toBeVisible();
    await expect(page.locator('text=Updated comment')).toBeVisible();
    await expect(page.locator('text=edit-test-config')).not.toBeVisible();
  });

  test('should delete a configuration', async ({ page }) => {
    // First create a configuration to delete
    await page.click('button:has-text("Create Configuration")');
    await page.fill('input[name="name"]', 'delete-test-config');
    await page.fill('textarea[name="configuration"]', '{"to_be": "deleted"}');
    await page.click('button:has-text("Create Configuration")');
    
    // Wait for creation to complete
    await expect(page.locator('text=delete-test-config')).toBeVisible();
    
    // Set up dialog handler for confirmation
    page.on('dialog', dialog => dialog.accept());
    
    // Click delete button
    await page.click('button:has-text("Delete")');
    
    // Check that the configuration was removed
    await expect(page.locator('text=delete-test-config')).not.toBeVisible();
  });

  test('should handle form validation errors', async ({ page }) => {
    // Click create configuration button
    await page.click('button:has-text("Create Configuration")');
    
    // Try to submit empty form
    await page.click('button:has-text("Create Configuration")');
    
    // Check for validation errors
    await expect(page.locator('text=Configuration name is required')).toBeVisible();
    await expect(page.locator('text=Configuration data is required')).toBeVisible();
    
    // Fill in name that's too long
    const longName = 'a'.repeat(300);
    await page.fill('input[name="name"]', longName);
    await page.click('button:has-text("Create Configuration")');
    
    // Check for length validation error
    await expect(page.locator('text=Configuration name must be 256 characters or less')).toBeVisible();
    
    // Test invalid JSON
    await page.fill('input[name="name"]', 'valid-name');
    await page.fill('textarea[name="configuration"]', '{invalid json}');
    await page.click('button:has-text("Create Configuration")');
    
    // Check for JSON validation error
    await expect(page.locator('text=Configuration must be valid JSON')).toBeVisible();
  });

  test('should cancel form creation', async ({ page }) => {
    // Click create configuration button
    await page.click('button:has-text("Create Configuration")');
    
    // Wait for form to appear
    await expect(page.locator('h3:has-text("Create Configuration")')).toBeVisible();
    
    // Fill in some data
    await page.fill('input[name="name"]', 'cancelled-config');
    await page.fill('textarea[name="configuration"]', '{"cancelled": true}');
    
    // Click cancel
    await page.click('button:has-text("Cancel")');
    
    // Check that form disappeared
    await expect(page.locator('h3:has-text("Create Configuration")')).not.toBeVisible();
    
    // Check that the data wasn't saved
    await expect(page.locator('text=cancelled-config')).not.toBeVisible();
  });

  test('should handle empty state', async ({ page }) => {
    // If no configurations exist, should show empty state
    const hasConfigurations = await page.locator('.list-item').count() > 0;
    
    if (!hasConfigurations) {
      await expect(page.locator('text=No configurations found')).toBeVisible();
      await expect(page.locator('text=Create your first configuration to get started')).toBeVisible();
    }
  });

  test('should navigate back to applications', async ({ page }) => {
    // Click on Applications breadcrumb
    await page.click('text=Applications');
    
    // Check that we're back on the applications view
    await expect(page.locator('h2:has-text("Applications")')).toBeVisible();
    
    // Check that our test application is still there
    await expect(page.locator(`text=${testApplicationName}`)).toBeVisible();
  });

  test('should handle complex JSON configuration data', async ({ page }) => {
    // Click create configuration button
    await page.click('button:has-text("Create Configuration")');
    
    // Fill in complex JSON configuration
    const complexConfig = JSON.stringify({
      database: {
        host: "localhost",
        port: 5432,
        credentials: {
          username: "admin",
          password: "secret"
        },
        pools: {
          min: 5,
          max: 20
        }
      },
      features: {
        authentication: true,
        logging: {
          level: "info",
          destinations: ["console", "file"]
        }
      },
      metadata: {
        version: "1.0.0",
        created_by: "test-user",
        tags: ["production", "critical"]
      }
    }, null, 2);
    
    await page.fill('input[name="name"]', 'complex-config');
    await page.fill('textarea[name="configuration"]', complexConfig);
    await page.fill('textarea[name="comment"]', 'Complex configuration with nested objects and arrays');
    
    // Submit the form
    await page.click('button:has-text("Create Configuration")');
    
    // Wait for the form to disappear and check for success
    await expect(page.locator('h3:has-text("Create Configuration")')).not.toBeVisible();
    
    // Check that the new configuration appears in the list
    await expect(page.locator('text=complex-config')).toBeVisible();
    await expect(page.locator('text=Complex configuration with nested objects and arrays')).toBeVisible();
  });

  test('should handle configuration name uniqueness within application', async ({ page }) => {
    const configName = 'unique-config-test';
    
    // Create first configuration
    await page.click('button:has-text("Create Configuration")');
    await page.fill('input[name="name"]', configName);
    await page.fill('textarea[name="configuration"]', '{"first": true}');
    await page.click('button:has-text("Create Configuration")');
    
    // Wait for creation to complete
    await expect(page.locator(`text=${configName}`)).toBeVisible();
    
    // Try to create another configuration with the same name
    await page.click('button:has-text("Create Configuration")');
    await page.fill('input[name="name"]', configName);
    await page.fill('textarea[name="configuration"]', '{"second": true}');
    await page.click('button:has-text("Create Configuration")');
    
    // Check for uniqueness validation error
    await expect(page.locator('text=Configuration name must be unique within the application')).toBeVisible();
  });

  test('should display configuration data preview', async ({ page }) => {
    // Create a configuration with formatted JSON
    await page.click('button:has-text("Create Configuration")');
    await page.fill('input[name="name"]', 'preview-config');
    await page.fill('textarea[name="configuration"]', '{"preview": {"enabled": true, "format": "json"}}');
    await page.click('button:has-text("Create Configuration")');
    
    // Wait for creation to complete
    await expect(page.locator('text=preview-config')).toBeVisible();
    
    // Check if there's a preview or view button
    const hasPreviewButton = await page.locator('button:has-text("View")').count() > 0;
    const hasExpandButton = await page.locator('button:has-text("Expand")').count() > 0;
    
    if (hasPreviewButton) {
      await page.click('button:has-text("View")');
      // Check that configuration data is displayed
      await expect(page.locator('text="preview"')).toBeVisible();
      await expect(page.locator('text="enabled"')).toBeVisible();
    } else if (hasExpandButton) {
      await page.click('button:has-text("Expand")');
      // Check that configuration data is displayed
      await expect(page.locator('text="preview"')).toBeVisible();
      await expect(page.locator('text="enabled"')).toBeVisible();
    }
  });

  test('should display and update configuration key count correctly', async ({ page }) => {
    // Create a configuration with one key
    await page.click('button:has-text("Create Configuration")');
    await page.fill('input[name="name"]', 'key-count-test');
    await page.fill('textarea[name="configuration"]', '{"initial_key": "value"}');
    await page.click('button:has-text("Create Configuration")');
    
    // Wait for creation to complete
    await expect(page.locator('text=key-count-test')).toBeVisible();
    
    // Check that the configuration shows 1 key in the metadata
    await expect(page.locator('text=1 key')).toBeVisible();
    
    // Check that the preview shows "1 configuration key defined"
    await expect(page.locator('text=1 configuration key defined')).toBeVisible();
    
    // Edit the configuration to add more keys
    await page.click('button:has-text("Edit")');
    
    // Wait for edit form to appear
    await expect(page.locator('h3:has-text("Edit Configuration")')).toBeVisible();
    
    // Update with multiple keys
    await page.fill('textarea[name="configuration"]', '{"initial_key": "value", "second_key": "another value", "third_key": 42, "nested": {"inner_key": "nested_value"}}');
    await page.click('button:has-text("Update Configuration")');
    
    // Wait for the form to disappear
    await expect(page.locator('h3:has-text("Edit Configuration")')).not.toBeVisible();
    
    // Check that the configuration now shows 4 keys (top-level keys only)
    await expect(page.locator('text=4 keys')).toBeVisible();
    
    // Check that the preview shows "4 configuration keys defined"
    await expect(page.locator('text=4 configuration keys defined')).toBeVisible();
  });

  test('should handle empty configuration object key count', async ({ page }) => {
    // Create a configuration with empty object
    await page.click('button:has-text("Create Configuration")');
    await page.fill('input[name="name"]', 'empty-config-test');
    await page.fill('textarea[name="configuration"]', '{}');
    await page.click('button:has-text("Create Configuration")');
    
    // Wait for creation to complete
    await expect(page.locator('text=empty-config-test')).toBeVisible();
    
    // Check that the configuration shows 0 keys
    await expect(page.locator('text=0 keys')).toBeVisible();
    
    // Check that the preview shows "0 configuration keys defined"
    await expect(page.locator('text=0 configuration keys defined')).toBeVisible();
  });
});
