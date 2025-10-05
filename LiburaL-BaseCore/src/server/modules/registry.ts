// server/modules/registry.ts
import { StampModule, stampCreatorModule } from "./stamp-creator";
import { aegisPgpModule } from "./aegis-pgp";

export class ModuleRegistry {
  private modules = new Map<string, StampModule>();

  constructor() {
    this.registerModule(stampCreatorModule);
    this.registerModule(aegisPgpModule);
  }

  registerModule(module: StampModule) {
    this.modules.set(module.id, module);
    console.log(`[REGISTRY] Registered module: ${module.id} (${module.name})`);
  }

  getModule(id: string): StampModule | undefined {
    return this.modules.get(id);
  }

  getAllModules(): StampModule[] {
    return Array.from(this.modules.values());
  }

  async getModuleStatus(id: string) {
    const module = this.getModule(id);
    if (!module) return null;
    return await (module as any).getInfo();
  }

  async getAllModuleStatuses() {
    const statuses = [];
    for (const [, module] of this.modules) {
      statuses.push(await (module as any).getInfo());
    }
    return statuses;
  }
}

export const moduleRegistry = new ModuleRegistry();