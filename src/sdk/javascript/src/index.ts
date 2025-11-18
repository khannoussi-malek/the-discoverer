/**
 * The Discoverer JavaScript/TypeScript SDK
 * 
 * A client library for interacting with The Discoverer API
 */

import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

export interface DiscovererConfig {
    baseURL?: string;
    apiKey?: string;
    timeout?: number;
}

export interface DatabaseConfig {
    id: string;
    type: string;
    name?: string;
    host: string;
    port: number;
    database: string;
    user?: string;
    password?: string;
    metadata?: Record<string, any>;
}

export interface QueryRequest {
    query: string;
    database_ids?: string[];
    page?: number;
    page_size?: number;
}

export interface QueryResponse {
    query_id: string;
    results: any[];
    total_rows: number;
    execution_time: number;
    databases_queried: string[];
    page?: number;
    page_size?: number;
    total_pages?: number;
}

export interface VisualizationRequest {
    query_id: string;
    chart_type?: string;
    x_axis?: string;
    y_axis?: string;
    z_axis?: string;
    title?: string;
    config?: Record<string, any>;
}

export interface ShareResponse {
    share_id: string;
    share_token: string;
    share_url: string;
    expires_at: string | null;
    max_accesses: number | null;
    created_at: string;
}

export interface SharedResultResponse {
    query_id: string;
    share_id: string;
    result: any;
    created_at: string;
    access_count: number;
}

export interface SharesListResponse {
    shares: Array<{
        share_id: string;
        query_id: string;
        share_token: string;
        expires_at: string | null;
        access_count: number;
        max_accesses: number | null;
        is_active: boolean;
        created_at: string;
    }>;
    total: number;
}

export class DiscovererClient {
    private client: AxiosInstance;
    private config: DiscovererConfig;

    constructor(config: DiscovererConfig = {}) {
        this.config = {
            baseURL: config.baseURL || 'http://localhost:8000',
            apiKey: config.apiKey,
            timeout: config.timeout || 30000,
        };

        this.client = axios.create({
            baseURL: this.config.baseURL,
            timeout: this.config.timeout,
            headers: this.config.apiKey
                ? { 'X-API-Key': this.config.apiKey }
                : {},
        });
    }

    // Discovery methods
    async registerDatabase(config: DatabaseConfig): Promise<any> {
        const response = await this.client.post('/api/discovery/databases', config);
        return response.data;
    }

    async listDatabases(): Promise<any[]> {
        const response = await this.client.get('/api/discovery/databases');
        return response.data;
    }

    async getDatabase(databaseId: string): Promise<any> {
        const response = await this.client.get(`/api/discovery/databases/${databaseId}`);
        return response.data;
    }

    async syncDatabase(databaseId: string): Promise<any> {
        const response = await this.client.post(`/api/discovery/databases/${databaseId}/sync`);
        return response.data;
    }

    // Query methods
    async executeQuery(
        request: QueryRequest
    ): Promise<QueryResponse> {
        const params: any = {};
        if (request.page) params.page = request.page;
        if (request.page_size) params.page_size = request.page_size;

        const response = await this.client.post(
            '/api/query/execute',
            {
                query: request.query,
                database_ids: request.database_ids,
            },
            { params }
        );
        return response.data;
    }

    async analyzeQuery(query: string): Promise<any> {
        const response = await this.client.post('/api/query/analyze', { query });
        return response.data;
    }

    // Visualization methods
    async generateChart(request: VisualizationRequest): Promise<any> {
        const response = await this.client.post('/api/visualization/generate', request);
        return response.data;
    }

    async exportChart(
        queryId: string,
        format: 'png' | 'pdf' | 'html' | 'svg' = 'png',
        width?: number,
        height?: number
    ): Promise<Blob> {
        const params: any = { format };
        if (width) params.width = width;
        if (height) params.height = height;

        const response = await this.client.get(
            `/api/visualization/export/${queryId}`,
            {
                params,
                responseType: 'blob',
            }
        );
        return response.data;
    }

    // Template methods
    async createTemplate(
        name: string,
        query: string,
        databaseIds?: string[],
        description?: string,
        tags?: string[]
    ): Promise<any> {
        const response = await this.client.post('/api/templates', {
            name,
            user_query: query,
            database_ids: databaseIds,
            description,
            tags,
        });
        return response.data;
    }

    async listTemplates(
        page: number = 1,
        pageSize: number = 20,
        tags?: string[]
    ): Promise<any> {
        const params: any = { page, page_size: pageSize };
        if (tags) params.tags = tags.join(',');

        const response = await this.client.get('/api/templates', { params });
        return response.data;
    }

    async executeTemplate(
        templateId: string,
        parameters?: Record<string, any>
    ): Promise<any> {
        const response = await this.client.post(
            `/api/templates/${templateId}/execute`,
            { template_id: templateId, parameters }
        );
        return response.data;
    }

    // Export methods
    async exportQuery(
        queryId: string,
        format: 'csv' | 'json' | 'excel' = 'csv'
    ): Promise<Blob> {
        const response = await this.client.get(`/api/export/query/${queryId}`, {
            params: { format },
            responseType: 'blob',
        });
        return response.data;
    }

    // Health methods
    async healthCheck(): Promise<any> {
        const response = await this.client.get('/health');
        return response.data;
    }

    // Analytics methods
    async getAnalytics(days: number = 7): Promise<any> {
        const response = await this.client.get('/api/analytics/stats', {
            params: { days },
        });
        return response.data;
    }

    async getTopQueries(limit: number = 10, days: number = 7): Promise<any> {
        const response = await this.client.get('/api/analytics/top-queries', {
            params: { limit, days },
        });
        return response.data;
    }

    // Comparison methods
    async compareQueries(query1Id: string, query2Id: string): Promise<any> {
        const response = await this.client.get('/api/comparison/compare', {
            params: { query1_id: query1Id, query2_id: query2Id },
        });
        return response.data;
    }

    /**
     * Create a shareable link for a query result
     */
    async createShare(options: {
        query_id: string;
        expires_in_hours?: number;
        max_accesses?: number;
        allowed_emails?: string[];
        password?: string;
    }): Promise<ShareResponse> {
        const response = await this.client.post('/api/sharing', options);
        return response.data;
    }

    /**
     * Get shared query result by token
     */
    async getSharedResult(
        shareToken: string,
        password?: string
    ): Promise<SharedResultResponse> {
        const params = password ? { password } : {};
        const response = await this.client.get(
            `/api/sharing/${shareToken}`,
            { params }
        );
        return response.data;
    }

    /**
     * List shared results
     */
    async listShares(queryId?: string): Promise<SharesListResponse> {
        const params = queryId ? { query_id: queryId } : {};
        const response = await this.client.get('/api/sharing', { params });
        return response.data;
    }

    /**
     * Revoke a shared result
     */
    async revokeShare(shareId: string): Promise<{ message: string }> {
        const response = await this.client.post(`/api/sharing/${shareId}/revoke`);
        return response.data;
    }

    /**
     * Delete a shared result
     */
    async deleteShare(shareId: string): Promise<{ message: string }> {
        const response = await this.client.delete(`/api/sharing/${shareId}`);
        return response.data;
    }
}

// Default export
export default DiscovererClient;

