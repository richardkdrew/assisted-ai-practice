/**
 * Configuration form component for creating and editing configurations
 */

import { BaseComponent } from '@/components/base/BaseComponent';
import { ComponentRegistry } from '@/components/base/ComponentRegistry';
import { configurationService } from '@/services/ConfigurationService';
import { applicationService } from '@/services/ApplicationService';
import type { Configuration, ConfigurationCreate, ConfigurationUpdate, Application } from '@/types/domain';

export class ConfigurationForm extends BaseComponent {
  private configuration: Configuration | null = null;
  private applications: Application[] = [];
  private loading: boolean = false;
  private applicationsLoading: boolean = false;
  private error: string | null = null;

  static get observedAttributes(): string[] {
    return ['configuration-id', 'default-application-id'];
  }

  protected createTemplate(): HTMLTemplateElement {
    return this.createTemplateFromHTML(`
      <style>
        :host {
          display: block;
        }

        .form-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
        }

        .form-title {
          font-size: 1.5rem;
          font-weight: 600;
          color: var(--text-color, #1f2937);
          margin: 0;
        }

        .close-btn {
          background: none;
          border: none;
          font-size: 1.5rem;
          cursor: pointer;
          color: var(--text-muted, #6b7280);
          padding: 0.25rem;
          border-radius: 0.25rem;
          transition: background-color 0.2s;
        }

        .close-btn:hover {
          background: var(--bg-hover, #f3f4f6);
        }

        .form {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .field {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .field-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
        }

        .label {
          font-weight: 500;
          color: var(--text-color, #374151);
        }

        .required {
          color: var(--error-color, #dc2626);
        }

        .input, .select {
          padding: 0.75rem;
          border: 1px solid var(--border-color, #d1d5db);
          border-radius: 0.5rem;
          font-size: 1rem;
          transition: border-color 0.2s;
        }

        .input:focus, .select:focus {
          outline: none;
          border-color: var(--primary-color, #2563eb);
          box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }

        .textarea {
          min-height: 200px;
          resize: vertical;
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
          font-size: 0.875rem;
          line-height: 1.5;
        }

        .help-text {
          font-size: 0.875rem;
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

        .form-actions {
          display: flex;
          gap: 1rem;
          justify-content: flex-end;
          margin-top: 1rem;
        }

        .btn {
          padding: 0.75rem 1.5rem;
          border-radius: 0.5rem;
          font-weight: 500;
          cursor: pointer;
          transition: background-color 0.2s;
          border: none;
        }

        .btn-primary {
          background: var(--primary-color, #2563eb);
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
          background: var(--primary-hover, #1d4ed8);
        }

        .btn-secondary {
          background: var(--bg-secondary, #f3f4f6);
          color: var(--text-color, #374151);
        }

        .btn-secondary:hover {
          background: var(--bg-hover, #e5e7eb);
        }

        .btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .loading {
          text-align: center;
          padding: 2rem;
          color: var(--text-muted, #6b7280);
        }

        .json-validator {
          margin-top: 0.5rem;
          padding: 0.5rem;
          border-radius: 0.25rem;
          font-size: 0.875rem;
        }

        .json-validator.valid {
          background: #f0fdf4;
          color: #166534;
          border: 1px solid #bbf7d0;
        }

        .json-validator.invalid {
          background: #fef2f2;
          color: #dc2626;
          border: 1px solid #fecaca;
        }
      </style>

      <div class="form-header">
        <h2 class="form-title" id="form-title">Create Configuration</h2>
        <button class="close-btn" id="close-btn">×</button>
      </div>

      <div id="error-container"></div>

      <div id="loading" class="loading" style="display: none;">
        Loading...
      </div>

      <form class="form" id="configuration-form">
        <div class="field">
          <label class="label" for="name">
            Name <span class="required">*</span>
          </label>
          <input
            type="text"
            id="name"
            name="name"
            class="input"
            required
            placeholder="Enter configuration name"
          />
        </div>

        <div class="field-row">
          <div class="field">
            <label class="label" for="application_id">
              Application <span class="required">*</span>
            </label>
            <select
              id="application_id"
              name="application_id"
              class="select"
              required
            >
              <option value="">Select an application</option>
            </select>
          </div>

          <div class="field">
            <label class="label" for="environment">
              Environment <span class="required">*</span>
            </label>
            <select
              id="environment"
              name="environment"
              class="select"
              required
            >
              <option value="">Select environment</option>
              <option value="development">Development</option>
              <option value="staging">Staging</option>
              <option value="production">Production</option>
              <option value="testing">Testing</option>
            </select>
          </div>
        </div>

        <div class="field">
          <label class="label" for="configuration_data">
            Configuration Data <span class="required">*</span>
          </label>
          <textarea
            id="configuration_data"
            name="configuration_data"
            class="input textarea"
            required
            placeholder="Enter JSON configuration data"
          ></textarea>
          <div class="help-text">
            Enter valid JSON configuration data. This will be validated before saving.
          </div>
          <div id="json-validator" class="json-validator" style="display: none;"></div>
        </div>

        <div class="form-actions">
          <button type="button" class="btn btn-secondary" id="cancel-btn">
            Cancel
          </button>
          <button type="submit" class="btn btn-primary" id="submit-btn">
            Create Configuration
          </button>
        </div>
      </form>
    `);
  }

  connectedCallback(): void {
    super.connectedCallback();
    this.loadApplications();

    const configurationId = this.getAttribute('configuration-id');
    if (configurationId) {
      this.loadConfiguration(configurationId);
    }
  }

  attributeChangedCallback(name: string, oldValue: string, newValue: string): void {
    if (name === 'configuration-id' && newValue !== oldValue) {
      if (newValue) {
        this.loadConfiguration(newValue);
      } else {
        this.configuration = null;
        this.updateFormForMode();
      }
    }

    if (name === 'default-application-id' && newValue !== oldValue) {
      // Set default application when form is for creating new configuration
      if (newValue && !this.configuration) {
        setTimeout(() => {
          const applicationSelect = this.query('#application_id') as HTMLSelectElement;
          if (applicationSelect) {
            applicationSelect.value = newValue;
          }
        }, 100);
      }
    }
  }

  protected attachEventListeners(): void {
    const form = this.query('#configuration-form') as HTMLFormElement;
    const closeBtn = this.query('#close-btn');
    const cancelBtn = this.query('#cancel-btn');
    const configDataTextarea = this.query('#configuration_data') as HTMLTextAreaElement;

    form?.addEventListener('submit', (event) => {
      event.preventDefault();
      this.handleSubmit();
    });

    closeBtn?.addEventListener('click', () => {
      this.dispatchCustomEvent('form-cancelled');
    });

    cancelBtn?.addEventListener('click', () => {
      this.dispatchCustomEvent('form-cancelled');
    });

    // JSON validation
    configDataTextarea?.addEventListener('input', () => {
      this.validateJson();
    });
  }

  private async loadApplications(): Promise<void> {
    this.applicationsLoading = true;

    try {
      const response = await applicationService.getApplications({ limit: 100 });
      this.applications = response.items;
      this.populateApplicationSelect();
    } catch (error) {
      this.error = error instanceof Error ? error.message : 'Failed to load applications';
    } finally {
      this.applicationsLoading = false;
    }
  }

  private async loadConfiguration(id: string): Promise<void> {
    this.loading = true;
    this.error = null;
    this.render();

    try {
      this.configuration = await configurationService.getConfiguration(id);
      this.populateForm();
    } catch (error) {
      this.error = error instanceof Error ? error.message : 'Failed to load configuration';
    } finally {
      this.loading = false;
      this.updateFormForMode();
      this.render();
    }
  }

  private populateApplicationSelect(): void {
    const select = this.query('#application_id') as HTMLSelectElement;
    if (!select) return;

    // Clear existing options except the first one
    select.innerHTML = '<option value="">Select an application</option>';

    // Add application options
    this.applications.forEach(app => {
      const option = document.createElement('option');
      option.value = app.id;
      option.textContent = app.name;
      select.appendChild(option);
    });

    // Set selected value if editing
    if (this.configuration) {
      select.value = this.configuration.application_id;
    }
  }

  private populateForm(): void {
    if (!this.configuration) return;

    const nameInput = this.query('#name') as HTMLInputElement;
    const applicationSelect = this.query('#application_id') as HTMLSelectElement;
    const environmentSelect = this.query('#environment') as HTMLSelectElement;
    const configDataTextarea = this.query('#configuration_data') as HTMLTextAreaElement;

    if (nameInput) nameInput.value = this.configuration.name;
    if (applicationSelect) applicationSelect.value = this.configuration.application_id;
    if (environmentSelect) environmentSelect.value = this.configuration.environment;
    if (configDataTextarea) {
      configDataTextarea.value = JSON.stringify(this.configuration.configuration_data, null, 2);
      this.validateJson();
    }
  }

  private updateFormForMode(): void {
    const isEditing = !!this.configuration;

    const title = this.query('#form-title');
    const submitBtn = this.query('#submit-btn');

    if (title) {
      title.textContent = isEditing ? 'Edit Configuration' : 'Create Configuration';
    }

    if (submitBtn) {
      submitBtn.textContent = isEditing ? 'Update Configuration' : 'Create Configuration';
    }
  }

  private validateJson(): void {
    const textarea = this.query('#configuration_data') as HTMLTextAreaElement;
    const validator = this.query('#json-validator');

    if (!textarea || !validator) return;

    const value = textarea.value.trim();
    if (!value) {
      (validator as HTMLElement).style.display = 'none';
      return;
    }

    try {
      JSON.parse(value);
      validator.className = 'json-validator valid';
      validator.textContent = '✓ Valid JSON format';
      (validator as HTMLElement).style.display = 'block';
    } catch (error) {
      validator.className = 'json-validator invalid';
      validator.textContent = `✗ Invalid JSON: ${(error as Error).message}`;
      (validator as HTMLElement).style.display = 'block';
    }
  }

  private async handleSubmit(): Promise<void> {
    const form = this.query('#configuration-form') as HTMLFormElement;
    if (!form) return;

    const formData = new FormData(form);
    const configDataText = formData.get('configuration_data') as string;

    // Basic validation
    const name = (formData.get('name') as string).trim();
    const applicationId = formData.get('application_id') as string;
    const environment = formData.get('environment') as string;

    if (!name) {
      this.error = 'Configuration name is required';
      this.render();
      return;
    }

    if (!applicationId) {
      this.error = 'Application selection is required';
      this.render();
      return;
    }

    if (!environment) {
      this.error = 'Environment selection is required';
      this.render();
      return;
    }

    if (!configDataText.trim()) {
      this.error = 'Configuration data is required';
      this.render();
      return;
    }

    // Validate JSON
    let configurationData: any;
    try {
      configurationData = JSON.parse(configDataText);
    } catch (error) {
      this.error = `Invalid JSON format: ${(error as Error).message}`;
      this.render();
      return;
    }

    this.loading = true;
    this.error = null;
    this.render();

    try {
      let result: Configuration;

      if (this.configuration) {
        // Update existing configuration
        const updateData: ConfigurationUpdate = {};
        if (name !== this.configuration.name) updateData.name = name;
        if (applicationId !== this.configuration.application_id) updateData.application_id = applicationId;
        if (environment !== this.configuration.environment) updateData.environment = environment;
        if (JSON.stringify(configurationData) !== JSON.stringify(this.configuration.configuration_data)) {
          updateData.configuration_data = configurationData;
        }

        result = await configurationService.updateConfiguration(this.configuration.id, updateData);
        this.dispatchCustomEvent('configuration-updated', { configuration: result });
      } else {
        // Create new configuration
        const createData: ConfigurationCreate = {
          name,
          application_id: applicationId,
          environment,
          configuration_data: configurationData
        };

        result = await configurationService.createConfiguration(createData);
        this.dispatchCustomEvent('configuration-created', { configuration: result });
      }

      // Reset form
      form.reset();
      const validator = this.query('#json-validator');
      if (validator) (validator as HTMLElement).style.display = 'none';
    } catch (error) {
      this.error = error instanceof Error ? error.message : 'Failed to save configuration';
    } finally {
      this.loading = false;
      this.render();
    }
  }

  protected render(): void {
    super.render();

    // Update loading state
    const loading = this.query('#loading');
    const form = this.query('#configuration-form');

    if (loading && form) {
      if (this.loading) {
        (loading as HTMLElement).style.display = 'block';
        (form as HTMLElement).style.display = 'none';
      } else {
        (loading as HTMLElement).style.display = 'none';
        (form as HTMLElement).style.display = 'block';
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

    // Update submit button state
    const submitBtn = this.query('#submit-btn') as HTMLButtonElement;
    if (submitBtn) {
      submitBtn.disabled = this.loading || this.applicationsLoading;
    }

    // Populate applications if loaded
    if (!this.applicationsLoading && this.applications.length > 0) {
      this.populateApplicationSelect();
    }
  }

  private escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

ComponentRegistry.register('configuration-form', ConfigurationForm);