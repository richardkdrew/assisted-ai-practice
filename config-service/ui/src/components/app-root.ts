export class AppRoot extends HTMLElement {
  private currentView: 'applications' | 'configurations' = 'applications';
  private selectedApplicationId: string | null = null;

  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  connectedCallback(): void {
    this.render();
    this.setupEventListeners();
  }

  private setupEventListeners(): void {
    // Listen for navigation events
    this.addEventListener('navigate', this.handleNavigation.bind(this) as EventListener);
    
    // Listen for application selection
    this.addEventListener('application-selected', this.handleApplicationSelected.bind(this) as EventListener);
  }

  private handleNavigation(event: Event): void {
    const customEvent = event as CustomEvent;
    const { view, applicationId } = customEvent.detail;
    this.currentView = view;
    if (applicationId) {
      this.selectedApplicationId = applicationId;
    }
    this.render();
  }

  private handleApplicationSelected(event: Event): void {
    const customEvent = event as CustomEvent;
    this.selectedApplicationId = customEvent.detail.applicationId;
    this.currentView = 'configurations';
    this.render();
  }

  private render(): void {
    if (!this.shadowRoot) return;

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          min-height: 100vh;
        }
        
        .header {
          background: #fff;
          border-bottom: 1px solid #e0e0e0;
          padding: 1rem 0;
          margin-bottom: 2rem;
        }
        
        .container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 20px;
        }
        
        .header h1 {
          color: #2c3e50;
          font-size: 2rem;
          font-weight: 600;
          margin: 0;
        }
        
        .nav {
          display: flex;
          gap: 1rem;
          margin-top: 1rem;
        }
        
        .nav-button {
          background: #3498db;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.9rem;
          transition: background-color 0.2s;
        }
        
        .nav-button:hover {
          background: #2980b9;
        }
        
        .nav-button.active {
          background: #2c3e50;
        }
        
        .breadcrumb {
          color: #7f8c8d;
          font-size: 0.9rem;
          margin-bottom: 1rem;
        }
        
        .breadcrumb a {
          color: #3498db;
          text-decoration: none;
        }
        
        .breadcrumb a:hover {
          text-decoration: underline;
        }
        
        .main-content {
          padding: 0 20px;
        }
      </style>
      
      <div class="header">
        <div class="container">
          <h1>Config Service Admin</h1>
          <nav class="nav">
            <button 
              class="nav-button ${this.currentView === 'applications' ? 'active' : ''}"
              data-view="applications"
            >
              Applications
            </button>
            <button 
              class="nav-button ${this.currentView === 'configurations' ? 'active' : ''}"
              data-view="configurations"
              ${!this.selectedApplicationId ? 'disabled' : ''}
            >
              Configurations
            </button>
          </nav>
        </div>
      </div>
      
      <main class="main-content">
        <div class="container">
          ${this.renderBreadcrumb()}
          ${this.renderCurrentView()}
        </div>
      </main>
    `;

    this.setupNavigation();
  }

  private renderBreadcrumb(): string {
    if (this.currentView === 'applications') {
      return '<div class="breadcrumb">Applications</div>';
    }
    
    if (this.currentView === 'configurations' && this.selectedApplicationId) {
      return `
        <div class="breadcrumb">
          <a href="#" data-navigate="applications">Applications</a> 
          &gt; Configurations
        </div>
      `;
    }
    
    return '';
  }

  private renderCurrentView(): string {
    switch (this.currentView) {
      case 'applications':
        return '<application-list></application-list>';
      case 'configurations':
        return this.selectedApplicationId 
          ? `<configuration-list application-id="${this.selectedApplicationId}"></configuration-list>`
          : '<div>Please select an application first.</div>';
      default:
        return '<div>Unknown view</div>';
    }
  }

  private setupNavigation(): void {
    const navButtons = this.shadowRoot?.querySelectorAll('.nav-button');
    navButtons?.forEach(button => {
      button.addEventListener('click', (e) => {
        const target = e.target as HTMLButtonElement;
        const view = target.dataset.view;
        if (view && !target.disabled) {
          this.currentView = view as 'applications' | 'configurations';
          if (view === 'applications') {
            this.selectedApplicationId = null;
          }
          this.render();
        }
      });
    });

    // Handle breadcrumb navigation
    const breadcrumbLinks = this.shadowRoot?.querySelectorAll('[data-navigate]');
    breadcrumbLinks?.forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const target = e.target as HTMLElement;
        const view = target.dataset.navigate;
        if (view) {
          this.currentView = view as 'applications' | 'configurations';
          if (view === 'applications') {
            this.selectedApplicationId = null;
          }
          this.render();
        }
      });
    });
  }
}

customElements.define('app-root', AppRoot);
