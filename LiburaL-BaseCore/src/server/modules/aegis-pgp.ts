// server/modules/aegis-pgp.ts
import { StampModule } from "./stamp-creator";

export interface AegisPgpModule extends StampModule {
  policies: string[];
  transports: string[];
}

export class AegisPgpCoreModule implements AegisPgpModule {
  public readonly id = "aegis-pgp";
  public readonly name = "Aegis-PGP暗号化システム";
  public readonly version = "v1.0.0";
  public status: 'active' | 'inactive' | 'maintenance' = 'active';
  public readonly endpoints = [
    "/v1/encrypt",
    "/v1/decrypt",
    "/v1/sign",
    "/v1/verify",
    "/v1/send",
    "/v1/wkd-path",
    "/v1/inspect"
  ];
  public readonly capabilities = [
    "modern-pgp-encryption",
    "context-lock-signatures",
    "wkd-support",
    "multi-transport-failover",
    "seipd-v2-ocb",
    "openpgp-v6-keys"
  ];
  public readonly policies = ["modern-strong", "compat", "backup-longterm"];
  public readonly transports = ["telegram", "email", "webhook"];

  constructor() {
    this.initialize();
  }

  private async initialize() {
    console.log(`[${this.id}] Initializing ${this.name} ${this.version}`);
    
    // Check if Aegis-PGP Core service is available
    try {
      const healthUrl = process.env.AEGIS_URL || "http://localhost:8787";
      const response = await fetch(`${healthUrl}/v1/health`);
      if (response.ok) {
        console.log(`[${this.id}] Connected to Aegis-PGP Core API`);
      } else {
        console.log(`[${this.id}] Aegis-PGP Core API not available, using mock mode`);
      }
    } catch (error) {
      console.log(`[${this.id}] Aegis-PGP Core API not available, using mock mode`);
    }
    
    this.status = 'active';
  }

  async health(): Promise<boolean> {
    return this.status === 'active';
  }

  async getInfo() {
    return {
      id: this.id,
      name: this.name,
      version: this.version,
      status: this.status,
      endpoints: this.endpoints,
      capabilities: this.capabilities,
      policies: this.policies,
      transports: this.transports,
      uptime: process.uptime(),
      lastCheck: new Date().toISOString(),
      mode: process.env.NODE_ENV === 'development' ? 'mock' : 'production'
    };
  }
}

// Aegis-PGP モジュールのシングルトンインスタンス
export const aegisPgpModule = new AegisPgpCoreModule();