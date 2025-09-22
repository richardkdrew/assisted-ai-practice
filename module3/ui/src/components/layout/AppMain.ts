/**
 * Main application component that handles routing and layout
 */

import { BaseComponent } from '@/components/base/BaseComponent';
import { ComponentRegistry } from '@/components/base/ComponentRegistry';

export class AppMain extends BaseComponent {
  private currentRoute: string = '/';

  protected createTemplate(): HTMLTemplateElement {
    return this.createTemplateFromHTML(`
      <style>
        :host {
          display: block;
          min-height: 100vh;
          background: transparent;
          font-family: var(--font-family, system-ui, -apple-system, sans-serif);
        }

        .app-container {
          display: grid;
          grid-template-rows: auto auto 1fr;
          min-height: 100vh;
        }

        .header {
          background: linear-gradient(135deg, var(--primary-color, #2563eb) 0%, var(--primary-hover, #1d4ed8) 100%);
          color: white;
          padding: 1.5rem 2rem;
          box-shadow: var(--shadow-lg);
        }

        .header h1 {
          margin: 0;
          font-size: var(--font-size-3xl);
          font-weight: 700;
          text-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }

        .nav {
          background: white;
          border-bottom: 1px solid var(--border-color);
          padding: 0 2rem;
          box-shadow: var(--shadow-sm);
        }

        .nav-list {
          display: flex;
          gap: 0;
          list-style: none;
          margin: 0;
          padding: 0;
        }

        .nav-item {
          position: relative;
        }

        .nav-item.active::after {
          content: '';
          position: absolute;
          bottom: -1px;
          left: 0;
          right: 0;
          height: 3px;
          background: var(--primary-color);
          border-radius: 2px 2px 0 0;
        }

        .nav-link {
          display: block;
          padding: 1rem 2rem;
          text-decoration: none;
          color: var(--text-muted);
          font-weight: 500;
          font-size: var(--font-size-sm);
          text-transform: uppercase;
          letter-spacing: 0.025em;
          transition: all 0.2s ease;
          border-radius: var(--radius-sm) var(--radius-sm) 0 0;
        }

        .nav-link:hover,
        .nav-item.active .nav-link {
          color: var(--primary-color);
          background: var(--primary-light);
        }

        .main-content {
          padding: 2rem;
          overflow: auto;
          background: transparent;
        }

        .route-content {
          max-width: 1400px;
          margin: 0 auto;
          background: white;
          border-radius: var(--radius-lg);
          box-shadow: var(--shadow-md);
          min-height: calc(100vh - 200px);
        }
      </style>

      <div class="app-container">
        <header class="header">
          <h1>Configuration Service Admin</h1>
        </header>

        <nav class="nav">
          <ul class="nav-list nav-links">
            <li class="nav-item" data-route="/">
              <a href="#/" class="nav-link">Applications</a>
            </li>
            <li class="nav-item" data-route="/configurations">
              <a href="#/configurations" class="nav-link">Configurations</a>
            </li>
          </ul>
        </nav>

        <main class="main-content">
          <div class="route-content" id="route-content">
            <!-- Route content will be inserted here -->
          </div>
        </main>
      </div>
    `);
  }

  protected attachEventListeners(): void {
    // Handle navigation clicks
    this.shadow.addEventListener('click', (event) => {
      const target = event.target as HTMLElement;
      if (target.matches('.nav-link')) {
        event.preventDefault();
        const href = target.getAttribute('href');
        if (href) {
          this.navigateTo(href.slice(1)); // Remove the # prefix
        }
      }
    });

    // Handle browser back/forward
    window.addEventListener('hashchange', () => {
      this.handleRouteChange();
    });

    // Handle initial route
    this.handleRouteChange();
  }

  private navigateTo(route: string): void {
    window.location.hash = route;
  }

  private handleRouteChange(): void {
    const hash = window.location.hash;
    const route = hash.slice(1) || '/'; // Default to root

    this.currentRoute = route;
    this.updateActiveNavItem();
    this.renderRoute();
  }

  private updateActiveNavItem(): void {
    // Remove active class from all nav items and links
    const navItems = this.queryAll('.nav-item');
    const navLinks = this.queryAll('.nav-link');
    navItems.forEach(item => item.classList.remove('active'));
    navLinks.forEach(link => link.classList.remove('active'));

    // Add active class to current route item and link
    const activeItem = this.query(`[data-route="${this.currentRoute}"]`);
    if (activeItem) {
      activeItem.classList.add('active');
      const activeLink = activeItem.querySelector('.nav-link');
      if (activeLink) {
        activeLink.classList.add('active');
      }
    }
  }

  private renderRoute(): void {
    const routeContent = this.query('#route-content');
    if (!routeContent) return;

    // Clear current content
    routeContent.innerHTML = '';

    // Render appropriate component based on route
    switch (this.currentRoute) {
      case '/':
      case '/applications':
        routeContent.innerHTML = '<application-list></application-list>';
        break;
      case '/configurations':
        routeContent.innerHTML = '<configuration-list></configuration-list>';
        break;
      default:
        routeContent.innerHTML = '<application-list></application-list>'; // Default to applications for invalid routes
    }
  }
}

ComponentRegistry.register('app-main', AppMain);