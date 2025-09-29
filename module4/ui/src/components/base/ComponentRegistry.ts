/**
 * Component registry for managing Web Component definitions
 * Provides centralized registration and prevents duplicate registrations
 */

type ComponentConstructor = new () => HTMLElement;

export class ComponentRegistry {
  private static registeredComponents = new Set<string>();

  /**
   * Register a custom element if not already registered
   */
  static register(name: string, constructor: ComponentConstructor): void {
    if (!customElements.get(name) && !this.registeredComponents.has(name)) {
      customElements.define(name, constructor);
      this.registeredComponents.add(name);
      console.debug(`Registered component: ${name}`);
    }
  }

  /**
   * Check if a component is registered
   */
  static isRegistered(name: string): boolean {
    return this.registeredComponents.has(name);
  }

  /**
   * Get all registered component names
   */
  static getRegistered(): string[] {
    return Array.from(this.registeredComponents);
  }
}