import { test, expect } from '@playwright/test';

test.describe('Navigation and Integration', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load the application successfully', async ({ page }) => {
    // Verify main components load
    await expect(page.locator('app-router')).toBeVisible();
    await expect(page.locator('application-list')).toBeVisible();

    // Verify navigation elements
    await expect(page.locator('.nav-links')).toBeVisible();
    await expect(page.locator('a[href="#/"]')).toContainText('Applications');
    await expect(page.locator('a[href="#/configurations"]')).toContainText('Configurations');
  });

  test('should navigate between applications and configurations', async ({ page }) => {
    // Start on applications page
    await expect(page.locator('application-list')).toBeVisible();
    await expect(page.locator('configuration-list')).not.toBeVisible();

    // Navigate to configurations
    await page.click('a[href="#/configurations"]');
    await page.waitForSelector('configuration-list');

    await expect(page.locator('configuration-list')).toBeVisible();
    await expect(page.locator('application-list')).not.toBeVisible();

    // Navigate back to applications
    await page.click('a[href="#/"]');
    await page.waitForSelector('application-list');

    await expect(page.locator('application-list')).toBeVisible();
    await expect(page.locator('configuration-list')).not.toBeVisible();
  });

  test('should maintain active navigation state', async ({ page }) => {
    // Applications should be active by default
    await expect(page.locator('a[href="#/"]')).toHaveClass(/active/);
    await expect(page.locator('a[href="#/configurations"]')).not.toHaveClass(/active/);

    // Navigate to configurations
    await page.click('a[href="#/configurations"]');
    await page.waitForSelector('configuration-list');

    // Configurations should now be active
    await expect(page.locator('a[href="#/configurations"]')).toHaveClass(/active/);
    await expect(page.locator('a[href="#/"]')).not.toHaveClass(/active/);
  });

  test('should handle browser back/forward navigation', async ({ page }) => {
    // Start on applications
    await expect(page.locator('application-list')).toBeVisible();

    // Navigate to configurations
    await page.click('a[href="#/configurations"]');
    await page.waitForSelector('configuration-list');
    await expect(page.locator('configuration-list')).toBeVisible();

    // Use browser back
    await page.goBack();
    await page.waitForSelector('application-list');
    await expect(page.locator('application-list')).toBeVisible();

    // Use browser forward
    await page.goForward();
    await page.waitForSelector('configuration-list');
    await expect(page.locator('configuration-list')).toBeVisible();
  });

  test('should handle direct URL navigation', async ({ page }) => {
    // Navigate directly to configurations URL
    await page.goto('/#/configurations');
    await page.waitForSelector('configuration-list');

    await expect(page.locator('configuration-list')).toBeVisible();
    await expect(page.locator('a[href="#/configurations"]')).toHaveClass(/active/);

    // Navigate directly to applications URL
    await page.goto('/#/');
    await page.waitForSelector('application-list');

    await expect(page.locator('application-list')).toBeVisible();
    await expect(page.locator('a[href="#/"]')).toHaveClass(/active/);
  });

  test('should show error state for invalid routes', async ({ page }) => {
    // Navigate to invalid route
    await page.goto('/#/invalid-route');

    // Should default to applications or show error
    await expect(page.locator('application-list')).toBeVisible();
  });

  test('should maintain page title and meta information', async ({ page }) => {
    // Check initial title
    await expect(page).toHaveTitle(/Configuration Service/);

    // Navigate to configurations
    await page.click('a[href="#/configurations"]');
    await page.waitForSelector('configuration-list');

    // Title should still be appropriate
    await expect(page).toHaveTitle(/Configuration Service/);
  });

  test('should handle responsive design elements', async ({ page }) => {
    // Test on different viewport sizes
    await page.setViewportSize({ width: 1200, height: 800 });
    await expect(page.locator('.nav-links')).toBeVisible();

    // Test mobile size
    await page.setViewportSize({ width: 375, height: 667 });
    // Navigation should still be accessible (might be collapsed)
    await expect(page.locator('a[href="#/"]')).toBeVisible();
    await expect(page.locator('a[href="#/configurations"]')).toBeVisible();

    // Test tablet size
    await page.setViewportSize({ width: 768, height: 1024 });
    await expect(page.locator('.nav-links')).toBeVisible();
  });
});