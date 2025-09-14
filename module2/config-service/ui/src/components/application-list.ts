import { applicationService } from '../services/application-service';
import { ApplicationListItem } from '../models/application';

export class ApplicationList extends HTMLElement {
  private applications: ApplicationListItem[] = [];
  private loading = false;
  private error: string | null = null;
  private currentPage = 1;
  private pageSize = 10;
  private showForm = false;
  private editingApplication: ApplicationListItem | null = null;
  private submitting = false;

  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  connectedCallback(): void {
    this.loadApplications();
    this.render();
  }

  private async loadApplications(): Promise<void> {
    this.loading = true;
    this.error = null;
    this.render();

    try {
      const offset = (this.currentPage - 1) * this.pageSize;
      const response = await applicationService.getAllWithCounts(this.pageSize, offset);
      
      if (response.error) {
        this.error = response.error;
      } else if (response.data) {
        this.applications = response.data;
      }
    } catch (err) {
      this.error = err instanceof Error ? err.message : 'Failed to load applications';
    } finally {
      this.loading = false;
      this.render();
    }
  }

  private async deleteApplication(id: string): Promise<void> {
    if (!confirm('Are you sure you want to delete this application? This will also delete all related configurations.')) {
      return;
    }

    try {
      const response = await applicationService.delete(id);
      if (response.error) {
        this.error = response.error;
        this.render();
      } else {
        await this.loadApplications();
      }
    } catch (err) {
      this.error = err instanceof Error ? err.message : 'Failed to delete application';
      this.render();
    }
  }

  private viewConfigurations(applicationId: string): void {
    const event = new CustomEvent('application-selected', {
      detail: { applicationId },
      bubbles: true,
      composed: true
    });
    this.dispatchEvent(event);
  }

  private showCreateForm(): void {
    this.showForm = true;
    this.editingApplication = null;
    this.render();
  }

  private showEditForm(application: ApplicationListItem): void {
    this.showForm = true;
    this.editingApplication = application;
    this.render();
  }

  private hideForm(): void {
    this.showForm = false;
    this.editingApplication = null;
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
    this.render();
    
    try {
      let response;
      if (this.editingApplication) {
        response = await applicationService.update(this.editingApplication.id, formData);
      } else {
        response = await applicationService.create(formData);
      }

      if (response.error) {
        this.error = response.error;
        this.render();
      } else {
        this.hideForm();
        await this.loadApplications();
      }
    } catch (err) {
      this.error = err instanceof Error ? err.message : 'Failed to save application';
      this.render();
    } finally {
      this.submitting = false;
      this.render();
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
        
        .btn-success {
          background: #27ae60;
          color: white;
        }
        
        .btn-success:hover {
          background: #229954;
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
          align-items: center;
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
        }
        
        .list-item-actions {
          display: flex;
          gap: 0.5rem;
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
        <h2 class="title">Applications</h2>
        <button class="btn btn-primary" id="create-btn">
          Create Application
        </button>
      </div>
      
      ${this.error ? `<div class="error">${this.error}</div>` : ''}
      
      ${this.showForm ? this.renderForm() : ''}
      
      ${this.loading ? '<div class="loading">Loading applications...</div>' : this.renderApplications()}
    `;

    this.setupEventListeners();
  }

  private renderForm(): string {
    return `
      <application-form 
        ${this.editingApplication ? `application='${JSON.stringify(this.editingApplication)}'` : ''}
      ></application-form>
    `;
  }

  private renderApplications(): string {
    if (this.applications.length === 0) {
      return `
        <div class="empty-state">
          <p>No applications found.</p>
          <p>Create your first application to get started.</p>
        </div>
      `;
    }

    const applicationItems = this.applications.map(app => `
      <li class="list-item">
        <div class="list-item-content">
          <div class="list-item-title">${app.name}</div>
          <div class="list-item-meta">
            ${app.comments || 'No description'} • 
            ${app.configurationCount} configuration${app.configurationCount !== 1 ? 's' : ''} • 
            Created ${new Date(app.created_at).toLocaleDateString()}
          </div>
        </div>
        <div class="list-item-actions">
          <button class="btn btn-success btn-small" data-action="view-configs" data-id="${app.id}">
            View Configs
          </button>
          <button class="btn btn-primary btn-small" data-action="edit" data-id="${app.id}">
            Edit
          </button>
          <button class="btn btn-danger btn-small" data-action="delete" data-id="${app.id}">
            Delete
          </button>
        </div>
      </li>
    `).join('');

    return `
      <ul class="list">
        ${applicationItems}
      </ul>
      ${this.renderPagination()}
    `;
  }

  private renderPagination(): string {
    const hasMore = this.applications.length === this.pageSize;
    
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
          case 'view-configs':
            if (id) this.viewConfigurations(id);
            break;
          case 'edit':
            if (id) {
              const app = this.applications.find(a => a.id === id);
              if (app) this.showEditForm(app);
            }
            break;
          case 'delete':
            if (id) this.deleteApplication(id);
            break;
          case 'prev-page':
            if (this.currentPage > 1) {
              this.currentPage--;
              this.loadApplications();
            }
            break;
          case 'next-page':
            this.currentPage++;
            this.loadApplications();
            break;
        }
      });
    });

    // Form events
    this.addEventListener('form-submit', this.handleFormSubmit.bind(this) as EventListener);
    this.addEventListener('form-cancel', this.hideForm.bind(this));
  }
}

customElements.define('application-list', ApplicationList);
