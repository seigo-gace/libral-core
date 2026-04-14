import { WebSocketServer, WebSocket } from 'ws';
import { Server } from 'http';
import { redisService } from './redis';

export class WebSocketService {
  private wss: WebSocketServer | null = null;
  private clients: Set<WebSocket> = new Set();

  initialize(server: Server) {
    this.wss = new WebSocketServer({ server, path: '/ws' });

    this.wss.on('connection', (ws: WebSocket, req) => {
      console.log('WebSocket client connected');
      this.clients.add(ws);

      ws.on('message', (message: Buffer) => {
        try {
          const data = JSON.parse(message.toString());
          this.handleMessage(ws, data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      });

      ws.on('close', () => {
        console.log('WebSocket client disconnected');
        this.clients.delete(ws);
      });

      ws.on('error', (error) => {
        console.error('WebSocket error:', error);
        this.clients.delete(ws);
      });

      // Send initial connection success message
      this.sendToClient(ws, {
        type: 'connection',
        status: 'connected',
        timestamp: new Date().toISOString()
      });
    });

    // Subscribe to system events for real-time updates
    this.setupEventSubscriptions();
  }

  private async setupEventSubscriptions() {
    // Subscribe to various Redis channels for real-time updates
    await redisService.subscribe('system.events', (eventData) => {
      this.broadcast({
        type: 'system_event',
        data: eventData
      });
    });

    await redisService.subscribe('metrics.update', (metricsData) => {
      this.broadcast({
        type: 'metrics_update',
        data: metricsData
      });
    });

    await redisService.subscribe('module.status', (statusData) => {
      this.broadcast({
        type: 'module_status',
        data: statusData
      });
    });
  }

  private handleMessage(ws: WebSocket, data: any) {
    switch (data.type) {
      case 'ping':
        this.sendToClient(ws, { type: 'pong', timestamp: new Date().toISOString() });
        break;
      case 'subscribe':
        // Handle subscription requests for specific data types
        this.sendToClient(ws, { type: 'subscribed', channel: data.channel });
        break;
      default:
        console.log('Unknown WebSocket message type:', data.type);
    }
  }

  private sendToClient(ws: WebSocket, data: any) {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data));
    }
  }

  broadcast(data: any) {
    const message = JSON.stringify(data);
    this.clients.forEach(client => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message);
      }
    });
  }

  // Broadcast system metrics updates
  broadcastMetrics(metrics: any) {
    this.broadcast({
      type: 'metrics_update',
      data: metrics,
      timestamp: new Date().toISOString()
    });
  }

  // Broadcast module status updates
  broadcastModuleStatus(moduleId: string, status: string) {
    this.broadcast({
      type: 'module_status',
      data: { moduleId, status },
      timestamp: new Date().toISOString()
    });
  }

  // Broadcast new events
  broadcastEvent(event: any) {
    this.broadcast({
      type: 'new_event',
      data: event,
      timestamp: new Date().toISOString()
    });
  }
}

export const websocketService = new WebSocketService();
