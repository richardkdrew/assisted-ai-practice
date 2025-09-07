import { ConfigurationListItem, ConfigKeyValue } from '../models/configuration.js';
import { configurationService } from '../services/configuration-service.js';

export class ConfigurationForm extends HTMLElement {
  private configuration: ConfigurationListItem | null = null;
  private applicationId: string | null = null;
  private formData = {
    name: '',
    comments: '',
    config: {} as Record<string, any>
  };
  private configPairs: ConfigKeyValue[] = [];
  private errors: Record<string, string> = {};

  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  static get observedAttributes(): string[] {
    return ['configuration', 'application-id'];
  }

  attributeChangedCallback(name: string, oldValue: string, newValue: string): void {
    if (name === 'configuration' && newValue) {
      try {
        this.configuration = JSON.parse(newValue);
        if (this.configuration) {
          this.loadConfigurationData();
        }
      } catch (e) {
        console.error('Failed to parse configuration data:', e);
      }
    } else if (name === 'application-id') {
      this.applicationId = newValue;
    }
  }

  connectedCallback(): void {
    this.render();
  }

  private async loadConfigurationData(): Promise<void> {
    if (!this.configuration) return;

    try {
      const response = await configurationService.getById(this.configuration.id);
      if (response.data) {
        const config = response.data;
        this.formData = {
          name: config.name,
          comments: config.comments || '',
          config: config.config
        };
        this.configPairs = this.convertConfigToKeyValuePairs(config.config);
        this.render();
      }
    } catch (err) {
      console.error('Failed to load configuration details:', err);
    }
  }

  private convertConfigToKeyValuePairs(config: Record<string, any>): ConfigKeyValue[] {
    return Object.entries(config).map(([key, value]) => ({
      key,
      value,
      type: this.getValueType(value)
    }));
  }

  private getValueType(value: any): 'string' | 'number' | 'boolean' | 'object' {
    if (typeof value === 'string') return 'string';
    if (typeof value === 'number') return 'number';
    if (typeof value === 'boolean') return 'boolean';
    return 'object';
  }

  private convertKeyValuePairsToConfig(): Record<string, any> {
    const config: Record<string, any> = {};
    
    this.configPairs.forEach(pair => {
      if (pair.key.trim()) {
        let value = pair.value;
        
        // Convert value based on type
        switch (pair.type) {
          case 'number':
            value = parseFloat(value);
            if (isNaN(value)) value = 0;
            break;
          case 'boolean':
            value = value === 'true' || value === true;
            break;
          case 'object':
            try {
              value = JSON.parse(value);
            } catch {
              value = value; // Keep as string if JSON parsing fails
            }
            break;
          default:
            value = String(value);
        }
        
        config[pair.key.trim()] = value;
      }
    });
    
    return config;
  }

  private validateForm(): boolean {
    this.errors = {};

    if (!this.formData.name.trim()) {
      this.errors.name = 'Configuration name is required';
    } else if (this.formData.name.length > 256) {
      this.errors.name = 'Configuration name must be 256 characters or less';
    }

    if (this.formData.comments && this.formData.comments.length > 1024) {
      this.errors.comments = 'Comments must be 1024 characters or less';
    }

    // Validate config pairs
    const usedKeys = new Set<string>();
    let hasConfigErrors = false;

    this.configPairs.forEach((pair, index) => {
      if (pair.key.trim()) {
        if (usedKeys.has(pair.key.trim())) {
          this.errors[`config_key_${index}`] = 'Duplicate key';
          hasConfigErrors = true;
        } else {
          usedKeys.add(pair.key.trim());
        }

        // Validate JSON for object type
        if (pair.type === 'object') {
          try {
            JSON.parse(pair.value);
          } catch {
            this.errors[`config_value_${index}`] = 'Invalid JSON';
            hasConfigErrors = true;
          }
        }
      }
    });

    if (this.configPairs.length === 0 || this.configPairs.every(pair => !pair.key.trim())) {
      this.errors.config = 'At least one configuration key-value pair is required';
      hasConfigErrors = true;
    }

    return Object.keys(this.errors).length === 0;
  }

  private handleSubmit(event: Event): void {
    event.preventDefault();
    
    this.formData.config = this.convertKeyValuePairsToConfig();
    
    if (this.validateForm()) {
      const submitEvent = new CustomEvent('form-submit', {
        detail: {
          name: this.formData.name.trim(),
          comments: this.formData.comments.trim() || undefined,
          config: this.formData.config
        },
        bubbles: true,
        composed: true
      });
      this.dispatchEvent(submitEvent);
    } else {
      this.render();
    }
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
    
    if (field === 'name' || field === 'comments') {
      this.formData[field] = target.value;
      
      // Clear error for this field when user starts typing
      if (this.errors[field]) {
        delete this.errors[field];
        this.render();
      }
    }
  }

  private addConfigPair(): void {
    this.configPairs.push({
      key: '',
      value: '',
      type: 'string'
    });
    this.render();
  }

  private removeConfigPair(index: number): void {
    this.configPairs.splice(index, 1);
    this.render();
  }

  private updateConfigPair(index: number, field: 'key' | 'value' | 'type', value: string): void {
    if (this.configPairs[index]) {
      this.configPairs[index][field] = value as any;
      
      // Clear errors for this pair
      delete this.errors[`config_key_${index}`];
      delete this.errors[`config_value_${index}`];
      delete this.errors.config;
    }
  }

  private render(): void {
    if (!this.shadowRoot) return;

    const isEditing = !!this.configuration;
    const title = isEditing ? 'Edit Configuration' : 'Create Configuration';

    // Initialize with one empty pair if none exist
    if (this.configPairs.length === 0) {
      this.configPairs.push({
        key: '',
        value: '',
        type: 'string'
      });
    }

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
        
        .config-section {
          margin-top: 2rem;
          padding-top: 1rem;
          border-top: 1px solid #e0e0e0;
        }
        
        .config-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }
        
        .config-title {
          font-size: 1.1rem;
          font-weight: 600;
          color: #2c3e50;
          margin: 0;
        }
        
        .config-pair {
          display: grid;
          grid-template-columns: 1fr 1fr auto auto auto;
          gap: 0.5rem;
          align-items: start;
          margin-bottom: 0.5rem;
          padding: 0.5rem;
          background: #f8f9fa;
          border-radius: 4px;
        }
        
        .config-pair-input {
          padding: 0.4rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 0.85rem;
        }
        
        .config-pair-input:focus {
          outline: none;
          border-color: #3498db;
        }
        
        .config-pair-input.error {
          border-color: #e74c3c;
        }
        
        .config-pair-select {
          padding: 0.4rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 0.85rem;
          background: white;
        }
        
        .config-pair-textarea {
          min-height: 60px;
          resize: vertical;
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
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
        
        .btn-small {
          padding: 0.25rem 0.5rem;
          font-size: 0.8rem;
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
        
        .btn-secondary {
          background: #95a5a6;
          color: white;
        }
        
        .btn-secondary:hover {
          background: #7f8c8d;
        }
        
        .form-actions {
          display: flex;
          gap: 0.5rem;
          margin-top: 1.5rem;
          padding-top: 1rem;
          border-top: 1px solid #e0e0e0;
        }
        
        .btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
        
        .config-labels {
          display: grid;
          grid-template-columns: 1fr 1fr auto auto auto;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
          font-size: 0.8rem;
          font-weight: 500;
          color: #7f8c8d;
        }
      </style>
      
      <div class="form-card">
        <div class="form-header">
          <h3 class="form-title">${title}</h3>
        </div>
        
        <form id="configuration-form">
          <div class="form-group">
            <label class="form-label required" for="name">Configuration Name</label>
            <input
              type="text"
              id="name"
              name="name"
              class="form-input ${this.errors.name ? 'error' : ''}"
              value="${this.formData.name}"
              placeholder="Enter configuration name"
              maxlength="256"
              required
            />
            ${this.errors.name ? `<div class="form-error">${this.errors.name}</div>` : ''}
            <div class="form-help">Must be unique per application and up to 256 characters</div>
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
          
          <div class="config-section">
            <div class="config-header">
              <h4 class="config-title">Configuration Values</h4>
              <button type="button" class="btn btn-success btn-small" id="add-config-btn">
                Add Key-Value Pair
              </button>
            </div>
            
            ${this.errors.config ? `<div class="form-error">${this.errors.config}</div>` : ''}
            
            <div class="config-labels">
              <div>Key</div>
              <div>Value</div>
              <div>Type</div>
              <div></div>
              <div></div>
            </div>
            
            ${this.renderConfigPairs()}
          </div>
          
          <div class="form-actions">
            <button type="submit" class="btn btn-primary">
              ${isEditing ? 'Update Configuration' : 'Create Configuration'}
            </button>
            <button type="button" class="btn btn-secondary" id="cancel-btn">
              Cancel
            </button>
          </div>
        </form>
      </div>
    `;

    this.setupEventListeners();
  }

  private renderConfigPairs(): string {
    return this.configPairs.map((pair, index) => `
      <div class="config-pair">
        <input
          type="text"
          class="config-pair-input ${this.errors[`config_key_${index}`] ? 'error' : ''}"
          placeholder="Key"
          value="${pair.key}"
          data-index="${index}"
          data-field="key"
        />
        ${pair.type === 'object' ? `
          <textarea
            class="config-pair-input config-pair-textarea ${this.errors[`config_value_${index}`] ? 'error' : ''}"
            placeholder="JSON value"
            data-index="${index}"
            data-field="value"
          >${typeof pair.value === 'object' ? JSON.stringify(pair.value, null, 2) : pair.value}</textarea>
        ` : `
          <input
            type="${pair.type === 'number' ? 'number' : pair.type === 'boolean' ? 'text' : 'text'}"
            class="config-pair-input ${this.errors[`config_value_${index}`] ? 'error' : ''}"
            placeholder="Value"
            value="${pair.type === 'boolean' ? (pair.value ? 'true' : 'false') : pair.value}"
            data-index="${index}"
            data-field="value"
          />
        `}
        <select
          class="config-pair-select"
          data-index="${index}"
          data-field="type"
        >
          <option value="string" ${pair.type === 'string' ? 'selected' : ''}>String</option>
          <option value="number" ${pair.type === 'number' ? 'selected' : ''}>Number</option>
          <option value="boolean" ${pair.type === 'boolean' ? 'selected' : ''}>Boolean</option>
          <option value="object" ${pair.type === 'object' ? 'selected' : ''}>JSON</option>
        </select>
        <button
          type="button"
          class="btn btn-danger btn-small"
          data-action="remove-config"
          data-index="${index}"
          ${this.configPairs.length === 1 ? 'disabled' : ''}
        >
          Remove
        </button>
        <div>
          ${this.errors[`config_key_${index}`] ? `<div class="form-error">${this.errors[`config_key_${index}`]}</div>` : ''}
          ${this.errors[`config_value_${index}`] ? `<div class="form-error">${this.errors[`config_value_${index}`]}</div>` : ''}
        </div>
      </div>
    `).join('');
  }

  private setupEventListeners(): void {
    const form = this.shadowRoot?.getElementById('configuration-form') as HTMLFormElement;
    form?.addEventListener('submit', this.handleSubmit.bind(this));

    const cancelBtn = this.shadowRoot?.getElementById('cancel-btn');
    cancelBtn?.addEventListener('click', this.handleCancel.bind(this));

    const addConfigBtn = this.shadowRoot?.getElementById('add-config-btn');
    addConfigBtn?.addEventListener('click', this.addConfigPair.bind(this));

    // Basic input change listeners
    const basicInputs = this.shadowRoot?.querySelectorAll('input[name], textarea[name]');
    basicInputs?.forEach(input => {
      input.addEventListener('input', this.handleInputChange.bind(this));
    });

    // Config pair input listeners
    const configInputs = this.shadowRoot?.querySelectorAll('[data-index]');
    configInputs?.forEach(input => {
      input.addEventListener('input', (e) => {
        const target = e.target as HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement;
        const index = parseInt(target.dataset.index || '0');
        const field = target.dataset.field as 'key' | 'value' | 'type';
        this.updateConfigPair(index, field, target.value);
      });
    });

    // Remove config pair buttons
    const removeButtons = this.shadowRoot?.querySelectorAll('[data-action="remove-config"]');
    removeButtons?.forEach(button => {
      button.addEventListener('click', (e) => {
        const target = e.target as HTMLButtonElement;
        const index = parseInt(target.dataset.index || '0');
        this.removeConfigPair(index);
      });
    });
  }
}

customElements.define('configuration-form', ConfigurationForm);
