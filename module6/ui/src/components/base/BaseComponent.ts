/**
 * Abstract base component for all Web Components in the application.
 * Provides common functionality and follows SOLID principles.
 */
export abstract class BaseComponent extends HTMLElement {
  protected shadow: ShadowRoot;
  protected template: HTMLTemplateElement;
  private isInitialized: boolean = false;

  constructor() {
    super();
    this.shadow = this.attachShadow({ mode: 'open' });
    this.template = this.createTemplate();
  }

  /**
   * Called when the component is added to the DOM
   */
  connectedCallback(): void {
    if (!this.isInitialized) {
      this.render();
      this.attachEventListeners();
      this.isInitialized = true;
    }
  }

  /**
   * Called when the component is removed from the DOM
   */
  disconnectedCallback(): void {
    this.cleanup();
  }

  /**
   * Abstract method to create the component's template
   */
  protected abstract createTemplate(): HTMLTemplateElement;

  /**
   * Render the component's template into the shadow DOM
   */
  protected render(): void {
    // Clear shadow DOM first to prevent duplication
    this.shadow.innerHTML = '';

    // Clone and append template
    const clone = this.template.content.cloneNode(true);
    this.shadow.appendChild(clone);
  }

  /**
   * Attach event listeners for the component
   * Override in subclasses to add specific event handling
   */
  protected attachEventListeners(): void {
    // Default implementation - override in subclasses
  }

  /**
   * Cleanup resources when component is destroyed
   * Override in subclasses to clean up specific resources
   */
  protected cleanup(): void {
    // Default implementation - override in subclasses
  }

  /**
   * Query a single element within the shadow DOM
   */
  protected query<T extends Element = Element>(selector: string): T | null {
    return this.shadow.querySelector<T>(selector);
  }

  /**
   * Query all elements within the shadow DOM
   */
  protected queryAll<T extends Element = Element>(selector: string): NodeListOf<T> {
    return this.shadow.querySelectorAll<T>(selector);
  }

  /**
   * Dispatch a custom event from this component
   */
  protected dispatchCustomEvent(type: string, detail?: any): void {
    const event = new CustomEvent(type, {
      detail,
      bubbles: true,
      composed: true
    });
    this.dispatchEvent(event);
  }

  /**
   * Helper method to create a template element with HTML content
   */
  protected createTemplateFromHTML(html: string): HTMLTemplateElement {
    const template = document.createElement('template');
    template.innerHTML = html;
    return template;
  }
}