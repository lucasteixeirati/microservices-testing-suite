const request = require('supertest');
const { app, isAllowedURL, isValidUserId } = require('./app');

global.fetch = jest.fn();

describe('Order Service', () => {
  beforeEach(() => fetch.mockReset());

  test('reports its health', async () => {
    const response = await request(app).get('/health');
    expect(response.status).toBe(200);
    expect(response.body).toEqual({ status: 'healthy', service: 'order-service' });
  });

  test('rejects a browser write without a CSRF token', async () => {
    const response = await request(app)
      .post('/orders')
      .set('Origin', 'http://localhost:3000')
      .send({ user_id: 'abc-123', items: [], total_amount: 10 });
    expect(response.status).toBe(403);
    expect(response.body.error).toBe('Invalid CSRF token');
  });

  test('creates an order with a valid browser CSRF token', async () => {
    fetch.mockResolvedValueOnce({ status: 200 });
    const agent = request.agent(app);
    const tokenResponse = await agent
      .get('/csrf-token')
      .set('Origin', 'http://localhost:3000');

    const response = await agent
      .post('/orders')
      .set('Origin', 'http://localhost:3000')
      .set('X-CSRF-Token', tokenResponse.body.csrfToken)
      .send({ user_id: 'abc-123', items: [{ sku: 'A', quantity: 1 }], total_amount: 10 });

    expect(response.status).toBe(201);
    expect(response.body.user_id).toBe('abc-123');
    expect(response.body.status).toBe('pending');
  });

  test('validates identifiers and upstream URLs', () => {
    expect(isValidUserId('550e8400-e29b-41d4-a716-446655440000')).toBe(true);
    expect(isValidUserId('../etc/passwd')).toBe(false);
    const configuredUserURL = new URL(
      '/users/123',
      process.env.USER_SERVICE_URL || 'http://localhost:8001'
    ).toString();
    expect(isAllowedURL(configuredUserURL)).toBe(true);
    expect(isAllowedURL('http://evil.example/users/123')).toBe(false);
    expect(isAllowedURL('https://localhost:8001/users/123')).toBe(false);
    expect(isAllowedURL('not a url')).toBe(false);
  });

  test('rejects invalid user IDs before calling the upstream service', async () => {
    const response = await request(app)
      .post('/orders')
      .send({ user_id: '../etc/passwd', items: [], total_amount: 10 });
    expect(response.status).toBe(400);
    expect(fetch).not.toHaveBeenCalled();
  });

  test('reports unavailable upstream services', async () => {
    const errorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    fetch.mockRejectedValueOnce(new Error('connection refused'));
    const response = await request(app)
      .post('/orders')
      .send({ user_id: 'dead-beef', items: [], total_amount: 10 });
    expect(response.status).toBe(503);
    expect(errorSpy).toHaveBeenCalled();
    errorSpy.mockRestore();
  });

  test('handles missing users and orders', async () => {
    fetch.mockResolvedValueOnce({ status: 404 });
    const createResponse = await request(app)
      .post('/orders')
      .send({ user_id: 'feed-face', items: [], total_amount: 10 });
    const getResponse = await request(app).get('/orders/unknown-order');
    expect(createResponse.status).toBe(400);
    expect(getResponse.status).toBe(404);
  });

  test('reads, lists and updates a created order', async () => {
    fetch.mockResolvedValueOnce({ status: 200 });
    const created = await request(app)
      .post('/orders')
      .send({ user_id: 'cafe-babe', items: [{ sku: 'B', quantity: 2 }], total_amount: 25 });
    const id = created.body.id;

    const read = await request(app).get(`/orders/${id}`);
    const listed = await request(app).get('/orders');
    const updated = await request(app)
      .patch(`/orders/${id}/status`)
      .send({ status: 'paid' });

    expect(read.status).toBe(200);
    expect(listed.body.some((order) => order.id === id)).toBe(true);
    expect(updated.body.status).toBe('paid');
  });
});
