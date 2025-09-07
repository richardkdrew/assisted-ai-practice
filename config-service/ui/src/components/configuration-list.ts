import { configurationService } from '../services/configuration-service';
import { ConfigurationListItem } from '../models/configuration';

export class ConfigurationList extends HTMLElement {
  private configurations: ConfigurationListItem[] = [];
  private loading = false;
  private error: string | null = null;
  private currentPage = 1;
  private pageSize = 10;
  private showForm = false;
  private editingConfiguration: ConfigurationListItem | null = null;
  private applicationId: string | null = null;
  private submitting = false;

  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes(): string[] {
    return ['application-id'];
  }

  attributeChangedCallback(name: string, oldValue: string, newValue: string): void {
    if (name === 'application-id' && newValue !== oldValue) {
      this.applicationId = newValue;
      if (this.isConnected) {
        this.loadConfigurations();
      }
    }
  }

  connectedCallback(): void {
    if (this.applicationId) {
      this.loadConfigurations();
    }
    this.render();
  }

  private async loadConfigurations(): Promise<void> {
    if (!this.applicationId) return;

    this.loading = true;
    this.error = null;
    this.render();

    try {
      const offset = (this.currentPage - 1) * this.pageSize;
      const response = await configurationService.getByApplicationId(
        this.applicationId,
        this.pageSize,
        offset
      );
      
      if (response.error) {
        this.error = response.error;
      } else if (response.data) {
        this.configurations = configurationService.transformToListItems(response.data);
      }
    } catch (err) {
      this.error = err instanceof Error ? err.message : 'Failed to load configurations';
    } finally {
      this.loading = false;
      this.render();
    }
  }

  private async deleteConfiguration(id: string): Promise<void> {
    if (!confirm('Are you sure you want to delete this configuration?')) {
      return;
    }

    try {
      const response = await configurationService.delete(id);
      if (response.error) {
        this.error = response.error;
        this.render();
      } else {
        await this.loadConfigurations();
      }
    } catch (err) {
      this.error = err instanceof Error ? err.message : 'Failed to delete configuration';
      this.render();
    }
  }

  private showCreateForm(): void {
    this.showForm = true;
    this.editingConfiguration = null;
    this.render();
  }

  private showEditForm(configuration: ConfigurationListItem): void {
    this.showForm = true;
    this.editingConfiguration = configuration;
    this.render();
  }

  private hideForm(): void {
    this.showForm = false;
    this.editingConfiguration = null;
    this.render();
  }

  private async handleFormSubmit(event: Event): Promise<void> {
    // Prevent multiple simultaneous submissions
    if (this.submitting) {
      return;
    }

    const customEvent = event as CustomEvent;
    const formData = customEvent.detail;
    
    this.submitting = true;
    this.error = null;
    
    try {
      let response;
      if (this.editingConfiguration) {
        response = await configurationService.update(this.editingConfiguration.id, formData);
      } else {
        // Add application_id to form data for creation
        const createData = {
          ...formData,
          application_id: this.applicationId
        };
        response = await configurationService.create(createData);
      }

      if (response.error) {
        this.error = response.error;
        this.render();
      } else {
        this.hideForm();
        await this.loadConfigurations();
      }
    } catch (err) {
      this.error = err instanceof Error ? err.message : 'Failed to save configuration';
      this.render();
    } finally {
      this.submitting = false;
    }
  }

  private render(): void {
    if (!this.shadowRoot) return;

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
        }
        
        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
        }
        
        .title {
          font-size: 1.5rem;
          font-weight: 600;
          color: #2c3e50;
          margin: 0;
        }
        
        .btn {
          display: inline-block;
          padding: 0.5rem 1rem;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.9rem;
          text-decoration: none;
          transition: all 0.2s;
          font-family: inherit;
        }
        
        .btn-primary {
          background: #3498db;
          color: white;
        }
        
        .btn-primary:hover {
          background: #2980b9;
        }
        
        .btn-danger {
          background: #e74c3c;
          color: white;
        }
        
        .btn-danger:hover {
          background: #c0392b;
        }
        
        .btn-small {
          padding: 0.25rem 0.5rem;
          font-size: 0.8rem;
        }
        
        .loading {
          display: flex;
          justify-content: center;
          align-items: center;
          padding: 2rem;
          color: #7f8c8d;
        }
        
        .error {
          background: #fdf2f2;
          border: 1px solid #f5c6cb;
          color: #721c24;
          padding: 1rem;
          border-radius: 4px;
          margin-bottom: 1rem;
        }
        
        .list {
          list-style: none;
          margin: 0;
          padding: 0;
        }
        
        .list-item {
          background: white;
          border: 1px solid #e0e0e0;
          border-radius: 4px;
          padding: 1rem;
          margin-bottom: 0.5rem;
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
        }
        
        .list-item:hover {
          background: #f8f9fa;
        }
        
        .list-item-content {
          flex: 1;
        }
        
        .list-item-title {
          font-weight: 600;
          color: #2c3e50;
          margin-bottom: 0.25rem;
        }
        
        .list-item-meta {
          font-size: 0.8rem;
          color: #7f8c8d;
          margin-bottom: 0.5rem;
        }
        
        .list-item-preview {
          font-size: 0.8rem;
          color: #555;
          background: #f8f9fa;
          padding: 0.5rem;
          border-radius: 4px;
          border-left: 3px solid #3498db;
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        }
        
        .list-item-actions {
          display: flex;
          gap: 0.5rem;
          margin-left: 1rem;
        }
        
        .empty-state {
          text-align: center;
          padding: 3rem;
          color: #7f8c8d;
        }
        
        .pagination {
          display: flex;
          justify-content: center;
          gap: 0.5rem;
          margin-top: 2rem;
        }
        
        .pagination button {
          padding: 0.5rem 0.75rem;
          border: 1px solid #ddd;
          background: white;
          cursor: pointer;
          border-radius: 4px;
        }
        
        .pagination button:hover {
          background: #f8f9fa;
        }
        
        .pagination button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      </style>
      
      <div class="header">
        <h2 class="title">Configurations</h2>
        <button class="btn btn-primary" id="create-btn" ${!this.applicationId ? 'disabled' : ''}>
          Create Configuration
        </button>
      </div>
      
      ${this.error ? `<div class="error">${this.error}</div>` : ''}
      
      ${this.showForm ? this.renderForm() : ''}
      
      ${this.loading ? '<div class="loading">Loading configurations...</div>' : this.renderConfigurations()}
    `;

    this.setupEventListeners();
  }

  private renderForm(): string {
    return `
      <configuration-form 
        application-id="${this.applicationId}"
        ${this.editingConfiguration ? `configuration='${JSON.stringify(this.editingConfiguration)}'` : ''}
      ></configuration-form>
    `;
  }

  private renderConfigurations(): string {
    if (!this.applicationId) {
      return `
        <div class="empty-state">
          <p>No application selected.</p>
          <p>Please select an application to view its configurations.</p>
        </div>
      `;
    }

    if (this.configurations.length === 0) {
      return `
        <div class="empty-state">
          <p>No configurations found for this application.</p>
          <p>Create your first configuration to get started.</p>
        </div>
      `;
    }

    const configurationItems = this.configurations.map(config => `
      <li class="list-item">
        <div class="list-item-content">
          <div class="list-item-title">${config.name}</div>
          <div class="list-item-meta">
            ${config.comments || 'No description'} • 
            ${config.configKeyCount} key${config.configKeyCount !== 1 ? 's' : ''} • 
            Created ${new Date(config.created_at).toLocaleDateString()}
          </div>
          <div class="list-item-preview">
            ${config.configKeyCount} configuration key${config.configKeyCount !== 1 ? 's' : ''} defined
          </div>
        </div>
        <div class="list-item-actions">
          <button class="btn btn-primary btn-small" data-action="edit" data-id="${config.id}">
            Edit
          </button>
          <button class="btn btn-danger btn-small" data-action="delete" data-id="${config.id}">
            Delete
          </button>
        </div>
      </li>
    `).join('');

    return `
      <ul class="list">
        ${configurationItems}
      </ul>
      ${this.renderPagination()}
    `;
  }

  private renderPagination(): string {
    const hasMore = this.configurations.length === this.pageSize;
    
    return `
      <div class="pagination">
        <button ${this.currentPage === 1 ? 'disabled' : ''} data-action="prev-page">
          Previous
        </button>
        <span>Page ${this.currentPage}</span>
        <button ${!hasMore ? 'disabled' : ''} data-action="next-page">
          Next
        </button>
      </div>
    `;
  }

  private setupEventListeners(): void {
    // Create button
    const createBtn = this.shadowRoot?.getElementById('create-btn');
    createBtn?.addEventListener('click', () => this.showCreateForm());

    // Action buttons
    const actionButtons = this.shadowRoot?.querySelectorAll('[data-action]');
    actionButtons?.forEach(button => {
      button.addEventListener('click', (e) => {
        const target = e.target as HTMLButtonElement;
        const action = target.dataset.action;
        const id = target.dataset.id;

        switch (action) {
          case 'edit':
            if (id) {
              const config = this.configurations.find(c => c.id === id);
              if (config) this.showEditForm(config);
            }
            break;
          case 'delete':
            if (id) this.deleteConfiguration(id);
            break;
          case 'prev-page':
            if (this.currentPage > 1) {
              this.currentPage--;
              this.loadConfigurations();
            }
            break;
          case 'next-page':
            this.currentPage++;
            this.loadConfigurations();
            break;
        }
      });
    });

    // Form events
    this.addEventListener('form-submit', this.handleFormSubmit.bind(this) as EventListener);
    this.addEventListener('form-cancel', this.hideForm.bind(this));
  }
}

customElements.define('configuration-list', ConfigurationList);
