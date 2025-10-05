# Prompt for your AI assistant

## Simple connectivity test

```Can you ping the stdio-server-uv MCP server?```

## Tool discovery test

- ```What MCP servers and tools are available?```
- ```Show me the stdio-server-uv tools.```

## Deployment Questions

- ```What's deployed in production right now?```
- ```Show me the deployment status for web-app```
- ```Are there any failed deployments?```

## Health Monitoring

- ```Check the health of all environments```
- ```Is production healthy?```
- ```What services need attention?```

## Release Management

- ```Show me the last 5 releases for api-service```
- ```Promote version 2.1.4 of web-app from staging to production```

## Chained tool test

- ```Check the deployment status of the "web-app" application in the "prod" environment, then check the health of that environment, and finally list the last 3 releases for that application. Please show me what tools you're using and chain them together.```

## Complex workflow test

- ```I need to promote the web-app from staging to UAT. First check the current deployment status in staging to see what version is deployed, then check UAT's health to make sure it's ready, and finally promote the release.```