/**
 * Configuration list component for displaying and managing configurations
 */

import { BaseComponent } from '@/components/base/BaseComponent';
import { ComponentRegistry } from '@/components/base/ComponentRegistry';
import { configurationService } from '@/services/ConfigurationService';
import { applicationService } from '@/services/ApplicationService';
import type { Configuration, Application } from '@/types/domain';

export class ConfigurationList extends BaseComponent {
  private configurations: Configuration[] = [];
  private applications: Application[] = [];
  private loading: boolean = false;
  private error: string | null = null;
  private showCreateForm: boolean = false;
  private selectedApplicationId: string | null = null;

  protected createTemplate(): HTMLTemplateElement {
    return this.createTemplateFromHTML(`
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
          font-size: 2rem;
          font-weight: 700;
          color: var(--text-color, #1f2937);
          margin: 0;
        }

        .header-actions {
          display: flex;
          gap: 1rem;
          align-items: center;
        }

        .filter-select {
          padding: 0.5rem;
          border: 1px solid var(--border-color, #d1d5db);
          border-radius: 0.5rem;
          background: white;
          min-width: 200px;
        }

        .create-btn {
          background: var(--primary-color, #2563eb);
          color: white;
          border: none;
          padding: 0.75rem 1.5rem;
          border-radius: 0.5rem;
          cursor: pointer;
          font-weight: 500;
          transition: background-color 0.2s;
        }

        .create-btn:hover {
          background: var(--primary-hover, #1d4ed8);
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

        .configurations-table {
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

        .config-name {
          font-weight: 600;
          color: var(--text-color);
          font-size: var(--font-size-base);
        }

        .config-version {
          background: var(--primary-color);
          color: white;
          padding: 0.125rem 0.5rem;
          border-radius: var(--radius-sm);
          font-size: var(--font-size-xs);
          font-weight: 600;
          margin-left: 0.5rem;
        }

        .config-app {
          color: var(--text-muted);
          font-size: var(--font-size-sm);
        }

        .config-env {
          background: var(--bg-secondary);
          color: var(--text-color);
          padding: 0.25rem 0.5rem;
          border-radius: var(--radius-sm);
          font-size: var(--font-size-xs);
          font-weight: 500;
          text-transform: uppercase;
        }

        .config-env.production {
          background: var(--error-color);
          color: white;
        }

        .config-env.staging {
          background: var(--warning-color);
          color: white;
        }

        .config-env.development {
          background: var(--success-color);
          color: white;
        }

        .config-date {
          color: var(--text-muted);
          font-size: var(--font-size-sm);
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
          max-width: 600px;
          max-height: 90vh;
          overflow-y: auto;
          box-shadow: 0 20px 25px rgba(0,0,0,0.15);
        }

        .hidden {
          display: none;
        }
      </style>

      <div class="header">
        <h1 class="title">Configurations</h1>
        <div class="header-actions">
          <select class="filter-select" id="application-filter">
            <option value="">All Applications</option>
          </select>
          <button class="create-btn" id="create-btn">Create Configuration</button>
        </div>
      </div>

      <div id="error-container"></div>

      <div id="loading" class="loading hidden">
        Loading configurations...
      </div>

      <div id="configurations-container">
        <div class="configurations-table">
          <table class="table" id="configurations-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Application</th>
                <th>Config Size</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody id="configurations-tbody">
            </tbody>
          </table>
        </div>
      </div>

      <div id="form-overlay" class="form-overlay hidden">
        <div class="form-modal">
          <configuration-form id="create-form"></configuration-form>
        </div>
      </div>
    `);
  }

  connectedCallback(): void {
    super.connectedCallback();
    this.loadData();
  }

  protected attachEventListeners(): void {
    const createBtn = this.query('#create-btn');
    const applicationFilter = this.query('#application-filter');

    createBtn?.addEventListener('click', () => {
      this.showCreateForm = true;
      this.renderCreateForm();
    });

    applicationFilter?.addEventListener('change', (event) => {
      const target = event.target as HTMLSelectElement;
      this.selectedApplicationId = target.value || null;
      this.loadConfigurations();
    });

    // Listen for form events
    this.addEventListener('configuration-created', () => {
      this.showCreateForm = false;
      this.renderCreateForm();
      this.loadConfigurations();
    });

    this.addEventListener('configuration-updated', () => {
      this.showCreateForm = false;
      this.renderCreateForm();
      this.loadConfigurations();
    });

    this.addEventListener('form-cancelled', () => {
      this.showCreateForm = false;
      this.renderCreateForm();
    });

    // Listen for edit/delete events
    this.addEventListener('edit-configuration', (event: Event) => {
      this.editConfiguration((event as CustomEvent).detail.id);
    });

    this.addEventListener('delete-configuration', (event: Event) => {
      this.deleteConfiguration((event as CustomEvent).detail.id);
    });
  }

  private async loadData(): Promise<void> {
    this.loading = true;
    this.error = null;
    this.render();

    try {
      // Load applications for filter dropdown
      const applicationsResponse = await applicationService.getApplications({ limit: 100 });
      this.applications = applicationsResponse.items;
      this.renderApplicationFilter();

      // Load configurations
      await this.loadConfigurations();
    } catch (error) {
      this.error = error instanceof Error ? error.message : 'Failed to load data';
    } finally {
      this.loading = false;
      this.render();
    }
  }

  private async loadConfigurations(): Promise<void> {
    try {
      const params = this.selectedApplicationId
        ? { application_id: this.selectedApplicationId, limit: 100 }
        : { limit: 100 };

      const response = await configurationService.getConfigurations(params);
      this.configurations = response.items;
    } catch (error) {
      this.error = error instanceof Error ? error.message : 'Failed to load configurations';
    }

    if (!this.loading) {
      this.render();
    }
  }

  private renderApplicationFilter(): void {
    const filter = this.query('#application-filter') as HTMLSelectElement;
    if (!filter) return;

    // Clear existing options (except "All Applications")
    filter.innerHTML = '<option value="">All Applications</option>';

    // Add application options
    this.applications.forEach(app => {
      const option = document.createElement('option');
      option.value = app.id;
      option.textContent = app.name;
      if (app.id === this.selectedApplicationId) {
        option.selected = true;
      }
      filter.appendChild(option);
    });
  }

  private renderConfigurations(): void {
    const tbody = this.query('#configurations-tbody');
    const table = this.query('#configurations-table');

    if (!tbody || !table) return;

    if (this.configurations.length === 0) {
      const filterText = this.selectedApplicationId
        ? 'No configurations found for the selected application.'
        : 'No configurations yet';

      tbody.innerHTML = `
        <tr>
          <td colspan="5" class="empty-state">
            <h3>${filterText}</h3>
            <p>Create your first configuration to get started.</p>
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = this.configurations.map(config => this.renderConfigurationRow(config)).join('');

    // Attach event listeners to action buttons
    this.configurations.forEach(config => {
      const editBtn = this.query(`[data-edit="${config.id}"]`);
      const deleteBtn = this.query(`[data-delete="${config.id}"]`);

      editBtn?.addEventListener('click', () => {
        this.dispatchCustomEvent('edit-configuration', { id: config.id });
      });

      deleteBtn?.addEventListener('click', () => {
        this.dispatchCustomEvent('delete-configuration', { id: config.id });
      });
    });
  }

  private renderConfigurationRow(config: Configuration): string {
    const application = this.applications.find(app => app.id === config.application_id);
    const createdDate = new Date(config.created_at).toLocaleDateString();
    const configSize = Object.keys(config.config || {}).length;

    return `
      <tr>
        <td>
          <div class="config-name">${this.escapeHtml(config.name)}</div>
        </td>
        <td>
          <div class="config-app">${application ? this.escapeHtml(application.name) : 'Unknown'}</div>
        </td>
        <td>
          <div class="config-size">${configSize} keys</div>
        </td>
        <td>
          <div class="config-date">${createdDate}</div>
        </td>
        <td>
          <div class="actions">
            <button class="btn-sm btn-outline" data-edit="${config.id}" title="Edit">
              Edit
            </button>
            <button class="btn-sm btn-danger" data-delete="${config.id}" title="Delete">
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

      // Pass the selected application to the form if one is selected
      const form = this.query('#create-form') as any;
      if (form && this.selectedApplicationId) {
        form.setAttribute('default-application-id', this.selectedApplicationId);
      }
    } else {
      overlay.classList.add('hidden');
    }
  }

  protected render(): void {
    super.render();

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

    // Render configurations if not loading
    if (!this.loading) {
      this.renderConfigurations();
    }

    this.renderCreateForm();
  }

  private async editConfiguration(id: string): Promise<void> {
    this.showCreateForm = true;

    // Set the configuration ID on the form for editing
    const form = this.query('#create-form') as any;
    if (form) {
      form.setAttribute('configuration-id', id);
    }

    this.renderCreateForm();
  }

  private async deleteConfiguration(id: string): Promise<void> {
    if (!confirm('Are you sure you want to delete this configuration?')) {
      return;
    }

    try {
      await configurationService.deleteConfiguration(id);
      this.configurations = this.configurations.filter(config => config.id !== id);
      this.render();
    } catch (error) {
      this.error = error instanceof Error ? error.message : 'Failed to delete configuration';
      this.render();
    }
  }

  private escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

ComponentRegistry.register('configuration-list', ConfigurationList);