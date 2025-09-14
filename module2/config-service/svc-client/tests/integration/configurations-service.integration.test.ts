import { describe, it, expect, beforeAll, afterAll, beforeEach, afterEach } from 'vitest';
import { ConfigServiceClient } from '../../src/index.js';
import { Configuration } from '../../src/models/configuration.js';
import { ulid } from 'ulid';

describe('Configurations Service Integration Tests', () => {
  let client: ConfigServiceClient;
  let testApplicationId: string;
  let createdConfigIds: string[] = [];

  beforeAll(async () => {
    // Initialize client with test configuration
    client = new ConfigServiceClient({
      baseUrl: process.env.CONFIG_SERVICE_API_URL || 'http://localhost:8000/api'
    });

    // Create a test application for our tests
    const testApp = await client.applications.create({
      name: `Integration Test App ${Date.now()}`,
      description: 'Application created for integration testing'
    });

    testApplicationId = testApp.id;
  });

  afterAll(async () => {
    // Clean up created configurations
    for (const configId of createdConfigIds) {
      try {
        await client.configurations.delete(configId);
      } catch (error) {
        // Ignore cleanup errors
        console.warn(`Failed to cleanup configuration ${configId}:`, error);
      }
    }

    // Clean up test application
    try {
      await client.applications.delete(testApplicationId);
    } catch (error) {
      console.warn(`Failed to cleanup test application ${testApplicationId}:`, error);
    }
  });

  describe('getByApplicationId', () => {
    beforeEach(async () => {
      // Create test configurations for each test
      const config1 = await client.configurations.create({
        applicationId: testApplicationId,
        name: `Test Config 1 ${Date.now()}`,
        configuration: { 
          database: {
            host: 'localhost',
            port: 5432,
            name: 'testdb'
          }
        },
        comment: 'Database configuration for testing'
      });

      const config2 = await client.configurations.create({
        applicationId: testApplicationId,
        name: `Test Config 2 ${Date.now()}`,
        configuration: { 
          api: {
            baseUrl: 'https://api.test.com',
            timeout: 30000
          }
        },
        comment: 'API configuration for testing'
      });

      createdConfigIds.push(config1.id, config2.id);
    });

    it('should retrieve configurations for a specific application', async () => {
      const configurations = await client.configurations.getByApplicationId(testApplicationId);
      
      expect(Array.isArray(configurations)).toBe(true);
      expect(configurations.length).toBeGreaterThanOrEqual(2);
      
      // Verify all configurations belong to the correct application
      configurations.forEach(config => {
        expect(config.applicationId).toBe(testApplicationId);
        expect(config.id).toBeDefined();
        expect(config.name).toBeDefined();
        expect(config.configuration).toBeDefined();
      });
    });

    it('should support pagination with limit', async () => {
      const configurations = await client.configurations.getByApplicationId(testApplicationId, { 
        limit: 1
      });

      expect(configurations.length).toBeLessThanOrEqual(1);
      
      if (configurations.length > 0) {
        expect(configurations[0].applicationId).toBe(testApplicationId);
      }
    });

    it('should support pagination with limit and offset', async () => {
      // Get first page
      const firstPage = await client.configurations.getByApplicationId(testApplicationId, { 
        limit: 1, 
        offset: 0 
      });

      // Get second page
      const secondPage = await client.configurations.getByApplicationId(testApplicationId, { 
        limit: 1, 
        offset: 1 
      });

      expect(firstPage.length).toBeLessThanOrEqual(1);
      expect(secondPage.length).toBeLessThanOrEqual(1);

      // If both pages have results, ensure they're different configurations
      if (firstPage.length > 0 && secondPage.length > 0) {
        expect(firstPage[0].id).not.toBe(secondPage[0].id);
      }
    });

    it('should handle non-existent application appropriately', async () => {
      // Generate a valid ULID that doesn't exist
      const nonExistentAppId = ulid();
      
      // The backend validates application existence, so this should throw an error
      await expect(
        client.configurations.getByApplicationId(nonExistentAppId)
      ).rejects.toThrow();
    });

    it('should handle invalid application ID format', async () => {
      const invalidAppId = 'invalid-app-id';
      
      await expect(
        client.configurations.getByApplicationId(invalidAppId)
      ).rejects.toThrow();
    });
  });

  describe('Configuration filtering across multiple applications', () => {
    let secondApplicationId: string;
    let app1ConfigIds: string[] = [];
    let app2ConfigIds: string[] = [];

    beforeAll(async () => {
      // Create a second test application
      const secondApp = await client.applications.create({
        name: `Second Integration Test App ${Date.now()}`,
        description: 'Second application for cross-app filtering tests'
      });

      secondApplicationId = secondApp.id;

      // Create configurations for first application
      const app1Config = await client.configurations.create({
        applicationId: testApplicationId,
        name: `App1 Config ${Date.now()}`,
        configuration: { app: 1, feature: 'enabled' },
        comment: 'Configuration for first application'
      });

      // Create configurations for second application
      const app2Config = await client.configurations.create({
        applicationId: secondApplicationId,
        name: `App2 Config ${Date.now()}`,
        configuration: { app: 2, feature: 'disabled' },
        comment: 'Configuration for second application'
      });

      app1ConfigIds.push(app1Config.id);
      app2ConfigIds.push(app2Config.id);
      createdConfigIds.push(app1Config.id, app2Config.id);
    });

    afterAll(async () => {
      // Clean up second application
      try {
        await client.applications.delete(secondApplicationId);
      } catch (error) {
        console.warn(`Failed to cleanup second test application ${secondApplicationId}:`, error);
      }
    });

    it('should only return configurations for the specified application', async () => {
      // Get configurations for first application
      const app1Configs = await client.configurations.getByApplicationId(testApplicationId);
      
      // Get configurations for second application
      const app2Configs = await client.configurations.getByApplicationId(secondApplicationId);

      // Verify first application configurations
      expect(app1Configs.length).toBeGreaterThan(0);
      app1Configs.forEach(config => {
        expect(config.applicationId).toBe(testApplicationId);
      });

      // Verify second application configurations
      expect(app2Configs.length).toBeGreaterThan(0);
      app2Configs.forEach(config => {
        expect(config.applicationId).toBe(secondApplicationId);
      });

      // Verify no cross-contamination
      const app1ConfigIds = app1Configs.map(c => c.id);
      const app2ConfigIds = app2Configs.map(c => c.id);
      
      const intersection = app1ConfigIds.filter(id => app2ConfigIds.includes(id));
      expect(intersection.length).toBe(0);
    });

    it('should maintain filtering consistency across multiple calls', async () => {
      // Make multiple calls to the same application
      const firstCall = await client.configurations.getByApplicationId(testApplicationId);
      const secondCall = await client.configurations.getByApplicationId(testApplicationId);

      // Results should be consistent
      expect(firstCall.length).toBe(secondCall.length);
      
      const firstCallIds = firstCall.map(c => c.id).sort();
      const secondCallIds = secondCall.map(c => c.id).sort();
      
      expect(firstCallIds).toEqual(secondCallIds);
    });
  });

  describe('Configuration CRUD operations with application filtering', () => {
    it('should create and retrieve configuration for specific application', async () => {
      const configName = `CRUD Test Config ${Date.now()}`;
      const configData = {
        database: {
          host: 'crud-test-host',
          port: 3306
        },
        cache: {
          enabled: true,
          ttl: 300
        }
      };

      // Create configuration
      const createdConfig = await client.configurations.create({
        applicationId: testApplicationId,
        name: configName,
        configuration: configData,
        comment: 'Configuration for CRUD testing'
      });

      createdConfigIds.push(createdConfig.id);

      expect(createdConfig).toBeDefined();
      expect(createdConfig.applicationId).toBe(testApplicationId);
      expect(createdConfig.name).toBe(configName);
      expect(createdConfig.configuration).toEqual(configData);

      // Retrieve by application ID and verify it's included
      const appConfigs = await client.configurations.getByApplicationId(testApplicationId);
      const foundConfig = appConfigs.find(c => c.id === createdConfig.id);
      
      expect(foundConfig).toBeDefined();
      expect(foundConfig?.applicationId).toBe(testApplicationId);
      expect(foundConfig?.name).toBe(configName);
    });

    it('should update configuration and maintain application association', async () => {
      // Create initial configuration
      const initialConfig = await client.configurations.create({
        applicationId: testApplicationId,
        name: `Update Test Config ${Date.now()}`,
        configuration: { initial: true },
        comment: 'Initial configuration'
      });

      createdConfigIds.push(initialConfig.id);

      // Update the configuration
      const updatedConfig = await client.configurations.update(initialConfig.id, {
        name: `Updated ${initialConfig.name}`,
        configuration: { initial: false, updated: true },
        comment: 'Updated configuration'
      });

      expect(updatedConfig.applicationId).toBe(testApplicationId);
      expect(updatedConfig.name).toContain('Updated');
      expect(updatedConfig.configuration).toEqual({ initial: false, updated: true });

      // Verify it's still associated with the correct application
      const appConfigs = await client.configurations.getByApplicationId(testApplicationId);
      const foundConfig = appConfigs.find(c => c.id === initialConfig.id);
      
      expect(foundConfig).toBeDefined();
      expect(foundConfig?.applicationId).toBe(testApplicationId);
      expect(foundConfig?.name).toContain('Updated');
    });
  });

  describe('Error handling and edge cases', () => {
    it('should handle empty application gracefully', async () => {
      // Create a new application with no configurations
      const emptyApp = await client.applications.create({
        name: `Empty App ${Date.now()}`,
        description: 'Application with no configurations'
      });

      try {
        const configs = await client.configurations.getByApplicationId(emptyApp.id);
        expect(configs).toEqual([]);
      } finally {
        // Clean up
        await client.applications.delete(emptyApp.id);
      }
    });

    it('should handle malformed application ID', async () => {
      const malformedId = 'not-a-valid-ulid';
      
      await expect(
        client.configurations.getByApplicationId(malformedId)
      ).rejects.toThrow();
    });

    it('should handle network errors gracefully', async () => {
      // Create a client with invalid base URL
      const invalidClient = new ConfigServiceClient({
        baseUrl: 'http://invalid-host:9999/api'
      });

      await expect(
        invalidClient.configurations.getByApplicationId(testApplicationId)
      ).rejects.toThrow();
    });
  });

  describe('Configuration Keys Functionality', () => {
    let testConfigIds: string[] = [];

    afterEach(async () => {
      // Clean up configurations created in this test suite
      for (const configId of testConfigIds) {
        try {
          await client.configurations.delete(configId);
        } catch (error) {
          console.warn(`Failed to cleanup configuration ${configId}:`, error);
        }
      }
      testConfigIds = [];
    });

    it('should create and retrieve configuration with simple key-value pairs', async () => {
      const configName = `Simple Keys Config ${Date.now()}`;
      const simpleKeys = {
        stringKey: 'test-value',
        numberKey: 42,
        booleanKey: true,
        nullKey: null
      };

      // Create configuration with simple keys
      const createdConfig = await client.configurations.create({
        applicationId: testApplicationId,
        name: configName,
        configuration: simpleKeys,
        comment: 'Configuration with simple key-value pairs'
      });

      testConfigIds.push(createdConfig.id);

      // Verify configuration was created with correct keys
      expect(createdConfig.configuration).toEqual(simpleKeys);
      expect(createdConfig.configuration.stringKey).toBe('test-value');
      expect(createdConfig.configuration.numberKey).toBe(42);
      expect(createdConfig.configuration.booleanKey).toBe(true);
      expect(createdConfig.configuration.nullKey).toBeNull();

      // Retrieve configuration and verify keys are preserved
      const retrievedConfig = await client.configurations.getById(createdConfig.id);
      expect(retrievedConfig.configuration).toEqual(simpleKeys);
    });

    it('should support nested object configuration keys', async () => {
      const configName = `Nested Keys Config ${Date.now()}`;
      const nestedKeys = {
        database: {
          connection: {
            host: 'localhost',
            port: 5432,
            ssl: true
          },
          pool: {
            min: 2,
            max: 10
          }
        },
        api: {
          endpoints: {
            users: '/api/v1/users',
            orders: '/api/v1/orders'
          },
          timeout: 30000,
          retries: 3
        },
        features: {
          authentication: {
            enabled: true,
            providers: ['oauth', 'saml']
          },
          logging: {
            level: 'info',
            destinations: ['console', 'file']
          }
        }
      };

      // Create configuration with nested keys
      const createdConfig = await client.configurations.create({
        applicationId: testApplicationId,
        name: configName,
        configuration: nestedKeys,
        comment: 'Configuration with nested object keys'
      });

      testConfigIds.push(createdConfig.id);

      // Verify nested structure is preserved
      expect(createdConfig.configuration).toEqual(nestedKeys);
      expect((createdConfig.configuration as any).database.connection.host).toBe('localhost');
      expect((createdConfig.configuration as any).api.endpoints.users).toBe('/api/v1/users');
      expect((createdConfig.configuration as any).features.authentication.providers).toEqual(['oauth', 'saml']);

      // Retrieve and verify nested keys are intact
      const retrievedConfig = await client.configurations.getById(createdConfig.id);
      expect(retrievedConfig.configuration).toEqual(nestedKeys);
      expect((retrievedConfig.configuration as any).database.pool.max).toBe(10);
    });

    it('should support array values in configuration keys', async () => {
      const configName = `Array Keys Config ${Date.now()}`;
      const arrayKeys = {
        servers: ['server1.example.com', 'server2.example.com', 'server3.example.com'],
        ports: [8080, 8081, 8082],
        features: [
          { name: 'feature1', enabled: true },
          { name: 'feature2', enabled: false },
          { name: 'feature3', enabled: true }
        ],
        mixedArray: ['string', 123, true, null, { nested: 'object' }]
      };

      // Create configuration with array values
      const createdConfig = await client.configurations.create({
        applicationId: testApplicationId,
        name: configName,
        configuration: arrayKeys,
        comment: 'Configuration with array values'
      });

      testConfigIds.push(createdConfig.id);

      // Verify array values are preserved
      expect(createdConfig.configuration.servers).toEqual(['server1.example.com', 'server2.example.com', 'server3.example.com']);
      expect(createdConfig.configuration.ports).toEqual([8080, 8081, 8082]);
      expect((createdConfig.configuration.features as any)[0]).toEqual({ name: 'feature1', enabled: true });
      expect(createdConfig.configuration.mixedArray).toEqual(['string', 123, true, null, { nested: 'object' }]);

      // Retrieve and verify arrays are intact
      const retrievedConfig = await client.configurations.getById(createdConfig.id);
      expect(retrievedConfig.configuration).toEqual(arrayKeys);
    });

    it('should allow updating existing keys', async () => {
      const configName = `Update Keys Config ${Date.now()}`;
      const initialKeys = {
        environment: 'development',
        debug: true,
        maxConnections: 100
      };

      // Create initial configuration
      const createdConfig = await client.configurations.create({
        applicationId: testApplicationId,
        name: configName,
        configuration: initialKeys,
        comment: 'Configuration for key updates'
      });

      testConfigIds.push(createdConfig.id);

      // Update existing keys
      const updatedKeys = {
        environment: 'production',
        debug: false,
        maxConnections: 500
      };

      const updatedConfig = await client.configurations.update(createdConfig.id, {
        configuration: updatedKeys
      });

      // Verify keys were updated
      expect(updatedConfig.configuration.environment).toBe('production');
      expect(updatedConfig.configuration.debug).toBe(false);
      expect(updatedConfig.configuration.maxConnections).toBe(500);

      // Retrieve and verify updates persisted
      const retrievedConfig = await client.configurations.getById(createdConfig.id);
      expect(retrievedConfig.configuration).toEqual(updatedKeys);
    });

    it('should support adding and removing keys', async () => {
      const configName = `Add Remove Keys Config ${Date.now()}`;
      const initialKeys = {
        baseUrl: 'https://api.example.com',
        timeout: 5000
      };

      // Create initial configuration
      const createdConfig = await client.configurations.create({
        applicationId: testApplicationId,
        name: configName,
        configuration: initialKeys,
        comment: 'Configuration for adding/removing keys'
      });

      testConfigIds.push(createdConfig.id);

      // Add new keys and modify existing ones
      const expandedKeys = {
        baseUrl: 'https://api.example.com',
        timeout: 10000, // Modified existing key
        retries: 3,     // New key
        headers: {      // New nested key
          'Content-Type': 'application/json',
          'User-Agent': 'ConfigService/1.0'
        }
      };

      const updatedConfig = await client.configurations.update(createdConfig.id, {
        configuration: expandedKeys
      });

      // Verify new keys were added
      expect(updatedConfig.configuration.retries).toBe(3);
      expect(updatedConfig.configuration.headers).toEqual({
        'Content-Type': 'application/json',
        'User-Agent': 'ConfigService/1.0'
      });
      expect(updatedConfig.configuration.timeout).toBe(10000);

      // Remove some keys
      const reducedKeys = {
        baseUrl: 'https://api.example.com',
        retries: 3
        // timeout and headers removed
      };

      const finalConfig = await client.configurations.update(createdConfig.id, {
        configuration: reducedKeys
      });

      // Verify keys were removed
      expect(finalConfig.configuration).toEqual(reducedKeys);
      expect(finalConfig.configuration.timeout).toBeUndefined();
      expect(finalConfig.configuration.headers).toBeUndefined();
    });

    it('should handle special character keys', async () => {
      const configName = `Special Chars Config ${Date.now()}`;
      const specialKeys = {
        'key-with-dashes': 'dash-value',
        'key_with_underscores': 'underscore-value',
        'key.with.dots': 'dot-value',
        'key with spaces': 'space-value',
        'key@with#symbols$': 'symbol-value',
        'UPPERCASE_KEY': 'upper-value',
        'mixedCaseKey': 'mixed-value',
        '123numericKey': 'numeric-start-value'
      };

      // Create configuration with special character keys
      const createdConfig = await client.configurations.create({
        applicationId: testApplicationId,
        name: configName,
        configuration: specialKeys,
        comment: 'Configuration with special character keys'
      });

      testConfigIds.push(createdConfig.id);

      // Verify all special character keys are preserved
      expect(createdConfig.configuration['key-with-dashes']).toBe('dash-value');
      expect(createdConfig.configuration['key_with_underscores']).toBe('underscore-value');
      expect(createdConfig.configuration['key.with.dots']).toBe('dot-value');
      expect(createdConfig.configuration['key with spaces']).toBe('space-value');
      expect(createdConfig.configuration['key@with#symbols$']).toBe('symbol-value');
      expect(createdConfig.configuration['UPPERCASE_KEY']).toBe('upper-value');
      expect(createdConfig.configuration['mixedCaseKey']).toBe('mixed-value');
      expect(createdConfig.configuration['123numericKey']).toBe('numeric-start-value');

      // Retrieve and verify special keys are intact
      const retrievedConfig = await client.configurations.getById(createdConfig.id);
      expect(retrievedConfig.configuration).toEqual(specialKeys);
    });

    it('should handle deeply nested key structures', async () => {
      const configName = `Deep Nested Config ${Date.now()}`;
      const deeplyNestedKeys = {
        level1: {
          level2: {
            level3: {
              level4: {
                level5: {
                  deepValue: 'found-me',
                  deepArray: [1, 2, 3],
                  deepObject: {
                    nested: true,
                    count: 42
                  }
                }
              }
            }
          }
        },
        anotherBranch: {
          config: {
            settings: {
              advanced: {
                performance: {
                  caching: true,
                  compression: 'gzip'
                }
              }
            }
          }
        }
      };

      // Create configuration with deeply nested structure
      const createdConfig = await client.configurations.create({
        applicationId: testApplicationId,
        name: configName,
        configuration: deeplyNestedKeys,
        comment: 'Configuration with deeply nested keys'
      });

      testConfigIds.push(createdConfig.id);

      // Verify deep nesting is preserved
      expect((createdConfig.configuration as any).level1.level2.level3.level4.level5.deepValue).toBe('found-me');
      expect((createdConfig.configuration as any).level1.level2.level3.level4.level5.deepArray).toEqual([1, 2, 3]);
      expect((createdConfig.configuration as any).anotherBranch.config.settings.advanced.performance.caching).toBe(true);

      // Retrieve and verify deep structure is intact
      const retrievedConfig = await client.configurations.getById(createdConfig.id);
      expect(retrievedConfig.configuration).toEqual(deeplyNestedKeys);
    });

    it('should handle empty and edge case key values', async () => {
      const configName = `Edge Case Keys Config ${Date.now()}`;
      const edgeCaseKeys = {
        emptyString: '',
        emptyObject: {},
        emptyArray: [],
        zeroNumber: 0,
        falseBoolean: false,
        nullValue: null,
        undefinedValue: undefined, // This will be filtered out by JSON serialization
        whitespaceString: '   ',
        specialNumbers: {
          infinity: Infinity,
          negativeInfinity: -Infinity,
          notANumber: NaN
        }
      };

      // Create configuration with edge case values
      const createdConfig = await client.configurations.create({
        applicationId: testApplicationId,
        name: configName,
        configuration: edgeCaseKeys,
        comment: 'Configuration with edge case key values'
      });

      testConfigIds.push(createdConfig.id);

      // Verify edge case values are handled correctly
      expect(createdConfig.configuration.emptyString).toBe('');
      expect(createdConfig.configuration.emptyObject).toEqual({});
      expect(createdConfig.configuration.emptyArray).toEqual([]);
      expect(createdConfig.configuration.zeroNumber).toBe(0);
      expect(createdConfig.configuration.falseBoolean).toBe(false);
      expect(createdConfig.configuration.nullValue).toBeNull();
      expect(createdConfig.configuration.whitespaceString).toBe('   ');
      
      // Note: undefined values are typically removed during JSON serialization
      expect(createdConfig.configuration.undefinedValue).toBeUndefined();

      // Special numbers might be serialized as null or strings depending on JSON handling
      // We'll verify they exist but not their exact values due to JSON serialization behavior
      expect('specialNumbers' in createdConfig.configuration).toBe(true);
    });

    it('should preserve key order and structure consistency', async () => {
      const configName = `Key Order Config ${Date.now()}`;
      const orderedKeys = {
        firstKey: 'first',
        secondKey: 'second',
        thirdKey: 'third',
        nestedObject: {
          alpha: 'a',
          beta: 'b',
          gamma: 'c'
        }
      };

      // Create configuration
      const createdConfig = await client.configurations.create({
        applicationId: testApplicationId,
        name: configName,
        configuration: orderedKeys,
        comment: 'Configuration for testing key consistency'
      });

      testConfigIds.push(createdConfig.id);

      // Retrieve multiple times to ensure consistency
      const retrieval1 = await client.configurations.getById(createdConfig.id);
      const retrieval2 = await client.configurations.getById(createdConfig.id);

      // Verify structure is consistent across retrievals
      expect(retrieval1.configuration).toEqual(retrieval2.configuration);
      expect(retrieval1.configuration).toEqual(orderedKeys);

      // Verify all keys are present
      const keys1 = Object.keys(retrieval1.configuration);
      const keys2 = Object.keys(retrieval2.configuration);
      expect(keys1).toEqual(keys2);
    });
  });
});
