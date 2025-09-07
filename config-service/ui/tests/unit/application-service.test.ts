import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ApplicationService } from '../../src/services/application-service.js';
import { ApiService } from '../../src/services/api-service.js';

// Mock the API service
vi.mock('../../src/services/api-service.js', () => ({
  ApiService: vi.fn().mockImplementation(() => ({
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  })),
  apiService: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  }
}));

describe('ApplicationService', () => {
  let applicationService: ApplicationService;
  let mockApiService: any;

  beforeEach(() => {
    applicationService = new ApplicationService();
    mockApiService = vi.mocked(require('../../src/services/api-service.js').apiService);
    vi.clearAllMocks();
  });

  describe('getAll', () => {
    it('should call API service with correct parameters', async () => {
      const mockResponse = {
        data: [
          {
            id: '01HKQM5Z8X9Y2W3V4U5T6S7R8Q',
            name: 'Test App',
            comments: 'Test comments',
            configuration_ids: ['01HKQM5Z8X9Y2W3V4U5T6S7R8R'],
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z'
          }
        ],
        status: 200
      };

      mockApiService.get.mockResolvedValue(mockResponse);

      const result = await applicationService.getAll(10, 0);

      expect(mockApiService.get).toHaveBeenCalledWith('/applications', { limit: 10, offset: 0 });
      expect(result).toEqual(mockResponse);
    });

    it('should handle API errors', async () => {
      const mockError = {
        error: 'Internal server error',
        status: 500
      };

      mockApiService.get.mockResolvedValue(mockError);

      const result = await applicationService.getAll();

      expect(result).toEqual(mockError);
    });
  });

  describe('getById', () => {
    it('should call API service with correct ID', async () => {
      const testId = '01HKQM5Z8X9Y2W3V4U5T6S7R8Q';
      const mockResponse = {
        data: {
          id: testId,
          name: 'Test App',
          comments: 'Test comments',
          configuration_ids: [],
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        },
        status: 200
      };

      mockApiService.get.mockResolvedValue(mockResponse);

      const result = await applicationService.getById(testId);

      expect(mockApiService.get).toHaveBeenCalledWith(`/applications/${testId}`);
      expect(result).toEqual(mockResponse);
    });
  });

  describe('create', () => {
    it('should call API service with correct data', async () => {
      const createData = {
        name: 'New App',
        comments: 'New app comments'
      };

      const mockResponse = {
        data: {
          id: '01HKQM5Z8X9Y2W3V4U5T6S7R8Q',
          ...createData,
          configuration_ids: [],
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        },
        status: 201
      };

      mockApiService.post.mockResolvedValue(mockResponse);

      const result = await applicationService.create(createData);

      expect(mockApiService.post).toHaveBeenCalledWith('/applications', createData);
      expect(result).toEqual(mockResponse);
    });
  });

  describe('update', () => {
    it('should call API service with correct ID and data', async () => {
      const testId = '01HKQM5Z8X9Y2W3V4U5T6S7R8Q';
      const updateData = {
        name: 'Updated App',
        comments: 'Updated comments'
      };

      const mockResponse = {
        data: {
          id: testId,
          ...updateData,
          configuration_ids: [],
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        },
        status: 200
      };

      mockApiService.put.mockResolvedValue(mockResponse);

      const result = await applicationService.update(testId, updateData);

      expect(mockApiService.put).toHaveBeenCalledWith(`/applications/${testId}`, updateData);
      expect(result).toEqual(mockResponse);
    });
  });

  describe('delete', () => {
    it('should call API service with correct ID', async () => {
      const testId = '01HKQM5Z8X9Y2W3V4U5T6S7R8Q';
      const mockResponse = {
        status: 204
      };

      mockApiService.delete.mockResolvedValue(mockResponse);

      const result = await applicationService.delete(testId);

      expect(mockApiService.delete).toHaveBeenCalledWith(`/applications/${testId}`);
      expect(result).toEqual(mockResponse);
    });
  });

  describe('transformToListItem', () => {
    it('should transform application response to list item', () => {
      const applicationResponse = {
        id: '01HKQM5Z8X9Y2W3V4U5T6S7R8Q',
        name: 'Test App',
        comments: 'Test comments',
        configuration_ids: ['01HKQM5Z8X9Y2W3V4U5T6S7R8R', '01HKQM5Z8X9Y2W3V4U5T6S7R8S'],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      };

      const result = applicationService.transformToListItem(applicationResponse);

      expect(result).toEqual({
        id: '01HKQM5Z8X9Y2W3V4U5T6S7R8Q',
        name: 'Test App',
        comments: 'Test comments',
        configurationCount: 2,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      });
    });

    it('should handle missing comments', () => {
      const applicationResponse = {
        id: '01HKQM5Z8X9Y2W3V4U5T6S7R8Q',
        name: 'Test App',
        configuration_ids: [],
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z'
      };

      const result = applicationService.transformToListItem(applicationResponse);

      expect(result.comments).toBeUndefined();
      expect(result.configurationCount).toBe(0);
    });
  });

  describe('transformToListItems', () => {
    it('should transform array of application responses', () => {
      const applications = [
        {
          id: '01HKQM5Z8X9Y2W3V4U5T6S7R8Q',
          name: 'App 1',
          comments: 'Comments 1',
          configuration_ids: ['01HKQM5Z8X9Y2W3V4U5T6S7R8R'],
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        },
        {
          id: '01HKQM5Z8X9Y2W3V4U5T6S7R8S',
          name: 'App 2',
          configuration_ids: [],
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      ];

      const result = applicationService.transformToListItems(applications);

      expect(result).toHaveLength(2);
      expect(result[0].configurationCount).toBe(1);
      expect(result[1].configurationCount).toBe(0);
    });
  });
});
