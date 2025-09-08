// Test setup file for Vitest
import { vi } from 'vitest';

// Mock fetch globally for tests
global.fetch = vi.fn();

// Mock window.confirm for delete operations
global.confirm = vi.fn(() => true);

// Mock console methods to reduce noise in tests
global.console = {
  ...console,
  log: vi.fn(),
  warn: vi.fn(),
  error: vi.fn(),
};

// Setup custom elements registry mock
global.customElements = {
  define: vi.fn(),
  get: vi.fn(),
  upgrade: vi.fn(),
  whenDefined: vi.fn(() => Promise.resolve()),
};

// Mock HTMLElement for Web Components
global.HTMLElement = class MockHTMLElement {
  attachShadow = vi.fn(() => ({
    innerHTML: '',
    querySelector: vi.fn(),
    querySelectorAll: vi.fn(() => []),
    appendChild: vi.fn(),
  }));
  
  addEventListener = vi.fn();
  removeEventListener = vi.fn();
  dispatchEvent = vi.fn();
  
  setAttribute = vi.fn();
  getAttribute = vi.fn();
  removeAttribute = vi.fn();
  
  appendChild = vi.fn();
  removeChild = vi.fn();
  
  querySelector = vi.fn();
  querySelectorAll = vi.fn(() => []);
  
  innerHTML = '';
  textContent = '';
  
  style = {};
  classList = {
    add: vi.fn(),
    remove: vi.fn(),
    contains: vi.fn(),
    toggle: vi.fn(),
  };
};

// Reset all mocks before each test
beforeEach(() => {
  vi.clearAllMocks();
});
