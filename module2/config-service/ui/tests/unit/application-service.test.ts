import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ApplicationService } from '../../src/services/application-service';

// Mock the ConfigServiceClient
vi.mock('@config-service/client', () => ({
  ConfigServiceClient: vi.fn().mockImplementation(() => ({
    applications: {
      list: vi.fn(),
      getById: vi.fn(),
      create: vi.fn(),
      update: vi.fn(),
      delete: vi.fn(),
    }
  }))
}));

describe('ApplicationService', () => {
  let applicationService: ApplicationService;
  let mockClient: any;

  beforeEach(() => {
    applicationService = new ApplicationService();
    // Get the mock client instance
    mockClient = (applicationService as any).client;
    vi.clearAllMocks();
  });

  describe('getAll', () => {
    it('should call client with correct parameters and transform response', async () => {
      const mockClientResponse = {
        applications: [
          {
            id: '01HKQM5Z8X9Y2W3V4U5T6S7R8Q',
            name: 'Test App',
            description: 'Test description',
            createdAt: new Date('2024-01-01T00:00:00Z'),
            updatedAt: new Date('2024-01-01T00:00:00Z')
          }
        ]
      };

      mockClient.applications.list.mockResolvedValue(mockClientResponse);

      const result = await applicationService.getAll(10, 0);

      expect(mockClient.applications.list).toHaveBeenCalledWith({ limit: 10, offset: 0 });
      expect(result.status).toBe(200);
      expect(result.data).toHaveLength(1);
      expect(result.data![0]).toEqual({
        id: '01HKQM5Z8X9Y2W3V4U5T6S7R8Q',
        name: 'Test App',
        comments: 'Test description',
        configuration_ids: [],
        created_at: '2024-01-01T00:00:00.000Z',
        updated_at: '2024-01-01T00:00:00.000Z'
      });
    });

    it('should handle client errors', async () => {
      const mockError = new Error('Client error');
      mockClient.applications.list.mockRejectedValue(mockError);

      const result = await applicationService.getAll();

      expect(result.status).toBe(500);
      expect(result.error).toBe('Client error');
    });
  });

  describe('getById', () => {
    it('should call client with correct ID and transform response', async () => {
      const testId = '01HKQM5Z8X9Y2W3V4U5T6S7R8Q';
      const mockClientResponse = {
        id: testId,
        name: 'Test App',
        description: 'Test description',
        createdAt: new Date('2024-01-01T00:00:00Z'),
        updatedAt: new Date('2024-01-01T00:00:00Z')
      };

      mockClient.applications.getById.mockResolvedValue(mockClientResponse);

      const result = await applicationService.getById(testId);

      expect(mockClient.applications.getById).toHaveBeenCalledWith(testId);
      expect(result.status).toBe(200);
      expect(result.data).toEqual({
        id: testId,
        name: 'Test App',
        comments: 'Test description',
        configuration_ids: [],
        created_at: '2024-01-01T00:00:00.000Z',
        updated_at: '2024-01-01T00:00:00.000Z'
      });
    });

    it('should handle not found errors', async () => {
      const mockError = new Error('Application not found');
      mockClient.applications.getById.mockRejectedValue(mockError);

      const result = await applicationService.getById('invalid-id');

      expect(result.status).toBe(404);
      expect(result.error).toBe('Application not found');
    });
  });

  describe('create', () => {
    it('should call client with transformed data', async () => {
      const createData = {
        name: 'New App',
        comments: 'New app description'
      };

      const mockClientResponse = {
        id: '01HKQM5Z8X9Y2W3V4U5T6S7R8Q',
        name: 'New App',
        description: 'New app description',
        createdAt: new Date('2024-01-01T00:00:00Z'),
        updatedAt: new Date('2024-01-01T00:00:00Z')
      };

      mockClient.applications.create.mockResolvedValue(mockClientResponse);

      const result = await applicationService.create(createData);

      expect(mockClient.applications.create).toHaveBeenCalledWith({
        name: 'New App',
        description: 'New app description'
      });
      expect(result.status).toBe(201);
      expect(result.data?.name).toBe('New App');
    });
  });

  describe('update', () => {
    it('should call client with correct ID and transformed data', async () => {
      const testId = '01HKQM5Z8X9Y2W3V4U5T6S7R8Q';
      const updateData = {
        name: 'Updated App',
        comments: 'Updated description'
      };

      const mockClientResponse = {
        id: testId,
        name: 'Updated App',
        description: 'Updated description',
        createdAt: new Date('2024-01-01T00:00:00Z'),
        updatedAt: new Date('2024-01-01T00:00:00Z')
      };

      mockClient.applications.update.mockResolvedValue(mockClientResponse);

      const result = await applicationService.update(testId, updateData);

      expect(mockClient.applications.update).toHaveBeenCalledWith(testId, {
        name: 'Updated App',
        description: 'Updated description'
      });
      expect(result.status).toBe(200);
      expect(result.data?.name).toBe('Updated App');
    });
  });

  describe('delete', () => {
    it('should call client with correct ID', async () => {
      const testId = '01HKQM5Z8X9Y2W3V4U5T6S7R8Q';

      mockClient.applications.delete.mockResolvedValue(undefined);

      const result = await applicationService.delete(testId);

      expect(mockClient.applications.delete).toHaveBeenCalledWith(testId);
      expect(result.status).toBe(204);
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
