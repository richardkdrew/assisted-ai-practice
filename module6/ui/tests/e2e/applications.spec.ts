import { test, expect } from '@playwright/test';

test.describe('Applications CRUD', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to applications page
    await page.goto('/');
    await page.waitForSelector('application-list');
  });

  test.afterEach(async ({ page }) => {
    // Clean up any created applications by deleting them
    try {
      await page.goto('/');
      await page.waitForSelector('application-list');

      // Delete all applications (to clean up test data)
      const deleteButtons = await page.locator('[data-delete]').all();
      for (const button of deleteButtons) {
        page.on('dialog', dialog => dialog.accept());
        await button.click();
        await page.waitForTimeout(500); // Wait for deletion
      }
    } catch (error) {
      // Ignore cleanup errors
    }
  });

  test('should display empty state when no applications exist', async ({ page }) => {
    // First clean up any existing data
    try {
      const deleteButtons = await page.locator('[data-delete]').all();
      for (const button of deleteButtons) {
        page.on('dialog', dialog => dialog.accept());
        await button.click();
        await page.waitForTimeout(500);
      }
    } catch (error) {
      // No applications to delete
    }

    await expect(page.locator('.empty-state')).toBeVisible();
    await expect(page.locator('.empty-state h3')).toContainText('No applications yet');
  });

  test('should create a new application', async ({ page }) => {
    // Click create button
    await page.click('#create-btn');

    // Wait for form modal
    await expect(page.locator('#form-overlay')).toBeVisible();

    // Fill out application form
    await page.fill('[name="name"]', 'Test Application');
    await page.fill('[name="comments"]', 'This is a test application');

    // Submit form
    await page.click('button[type="submit"]');

    // Wait for success and form to close
    await expect(page.locator('#form-overlay')).toBeHidden();

    // Verify application appears in list
    await expect(page.locator('.app-name')).toContainText('Test Application');
    await expect(page.locator('.app-comments')).toContainText('This is a test application');
  });

  test('should edit an existing application', async ({ page }) => {
    // First create an application
    await page.click('#create-btn');
    await page.fill('[name="name"]', 'Original Name');
    await page.fill('[name="comments"]', 'Original comments');
    await page.click('button[type="submit"]');
    await expect(page.locator('#form-overlay')).toBeHidden();

    // Click edit button
    await page.click('[data-edit]');

    // Wait for form with existing data
    await expect(page.locator('#form-overlay')).toBeVisible();
    await expect(page.locator('[name="name"]')).toHaveValue('Original Name');

    // Update the application
    await page.fill('[name="name"]', 'Updated Name');
    await page.fill('[name="comments"]', 'Updated comments');
    await page.click('button[type="submit"]');

    // Verify changes
    await expect(page.locator('#form-overlay')).toBeHidden();
    await expect(page.locator('.app-name')).toContainText('Updated Name');
    await expect(page.locator('.app-comments')).toContainText('Updated comments');
  });

  test('should delete an application', async ({ page }) => {
    // First create an application
    await page.click('#create-btn');
    await page.fill('[name="name"]', 'To Be Deleted');
    await page.click('button[type="submit"]');
    await expect(page.locator('#form-overlay')).toBeHidden();

    // Handle confirmation dialog and delete
    page.on('dialog', dialog => dialog.accept());
    await page.click('[data-delete]');

    // Verify application is removed
    await expect(page.locator('.empty-state')).toBeVisible();
    await expect(page.locator('.app-name')).not.toBeVisible();
  });

  test('should cancel form creation', async ({ page }) => {
    // Open create form
    await page.click('#create-btn');
    await expect(page.locator('#form-overlay')).toBeVisible();

    // Fill partial data
    await page.fill('[name="name"]', 'Cancelled App');

    // Cancel
    await page.click('button[type="button"]'); // Cancel button

    // Verify form closed and no application created
    await expect(page.locator('#form-overlay')).toBeHidden();
  });
});