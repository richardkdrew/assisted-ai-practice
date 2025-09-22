/**
 * Application form component for creating and editing applications
 */

import { BaseComponent } from '@/components/base/BaseComponent';
import { ComponentRegistry } from '@/components/base/ComponentRegistry';
import { applicationService } from '@/services/ApplicationService';
import type { Application, ApplicationCreate, ApplicationUpdate } from '@/types/domain';

export class ApplicationForm extends BaseComponent {
  private application: Application | null = null;
  private loading: boolean = false;
  private error: string | null = null;

  static get observedAttributes(): string[] {
    return ['application-id'];
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

        .label {
          font-weight: 500;
          color: var(--text-color, #374151);
        }

        .required {
          color: var(--error-color, #dc2626);
        }

        .input {
          padding: 0.75rem;
          border: 1px solid var(--border-color, #d1d5db);
          border-radius: 0.5rem;
          font-size: 1rem;
          transition: border-color 0.2s;
        }

        .input:focus {
          outline: none;
          border-color: var(--primary-color, #2563eb);
          box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }

        .textarea {
          min-height: 100px;
          resize: vertical;
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
      </style>

      <div class="form-header">
        <h2 class="form-title" id="form-title">Create Application</h2>
        <button class="close-btn" id="close-btn">×</button>
      </div>

      <div id="error-container"></div>

      <div id="loading" class="loading" style="display: none;">
        Loading...
      </div>

      <form class="form" id="application-form">
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
            placeholder="Enter application name"
          />
        </div>

        <div class="field">
          <label class="label" for="comments">
            Comments
          </label>
          <textarea
            id="comments"
            name="comments"
            class="input textarea"
            placeholder="Optional description or comments"
          ></textarea>
        </div>

        <div class="form-actions">
          <button type="button" class="btn btn-secondary" id="cancel-btn">
            Cancel
          </button>
          <button type="submit" class="btn btn-primary" id="submit-btn">
            Create Application
          </button>
        </div>
      </form>
    `);
  }

  connectedCallback(): void {
    super.connectedCallback();

    const applicationId = this.getAttribute('application-id');
    if (applicationId) {
      this.loadApplication(applicationId);
    }
  }

  attributeChangedCallback(name: string, oldValue: string, newValue: string): void {
    if (name === 'application-id' && newValue !== oldValue) {
      if (newValue) {
        this.loadApplication(newValue);
      } else {
        this.application = null;
        this.updateFormForMode();
      }
    }
  }

  protected attachEventListeners(): void {
    const form = this.query('#application-form') as HTMLFormElement;
    const closeBtn = this.query('#close-btn');
    const cancelBtn = this.query('#cancel-btn');

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
  }

  private async loadApplication(id: string): Promise<void> {
    this.loading = true;
    this.error = null;
    this.render();

    try {
      this.application = await applicationService.getApplication(id);
    } catch (error) {
      this.error = error instanceof Error ? error.message : 'Failed to load application';
    } finally {
      this.loading = false;
      this.updateFormForMode();
      this.render();
      // Populate form after render to ensure DOM elements exist
      if (this.application && !this.error) {
        this.populateForm();
      }
    }
  }

  private populateForm(): void {
    if (!this.application) return;

    // Use a small delay to ensure DOM is fully rendered
    setTimeout(() => {
      const nameInput = this.query('#name') as HTMLInputElement;
      const commentsInput = this.query('#comments') as HTMLTextAreaElement;

      if (nameInput && this.application) {
        nameInput.value = this.application.name;
      }
      if (commentsInput && this.application) {
        commentsInput.value = this.application.comments || '';
      }
    }, 10);
  }

  private updateFormForMode(): void {
    const isEditing = !!this.application;

    const title = this.query('#form-title');
    const submitBtn = this.query('#submit-btn');

    if (title) {
      title.textContent = isEditing ? 'Edit Application' : 'Create Application';
    }

    if (submitBtn) {
      submitBtn.textContent = isEditing ? 'Update Application' : 'Create Application';
    }
  }

  private async handleSubmit(): Promise<void> {
    const form = this.query('#application-form') as HTMLFormElement;
    if (!form) return;

    const formData = new FormData(form);
    const data = {
      name: formData.get('name') as string,
      comments: formData.get('comments') as string || undefined
    };

    // Basic validation
    if (!data.name.trim()) {
      this.error = 'Application name is required';
      this.render();
      return;
    }

    this.loading = true;
    this.error = null;
    this.render();

    try {
      let result: Application;

      if (this.application) {
        // Update existing application
        const updateData: ApplicationUpdate = {};
        if (data.name !== this.application.name) updateData.name = data.name;
        if (data.comments !== this.application.comments) updateData.comments = data.comments;

        result = await applicationService.updateApplication(this.application.id, updateData);
        this.dispatchCustomEvent('application-updated', { application: result });
      } else {
        // Create new application
        const createData: ApplicationCreate = {
          name: data.name,
          comments: data.comments
        };

        result = await applicationService.createApplication(createData);
        this.dispatchCustomEvent('application-created', { application: result });
      }

      // Reset form and clear application data for next use
      form.reset();
      this.application = null;
      this.updateFormForMode();
    } catch (error) {
      this.error = error instanceof Error ? error.message : 'Failed to save application';
    } finally {
      this.loading = false;
      this.render();
    }
  }

  protected render(): void {
    super.render();

    // Update loading state
    const loading = this.query('#loading');
    const form = this.query('#application-form');

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
      submitBtn.disabled = this.loading;
    }
  }

  private escapeHtml(text: string): string {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

ComponentRegistry.register('application-form', ApplicationForm);