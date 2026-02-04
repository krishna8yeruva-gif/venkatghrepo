import * as appInsights from 'applicationinsights';

/**
 * Configuration options for Azure Analytics
 */
export interface AzureAnalyticsConfig {
  connectionString?: string;
  instrumentationKey?: string;
  enableAutoCollection?: boolean;
  samplingPercentage?: number;
}

/**
 * Azure Analytics Client wrapper for Application Insights
 */
export class AzureAnalyticsClient {
  private client: appInsights.TelemetryClient | null = null;
  private isInitialized = false;

  /**
   * Initialize the Azure Analytics client
   * @param config Configuration options
   */
  public initialize(config: AzureAnalyticsConfig): void {
    if (this.isInitialized) {
      console.warn('Azure Analytics client is already initialized');
      return;
    }

    if (!config.connectionString && !config.instrumentationKey) {
      throw new Error('Either connectionString or instrumentationKey must be provided');
    }

    try {
      if (config.connectionString) {
        appInsights.setup(config.connectionString);
      } else if (config.instrumentationKey) {
        appInsights.setup(config.instrumentationKey);
      }

      // Configure auto-collection
      if (config.enableAutoCollection !== false) {
        const configuration = appInsights.Configuration;
        configuration
          .setAutoCollectRequests(true)
          .setAutoCollectPerformance(true, true)
          .setAutoCollectExceptions(true)
          .setAutoCollectDependencies(true)
          .setAutoCollectConsole(true);
      }

      appInsights.start();
      this.client = appInsights.defaultClient;

      // Set sampling percentage after start
      if (config.samplingPercentage !== undefined) {
        this.client.config.samplingPercentage = config.samplingPercentage;
      }

      this.isInitialized = true;

      console.log('Azure Analytics client initialized successfully');
    } catch (error) {
      console.error('Failed to initialize Azure Analytics client:', error);
      throw error;
    }
  }

  /**
   * Track a custom event
   * @param name Event name
   * @param properties Custom properties
   */
  public trackEvent(name: string, properties?: { [key: string]: string }): void {
    if (!this.ensureInitialized()) return;
    this.client?.trackEvent({ name, properties });
  }

  /**
   * Track a custom metric
   * @param name Metric name
   * @param value Metric value
   * @param properties Custom properties
   */
  public trackMetric(name: string, value: number, properties?: { [key: string]: string }): void {
    if (!this.ensureInitialized()) return;
    this.client?.trackMetric({ name, value, properties });
  }

  /**
   * Track an exception
   * @param exception Exception to track
   * @param properties Custom properties
   */
  public trackException(exception: Error, properties?: { [key: string]: string }): void {
    if (!this.ensureInitialized()) return;
    this.client?.trackException({ exception, properties });
  }

  /**
   * Track a trace message
   * @param message Trace message
   * @param severity Severity level
   * @param properties Custom properties
   */
  public trackTrace(
    message: string,
    severity?: appInsights.Contracts.SeverityLevel,
    properties?: { [key: string]: string }
  ): void {
    if (!this.ensureInitialized()) return;
    this.client?.trackTrace({ message, severity, properties });
  }

  /**
   * Track a page view
   * @param name Page name
   * @param url Page URL
   * @param properties Custom properties
   */
  public trackPageView(name: string, url?: string, properties?: { [key: string]: string }): void {
    if (!this.ensureInitialized()) return;
    this.client?.trackPageView({ name, url, properties });
  }

  /**
   * Flush all pending telemetry
   */
  public flush(): void {
    if (!this.ensureInitialized()) return;
    this.client?.flush();
  }

  /**
   * Check if client is initialized
   */
  private ensureInitialized(): boolean {
    if (!this.isInitialized || !this.client) {
      console.error('Azure Analytics client is not initialized. Call initialize() first.');
      return false;
    }
    return true;
  }

  /**
   * Get the underlying Application Insights client
   */
  public getClient(): appInsights.TelemetryClient | null {
    return this.client;
  }
}

// Export singleton instance
export const azureAnalytics = new AzureAnalyticsClient();
