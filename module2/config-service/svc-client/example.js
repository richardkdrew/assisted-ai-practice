/**
 * Example usage of the Configuration Service Client Library
 * 
 * This example demonstrates how to use the client library to:
 * 1. Create an application
 * 2. Create configurations
 * 3. Retrieve configuration data
 * 4. Update configurations
 * 5. Handle errors
 */

// Import the client (in a real project, you would install via npm)
const { ConfigServiceClient } = require('./dist/index.js');

async function example() {
  // Create a client instance
  const client = new ConfigServiceClient({
    baseUrl: 'http://localhost:8000',
    timeout: 10000
  });

  try {
    console.log('🚀 Configuration Service Client Example\n');

    // Test health check
    console.log('1. Testing connection...');
    const health = await client.healthCheck();
    console.log(`   Status: ${health.status}`);
    if (health.error) {
      console.log(`   Note: ${health.error} (This is expected if the service isn't running)`);
    }
    console.log();

    // Example of how the client would be used when the service is running:
    console.log('2. Example usage (when service is running):');
    console.log(`
    // Create an application
    const app = await client.applications.create({
      name: 'my-web-app',
      description: 'My web application'
    });
    console.log('Created application:', app.name);

    // Create a database configuration
    const dbConfig = await client.configurations.create({
      applicationId: app.id,
      name: 'database',
      configuration: {
        host: 'localhost',
        port: 5432,
        database: 'myapp',
        username: 'user',
        password: 'password'
      },
      comment: 'Database configuration for production'
    });
    console.log('Created configuration:', dbConfig.name);

    // Get configuration data by name
    const configData = await client.getConfigByName('my-web-app', 'database');
    console.log('Database host:', configData.host);

    // Update configuration
    const updatedConfig = await client.configurations.update(dbConfig.id, {
      configuration: {
        ...dbConfig.configuration,
        pool: { min: 2, max: 10 }
      }
    });
    console.log('Updated configuration with connection pool settings');

    // List all applications
    const apps = await client.applications.list({ limit: 10 });
    console.log('Total applications:', apps.total);

    // Clean up - delete application and all its configurations
    await client.deleteApplicationWithConfigurations(app.id);
    console.log('Cleaned up application and configurations');
    `);

    console.log('3. Client library features:');
    console.log('   ✅ Type-safe TypeScript API');
    console.log('   ✅ Comprehensive error handling');
    console.log('   ✅ Automatic request/response transformation');
    console.log('   ✅ Built-in validation');
    console.log('   ✅ Convenient helper methods');
    console.log('   ✅ Configurable HTTP client');
    console.log('   ✅ Full CRUD operations for applications and configurations');
    console.log();

    console.log('4. Error handling example:');
    try {
      // This will fail because the service isn't running
      await client.applications.getById('01ARZ3NDEKTSV4RRFFQ69G5FAV');
    } catch (error) {
      console.log(`   Caught error: ${error.constructor.name}`);
      console.log(`   Message: ${error.message}`);
      if (error.code) {
        console.log(`   Code: ${error.code}`);
      }
    }

    console.log('\n✨ Configuration Service Client Library is ready to use!');
    console.log('\nTo use in your project:');
    console.log('1. Install: npm install @config-service/client');
    console.log('2. Import: import { ConfigServiceClient } from "@config-service/client";');
    console.log('3. Create client: const client = new ConfigServiceClient({ baseUrl: "http://localhost:8000" });');
    console.log('4. Start using the API methods!');

  } catch (error) {
    console.error('Example error:', error.message);
  }
}

// Run the example
example().catch(console.error);
