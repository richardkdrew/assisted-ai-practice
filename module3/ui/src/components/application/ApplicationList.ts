/**
 * Application list component for displaying and managing applications
 */

import { BaseComponent } from '@/components/base/BaseComponent';
import { ComponentRegistry } from '@/components/base/ComponentRegistry';
import { applicationService } from '@/services/ApplicationService';
import type { Application } from '@/types/domain';

export class ApplicationList extends BaseComponent {
  private applications: Application[] = [];
  private loading: boolean = false;
  private error: string | null = null;
  private showCreateForm: boolean = false;

  protected createTemplate(): HTMLTemplateElement {
    return this.createTemplateFromHTML(`
      <style>
        :host {
          display: block;
          padding: 2rem;
        }

        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid var(--border-light);
        }

        .title {
          font-size: var(--font-size-3xl);
          font-weight: 700;
          color: var(--text-color);
          margin: 0;
        }

        .create-btn {
          background: var(--primary-color);
          color: white;
          border: none;
          padding: 0.75rem 1.5rem;
          border-radius: var(--radius-md);
          cursor: pointer;
          font-weight: 600;
          font-size: var(--font-size-sm);
          transition: all 0.2s ease;
          box-shadow: var(--shadow-sm);
        }

        .create-btn:hover {
          background: var(--primary-hover);
          box-shadow: var(--shadow-md);
          transform: translateY(-1px);
        }

        .loading {
          text-align: center;
          padding: 2rem;
          color: var(--text-muted, #6b7280);
        }

        .error {
          background: #fef2f2;
          border: 1px solid #fecaca;
          color: #dc2626;
          padding: 1rem;
          border-radius: 0.5rem;
          margin-bottom: 1rem;
        }

        .applications-table {
          width: 100%;
          background: white;
          border-radius: var(--radius-md);
          box-shadow: var(--shadow-sm);
          overflow: hidden;
          border: 1px solid var(--border-color);
        }

        .table {
          width: 100%;
          border-collapse: collapse;
        }

        .table th {
          background: var(--bg-secondary);
          padding: 1rem;
          text-align: left;
          font-weight: 600;
          font-size: var(--font-size-sm);
          color: var(--text-color);
          border-bottom: 2px solid var(--border-color);
          text-transform: uppercase;
          letter-spacing: 0.025em;
        }

        .table td {
          padding: 1rem;
          border-bottom: 1px solid var(--border-light);
          vertical-align: middle;
        }

        .table tbody tr:hover {
          background: var(--bg-hover);
        }

        .table tbody tr:last-child td {
          border-bottom: none;
        }

        .app-name {
          font-weight: 600;
          color: var(--text-color);
          font-size: var(--font-size-base);
        }

        .app-comments {
          color: var(--text-muted);
          font-style: italic;
          max-width: 300px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .app-date {
          color: var(--text-muted);
          font-size: var(--font-size-sm);
        }

        .config-count {
          background: var(--primary-light);
          color: var(--primary-color);
          padding: 0.25rem 0.75rem;
          border-radius: var(--radius-sm);
          font-size: var(--font-size-xs);
          font-weight: 600;
          text-align: center;
          min-width: 60px;
          display: inline-block;
        }

        .actions {
          display: flex;
          gap: 0.5rem;
          justify-content: flex-end;
        }

        .btn-sm {
          padding: 0.5rem 0.75rem;
          font-size: var(--font-size-xs);
          border-radius: var(--radius-sm);
          border: none;
          cursor: pointer;
          font-weight: 500;
          transition: all 0.2s ease;
        }

        .btn-outline {
          background: transparent;
          border: 1px solid var(--border-color);
          color: var(--text-muted);
        }

        .btn-outline:hover {
          background: var(--bg-secondary);
          border-color: var(--text-muted);
          color: var(--text-color);
        }

        .btn-danger {
          background: var(--error-color);
          color: white;
        }

        .btn-danger:hover {
          background: #b91c1c;
        }

        .empty-state {
          text-align: center;
          padding: 4rem 2rem;
          color: var(--text-muted, #6b7280);
        }

        .empty-state h3 {
          margin: 0 0 0.5rem 0;
          font-size: 1.25rem;
        }

        .form-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0,0,0,0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }

        .form-modal {
          background: white;
          border-radius: 0.75rem;
          padding: 2rem;
          width: 90%;
          max-width: 500px;
          box-shadow: 0 20px 25px rgba(0,0,0,0.15);
        }

        .hidden {
          display: none;
        }
      </style>

      <div class="header">
        <h1 class="title">Applications</h1>
        <button class="create-btn" id="create-btn">Create Application</button>
      </div>

      <div id="error-container"></div>

      <div id="loading" class="loading hidden">
        Loading applications...
      </div>

      <div id="applications-container">
        <div class="applications-table">
          <table class="table" id="applications-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Comments</th>
                <th>Configurations</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="applications-tbody">
            </tbody>
          </table>
        </div>
      </div>

      <div id="form-overlay" class="form-overlay hidden">
        <div class="form-modal">
          <application-form id="create-form"></application-form>
        </div>
      </div>
    `);
  }

  connectedCallback(): void {
    super.connectedCallback();
    this.loadApplications();
  }

  protected attachEventListeners(): void {
    this.attachButtonListeners();

    // Listen for form events (these are on the component itself, not DOM elements)
    this.addEventListener('application-created', () => {
      this.showCreateForm = false;
      this.renderCreateForm();
      this.loadApplications();
    });

    this.addEventListener('application-updated', () => {
      this.showCreateForm = false;
      this.renderCreateForm();
      this.loadApplications();
    });

    this.addEventListener('form-cancelled', () => {
      this.showCreateForm = false;
      this.renderCreateForm();
    });

    // Listen for edit/delete events
    this.addEventListener('edit-application', (event: Event) => {
      this.editApplication((event as CustomEvent).detail.id);
    });

    this.addEventListener('delete-application', (event: Event) => {
      this.deleteApplication((event as CustomEvent).detail.id);
    });
  }

  private attachButtonListeners(): void {
    const createBtn = this.query('#create-btn');
    createBtn?.addEventListener('click', () => {
      this.showCreateForm = true;

      // Clear any existing application-id for create mode
      const form = this.query('#create-form') as any;
      if (form) {
        form.removeAttribute('application-id');
      }

      this.renderCreateForm();
    });
  }

  private async loadApplications(): Promise<void> {
    this.loading = true;
    this.error = null;
    this.render();

    try {
      const response = await applicationService.getApplications({ limit: 100 });
      this.applications = response.items;
    } catch (error) {
      this.error = error instanceof Error ? error.message : 'Failed to load applications';
    } finally {
      this.loading = false;
      this.render();
    }
  }

  private renderApplications(): void {
    const tbody = this.query('#applications-tbody');
    const table = this.query('#applications-table');

    if (!tbody || !table) return;

    if (this.applications.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" class="empty-state">
            <h3>No applications yet</h3>
            <p>Create your first application to get started.</p>
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = this.applications.map(app => this.renderApplicationRow(app)).join('');

    // Attach event listeners to action buttons
    this.applications.forEach(app => {
      const editBtn = this.query(`[data-edit="${app.id}"]`);
      const deleteBtn = this.query(`[data-delete="${app.id}"]`);

      editBtn?.addEventListener('click', () => {
        this.dispatchCustomEvent('edit-application', { id: app.id });
      });

      deleteBtn?.addEventListener('click', () => {
        this.dispatchCustomEvent('delete-application', { id: app.id });
      });
    });
  }

  private renderApplicationRow(app: Application): string {
    const configCount = app.configuration_ids.length;
    const createdDate = new Date(app.created_at).toLocaleDateString();

    return `
      <tr>
        <td>
          <div class="app-name">${this.escapeHtml(app.name)}</div>
        </td>
        <td>
          <div class="app-comments">${app.comments ? this.escapeHtml(app.comments) : '-'}</div>
        </td>
        <td>
          <span class="config-count">${configCount}</span>
        </td>
        <td>
          <div class="app-date">${createdDate}</div>
        </td>
        <td>
          <div class="actions">
            <button class="btn-sm btn-outline" data-edit="${app.id}" title="Edit">
              Edit
            </button>
            <button class="btn-sm btn-danger" data-delete="${app.id}" title="Delete">
              Delete
            </button>
          </div>
        </td>
      </tr>
    `;
  }

  private renderCreateForm(): void {
    const overlay = this.query('#form-overlay');
    if (!overlay) return;

    if (this.showCreateForm) {
      overlay.classList.remove('hidden');
    } else {
      overlay.classList.add('hidden');
    }
  }

  protected render(): void {
    super.render();

    // Re-attach event listeners after DOM is rebuilt
    this.attachButtonListeners();

    // Update loading state
    const loading = this.query('#loading');
    if (loading) {
      if (this.loading) {
        loading.classList.remove('hidden');
      } else {
        loading.classList.add('hidden');
      }
    }

    // Update error state
    const errorContainer = this.query('#error-container');
    if (errorContainer) {
      if (this.error) {
        errorContainer.innerHTML = `<div class="error">${this.escapeHtml(this.error)}</div>`;
      } else {
        errorContainer.innerHTML = '';
      }
    }

    // Render applications if not loading
    if (!this.loading) {
      this.renderApplications();
    }

    // Always render create form to maintain state
    this.renderCreateForm();
  }

  private async editApplication(id: string): Promise<void> {
    this.showCreateForm = true;

    // Set the application ID on the form for editing
    const form = this.query('#create-form') as any;
    if (form) {
      // Clear any existing application-id first
      form.removeAttribute('application-id');
      // Add small delay to ensure attribute change is processed
      setTimeout(() => {
        form.setAttribute('application-id', id);
      }, 10);
    }

    this.renderCreateForm();
  }

  private async deleteApplication(id: string): Promise<void> {
    if (!confirm('Are you sure you want to delete this application? This will also delete all its configurations.')) {
      return;
    }

    try {
      await applicationService.deleteApplication(id);
      // Remove from local array
      this.applications = this.applications.filter(app => app.id !== id);

      // Force a complete re-render of the applications table
      this.renderApplications();

      // Also clear any error state
      this.error = null;
      this.render();
    } catch (error) {
      this.error = error instanceof Error ? error.message : 'Failed to delete application';
      this.render();
    }
  }

  private escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

ComponentRegistry.register('application-list', ApplicationList);