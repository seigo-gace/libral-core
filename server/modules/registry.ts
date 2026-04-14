// server/modules/registry.ts
// 登録モジュールは docs/modules.yaml と docs/MODULE_REGISTRY.md に一覧化すること。
import { StampModule, stampCreatorModule } from "./stamp-creator";
import { aegisPgpModule } from "./aegis-pgp";

export class ModuleRegistry {
  private modules = new Map<string, StampModule>();

  constructor() {
    this.registerModule(stampCreatorModule);
    this.registerModule(aegisPgpModule);
  }

  /** 新規モジュール追加時は docs/modules.yaml の layer-registered-modules も更新する */
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

  async startModule(id: string): Promise<boolean> {
    const module = this.getModule(id);
    if (!module) return false;
    (module as { status?: string }).status = "active";
    return true;
  }

  async restartModule(id: string): Promise<boolean> {
    const module = this.getModule(id);
    if (!module) return false;
    (module as { status?: string }).status = "active";
    return true;
  }
}

export const moduleRegistry = new ModuleRegistry();