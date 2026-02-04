# venkatghrepo

Azure Analytics Service Integration for Application Insights

## Overview

This repository provides a TypeScript client for integrating Azure Application Insights analytics service into your applications.

## Features

- ✅ Azure Application Insights integration
- ✅ Custom event tracking
- ✅ Custom metric tracking
- ✅ Exception tracking
- ✅ Trace logging
- ✅ Page view tracking
- ✅ Auto-collection of requests, performance, exceptions, and dependencies
- ✅ TypeScript support with type definitions

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Azure Application Insights

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Add your Azure Application Insights connection string or instrumentation key:

```env
AZURE_CONNECTION_STRING=InstrumentationKey=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx;IngestionEndpoint=https://...
```

### 3. Build the Project

```bash
npm run build
```

## Usage

### Initialize the Client

```typescript
import { azureAnalytics } from './index';

// Initialize with connection string (recommended)
azureAnalytics.initialize({
  connectionString: process.env.AZURE_CONNECTION_STRING,
  enableAutoCollection: true,
  samplingPercentage: 100
});
```

### Track Custom Events

```typescript
azureAnalytics.trackEvent('UserLoggedIn', {
  userId: '12345',
  username: 'john.doe'
});
```

### Track Custom Metrics

```typescript
azureAnalytics.trackMetric('ApiResponseTime', 150, {
  endpoint: '/api/users'
});
```

### Track Exceptions

```typescript
try {
  // Your code
} catch (error) {
  azureAnalytics.trackException(error as Error, {
    component: 'UserService'
  });
}
```

### Track Trace Messages

```typescript
azureAnalytics.trackTrace('Application started', undefined, {
  version: '1.0.0'
});
```

### Track Page Views

```typescript
azureAnalytics.trackPageView('HomePage', 'https://example.com/home', {
  referrer: 'google'
});
```

### Flush Telemetry

```typescript
// Flush before application exits to ensure all telemetry is sent
azureAnalytics.flush();
```

## Configuration Options

- `connectionString`: Azure Application Insights connection string (recommended)
- `instrumentationKey`: Azure Application Insights instrumentation key (legacy)
- `enableAutoCollection`: Enable automatic collection of requests, performance, exceptions, and dependencies (default: true)
- `samplingPercentage`: Percentage of telemetry to sample (0-100, default: 100)

## Getting Your Azure Credentials

1. Go to [Azure Portal](https://portal.azure.com/)
2. Create or navigate to your Application Insights resource
3. Copy the **Connection String** from the Overview page
4. Add it to your `.env` file

## Scripts

- `npm run build` - Build the TypeScript project
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier
- `npm run clean` - Clean build artifacts

## Example

See `src/example.ts` for a complete usage example.

## License

ISC