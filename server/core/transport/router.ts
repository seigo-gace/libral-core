// server/core/transport/router.ts
import { TransportAdapter, SendInput, SendResult } from "./adapter";
import { RoutingConfig, decidePriority } from "./policy";

export class TransportRouter {
  constructor(
    private adapters: TransportAdapter[],
    private cfg: RoutingConfig,
    private emitAudit: (evt: any) => void
  ) {}

  private pick(name: string) { return this.adapters.find(a => a.name() === name); }

  async sendWithFailover(input: SendInput): Promise<SendResult> {
    const order = decidePriority(this.cfg, input.metadata);

    for (const name of order) {
      const a = this.pick(name);
      if (!a) continue;
      if (!(await a.health())) continue;

      const res = await a.send(input);

      this.emitAudit({
        type: "send_attempt",
        transport: name,
        ok: res.ok,
        tenant_id: input.metadata.tenant_id,
        usecase: input.metadata.usecase,
        idempotency_key: input.metadata.idempotency_key,
        error: res.error || null,
        ts: Date.now(),
      });

      if (res.ok) return { ...res, transport: name };
    }

    this.emitAudit({ type: "send_queued", idempotency_key: input.metadata.idempotency_key, ts: Date.now() });
    return { ok: false, error: "QUEUED_FOR_RETRY" };
  }
}