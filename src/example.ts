import { azureAnalytics } from './index.js';

/**
 * Example usage of Azure Analytics integration
 */

// Initialize with connection string (recommended)
azureAnalytics.initialize({
  connectionString: process.env.AZURE_CONNECTION_STRING,
  enableAutoCollection: true,
  samplingPercentage: 100
});

// OR initialize with instrumentation key (legacy)
// azureAnalytics.initialize({
//   instrumentationKey: process.env.AZURE_INSTRUMENTATION_KEY,
//   enableAutoCollection: true,
//   samplingPercentage: 100
// });

// Track custom events
azureAnalytics.trackEvent('UserLoggedIn', {
  userId: '12345',
  username: 'john.doe'
});

// Track custom metrics
azureAnalytics.trackMetric('ApiResponseTime', 150, {
  endpoint: '/api/users'
});

// Track exceptions
try {
  throw new Error('Something went wrong');
} catch (error) {
  azureAnalytics.trackException(error as Error, {
    component: 'UserService'
  });
}

// Track trace messages
azureAnalytics.trackTrace('Application started', undefined, {
  version: '1.0.0'
});

// Track page views
azureAnalytics.trackPageView('HomePage', 'https://example.com/home', {
  referrer: 'google'
});

// Flush telemetry before application exits
azureAnalytics.flush();
