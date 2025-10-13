/**
 * App router component - wrapper for routing functionality
 */

import { BaseComponent } from '@/components/base/BaseComponent';
import { ComponentRegistry } from '@/components/base/ComponentRegistry';

export class AppRouter extends BaseComponent {
  protected createTemplate(): HTMLTemplateElement {
    return this.createTemplateFromHTML(`
      <style>
        :host {
          display: block;
          width: 100%;
          height: 100%;
        }
      </style>

      <app-main></app-main>
    `);
  }

  protected attachEventListeners(): void {
    // Handle navigation link active states
    this.shadow.addEventListener('click', (event) => {
      const target = event.target as HTMLElement;
      if (target.matches('a')) {
        // Remove active class from all links
        this.queryAll('a').forEach(link => link.classList.remove('active'));
        // Add active class to clicked link
        target.classList.add('active');
      }
    });

    // Handle hash changes to update active state
    window.addEventListener('hashchange', () => {
      this.updateActiveLink();
    });

    // Set initial active state
    this.updateActiveLink();
  }

  private updateActiveLink(): void {
    const hash = window.location.hash || '#/';
    const links = this.queryAll('a');

    links.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === hash) {
        link.classList.add('active');
      }
    });
  }
}

ComponentRegistry.register('app-router', AppRouter);