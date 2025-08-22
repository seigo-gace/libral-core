// server/core/transport/bootstrap.ts
import { TransportRouter } from "./router";
import { loadRoutingConfig } from "./policy";
import { TelegramAdapter } from "../../adapters/telegram";
import { EmailAdapter }    from "../../adapters/email";
import { WebhookAdapter }  from "../../adapters/webhook";

let _router: TransportRouter | null = null;

// 既存のイベント基盤へ合わせて監査イベントを流す
const emitAudit = (evt: any) => {
  // 例）Redis PubSub / WebSocket / DB保存など
  // 既存の events サービスがあるならそこへ publish してください
  // ここではダミー（本番は差し替え）
  console.log(`[AUDIT] ${JSON.stringify(evt)}`);
};

export function getTransportRouter(): TransportRouter {
  if (!_router) throw new Error("TransportRouter not initialized");
  return _router;
}

export function initTransport(): void {
  if (_router) return;

  const cfg = loadRoutingConfig();

  const telegram = new TelegramAdapter(
    process.env.TELEGRAM_BOT_TOKEN || "",
    (to) => to // 必要なら userId 変換ロジックを注入
  );
  const email   = new EmailAdapter(process.env.SMTP_URL, process.env.MAIL_FROM);
  const webhook = new WebhookAdapter();

  _router = new TransportRouter([telegram, email, webhook], cfg, emitAudit);
}