import { test, expect } from '@playwright/test';

test.describe('Application CRUD Operations', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    
    // Wait for the application to load
    await expect(page.locator('app-root')).toBeVisible();
    await expect(page.locator('h1')).toContainText('Config Service Admin');
  });

  test('should display applications list', async ({ page }) => {
    // Check that we're on the applications view by default
    await expect(page.locator('h2')).toContainText('Applications');
    
    // Check for the create button
    await expect(page.locator('button:has-text("Create Application")')).toBeVisible();
  });

  test('should create a new application', async ({ page }) => {
    // Click create application button
    await page.click('button:has-text("Create Application")');
    
    // Wait for form to appear
    await expect(page.locator('h3:has-text("Create Application")')).toBeVisible();
    
    // Fill in the form
    await page.fill('input[name="name"]', 'Test Application');
    await page.fill('textarea[name="comments"]', 'This is a test application');
    
    // Submit the form
    await page.click('button:has-text("Create Application")');
    
    // Wait for the form to disappear and check for success
    await expect(page.locator('h3:has-text("Create Application")')).not.toBeVisible();
    
    // Check that the new application appears in the list
    await expect(page.locator('text=Test Application')).toBeVisible();
    await expect(page.locator('text=This is a test application')).toBeVisible();
  });

  test('should edit an existing application', async ({ page }) => {
    // First create an application to edit
    await page.click('button:has-text("Create Application")');
    await page.fill('input[name="name"]', 'Edit Test App');
    await page.fill('textarea[name="comments"]', 'Original description');
    await page.click('button:has-text("Create Application")');
    
    // Wait for creation to complete
    await expect(page.locator('text=Edit Test App')).toBeVisible();
    
    // Click edit button for the application
    await page.click('button:has-text("Edit")');
    
    // Wait for edit form to appear
    await expect(page.locator('h3:has-text("Edit Application")')).toBeVisible();
    
    // Modify the form
    await page.fill('input[name="name"]', 'Updated Test App');
    await page.fill('textarea[name="comments"]', 'Updated description');
    
    // Submit the form
    await page.click('button:has-text("Update Application")');
    
    // Wait for the form to disappear and check for updates
    await expect(page.locator('h3:has-text("Edit Application")')).not.toBeVisible();
    
    // Check that the application was updated
    await expect(page.locator('text=Updated Test App')).toBeVisible();
    await expect(page.locator('text=Updated description')).toBeVisible();
    await expect(page.locator('text=Edit Test App')).not.toBeVisible();
  });

  test('should navigate to configurations view', async ({ page }) => {
    // First create an application
    await page.click('button:has-text("Create Application")');
    await page.fill('input[name="name"]', 'Config Test App');
    await page.click('button:has-text("Create Application")');
    
    // Wait for creation to complete
    await expect(page.locator('text=Config Test App')).toBeVisible();
    
    // Click "View Configs" button
    await page.click('button:has-text("View Configs")');
    
    // Check that we navigated to configurations view
    await expect(page.locator('h2:has-text("Configurations")')).toBeVisible();
    
    // Check breadcrumb navigation
    await expect(page.locator('text=Applications > Configurations')).toBeVisible();
    
    // Check that create configuration button is visible
    await expect(page.locator('button:has-text("Create Configuration")')).toBeVisible();
  });

  test('should handle form validation errors', async ({ page }) => {
    // Click create application button
    await page.click('button:has-text("Create Application")');
    
    // Try to submit empty form
    await page.click('button:has-text("Create Application")');
    
    // Check for validation error
    await expect(page.locator('text=Application name is required')).toBeVisible();
    
    // Fill in name that's too long
    const longName = 'a'.repeat(300);
    await page.fill('input[name="name"]', longName);
    await page.click('button:has-text("Create Application")');
    
    // Check for length validation error
    await expect(page.locator('text=Application name must be 256 characters or less')).toBeVisible();
  });

  test('should cancel form creation', async ({ page }) => {
    // Click create application button
    await page.click('button:has-text("Create Application")');
    
    // Wait for form to appear
    await expect(page.locator('h3:has-text("Create Application")')).toBeVisible();
    
    // Fill in some data
    await page.fill('input[name="name"]', 'Cancelled App');
    
    // Click cancel
    await page.click('button:has-text("Cancel")');
    
    // Check that form disappeared
    await expect(page.locator('h3:has-text("Create Application")')).not.toBeVisible();
    
    // Check that the data wasn't saved
    await expect(page.locator('text=Cancelled App')).not.toBeVisible();
  });

  test('should delete an application', async ({ page }) => {
    // First create an application to delete
    await page.click('button:has-text("Create Application")');
    await page.fill('input[name="name"]', 'Delete Test App');
    await page.click('button:has-text("Create Application")');
    
    // Wait for creation to complete
    await expect(page.locator('text=Delete Test App')).toBeVisible();
    
    // Set up dialog handler for confirmation
    page.on('dialog', dialog => dialog.accept());
    
    // Click delete button
    await page.click('button:has-text("Delete")');
    
    // Check that the application was removed
    await expect(page.locator('text=Delete Test App')).not.toBeVisible();
  });

  test('should handle empty state', async ({ page }) => {
    // If no applications exist, should show empty state
    const hasApplications = await page.locator('.list-item').count() > 0;
    
    if (!hasApplications) {
      await expect(page.locator('text=No applications found')).toBeVisible();
      await expect(page.locator('text=Create your first application to get started')).toBeVisible();
    }
  });
});
