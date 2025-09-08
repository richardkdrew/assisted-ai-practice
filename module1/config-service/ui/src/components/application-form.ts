import { ApplicationListItem } from '../models/application';

export class ApplicationForm extends HTMLElement {
  private application: ApplicationListItem | null = null;
  private formData = {
    name: '',
    comments: ''
  };
  private errors: Record<string, string> = {};
  private submitting = false;

  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes(): string[] {
    return ['application'];
  }

  attributeChangedCallback(name: string, oldValue: string, newValue: string): void {
    if (name === 'application' && newValue) {
      try {
        this.application = JSON.parse(newValue);
        if (this.application) {
          this.formData = {
            name: this.application.name,
            comments: this.application.comments || ''
          };
        }
      } catch (e) {
        console.error('Failed to parse application data:', e);
      }
    }
  }

  connectedCallback(): void {
    this.render();
  }

  private validateForm(): boolean {
    this.errors = {};

    if (!this.formData.name.trim()) {
      this.errors.name = 'Application name is required';
    } else if (this.formData.name.length > 256) {
      this.errors.name = 'Application name must be 256 characters or less';
    }

    if (this.formData.comments && this.formData.comments.length > 1024) {
      this.errors.comments = 'Comments must be 1024 characters or less';
    }

    return Object.keys(this.errors).length === 0;
  }

  private handleSubmit(event: Event): void {
    event.preventDefault();
    
    // Prevent multiple submissions
    if (this.submitting) {
      return;
    }
    
    if (this.validateForm()) {
      this.submitting = true;
      this.render();
      
      const submitEvent = new CustomEvent('form-submit', {
        detail: {
          name: this.formData.name.trim(),
          comments: this.formData.comments.trim() || undefined
        },
        bubbles: true,
        composed: true
      });
      this.dispatchEvent(submitEvent);
    } else {
      this.render();
    }
  }

  // Method to reset submitting state (called by parent component)
  resetSubmitting(): void {
    this.submitting = false;
    this.render();
  }

  private handleCancel(): void {
    const cancelEvent = new CustomEvent('form-cancel', {
      bubbles: true,
      composed: true
    });
    this.dispatchEvent(cancelEvent);
  }

  private handleInputChange(event: Event): void {
    const target = event.target as HTMLInputElement | HTMLTextAreaElement;
    const field = target.name as keyof typeof this.formData;
    this.formData[field] = target.value;
    
    // Clear error for this field when user starts typing
    if (this.errors[field]) {
      delete this.errors[field];
      this.render();
    }
  }

  private render(): void {
    if (!this.shadowRoot) return;

    const isEditing = !!this.application;
    const title = isEditing ? 'Edit Application' : 'Create Application';

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          margin-bottom: 2rem;
        }
        
        .form-card {
          background: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          padding: 1.5rem;
          margin-bottom: 1rem;
        }
        
        .form-header {
          margin-bottom: 1.5rem;
          padding-bottom: 0.5rem;
          border-bottom: 1px solid #e0e0e0;
        }
        
        .form-title {
          font-size: 1.25rem;
          font-weight: 600;
          color: #2c3e50;
          margin: 0;
        }
        
        .form-group {
          margin-bottom: 1rem;
        }
        
        .form-label {
          display: block;
          margin-bottom: 0.25rem;
          font-weight: 500;
          color: #2c3e50;
        }
        
        .form-label.required::after {
          content: ' *';
          color: #e74c3c;
        }
        
        .form-input {
          width: 100%;
          padding: 0.5rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 0.9rem;
          font-family: inherit;
          box-sizing: border-box;
        }
        
        .form-input:focus {
          outline: none;
          border-color: #3498db;
          box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
        }
        
        .form-input.error {
          border-color: #e74c3c;
        }
        
        .form-textarea {
          min-height: 80px;
          resize: vertical;
        }
        
        .form-error {
          color: #e74c3c;
          font-size: 0.8rem;
          margin-top: 0.25rem;
        }
        
        .form-help {
          color: #7f8c8d;
          font-size: 0.8rem;
          margin-top: 0.25rem;
        }
        
        .form-actions {
          display: flex;
          gap: 0.5rem;
          margin-top: 1.5rem;
          padding-top: 1rem;
          border-top: 1px solid #e0e0e0;
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
        
        .btn-secondary {
          background: #95a5a6;
          color: white;
        }
        
        .btn-secondary:hover {
          background: #7f8c8d;
        }
        
        .btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
      </style>
      
      <div class="form-card">
        <div class="form-header">
          <h3 class="form-title">${title}</h3>
        </div>
        
        <form id="application-form">
          <div class="form-group">
            <label class="form-label required" for="name">Application Name</label>
            <input
              type="text"
              id="name"
              name="name"
              class="form-input ${this.errors.name ? 'error' : ''}"
              value="${this.formData.name}"
              placeholder="Enter application name"
              maxlength="256"
              required
            />
            ${this.errors.name ? `<div class="form-error">${this.errors.name}</div>` : ''}
            <div class="form-help">Must be unique and up to 256 characters</div>
          </div>
          
          <div class="form-group">
            <label class="form-label" for="comments">Comments</label>
            <textarea
              id="comments"
              name="comments"
              class="form-input form-textarea ${this.errors.comments ? 'error' : ''}"
              placeholder="Optional description or comments"
              maxlength="1024"
            >${this.formData.comments}</textarea>
            ${this.errors.comments ? `<div class="form-error">${this.errors.comments}</div>` : ''}
            <div class="form-help">Optional description up to 1024 characters</div>
          </div>
          
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" ${this.submitting ? 'disabled' : ''}>
              ${this.submitting ? 'Saving...' : (isEditing ? 'Update Application' : 'Create Application')}
            </button>
            <button type="button" class="btn btn-secondary" id="cancel-btn" ${this.submitting ? 'disabled' : ''}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    `;

    this.setupEventListeners();
  }

  private setupEventListeners(): void {
    const form = this.shadowRoot?.getElementById('application-form') as HTMLFormElement;
    form?.addEventListener('submit', this.handleSubmit.bind(this));

    const cancelBtn = this.shadowRoot?.getElementById('cancel-btn');
    cancelBtn?.addEventListener('click', this.handleCancel.bind(this));

    // Input change listeners
    const inputs = this.shadowRoot?.querySelectorAll('.form-input');
    inputs?.forEach(input => {
      input.addEventListener('input', this.handleInputChange.bind(this));
    });
  }
}

customElements.define('application-form', ApplicationForm);
