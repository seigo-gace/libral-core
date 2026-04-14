/**
 * Python (libral-core) HTTP client - 2026 safe & fast integration
 * Used when LIBRAL_PYTHON_URL is set. Timeout, AbortController, no credential leakage.
 */

const PYTHON_BASE_URL = process.env.LIBRAL_PYTHON_URL ?? "";
const PYTHON_TIMEOUT_MS = Math.min(
  Math.max(parseInt(process.env.LIBRAL_PYTHON_TIMEOUT_MS ?? "5000", 10), 1000),
  30000
);

export interface PythonHealthResponse {
  status: string;
  version?: string;
  architecture?: string;
  modules?: Record<string, { status: string; description?: string }>;
}

const allowedHosts = new Set(["localhost", "127.0.0.1", "::1"]);

function isAllowedUrl(url: string): boolean {
  try {
    const u = new URL(url);
    const host = u.hostname.toLowerCase();
    if (allowedHosts.has(host)) return true;
    if (process.env.NODE_ENV === "production" && host.endsWith(".libral.app")) return true;
    return process.env.NODE_ENV !== "production";
  } catch {
    return false;
  }
}

export async function checkPythonHealth(): Promise<PythonHealthResponse | null> {
  if (!PYTHON_BASE_URL.trim()) return null;
  const url = `${PYTHON_BASE_URL.replace(/\/$/, "")}/health`;
  if (!isAllowedUrl(url)) {
    console.warn("[AI-BRIDGE] Python URL not allowed (host check)");
    return null;
  }
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), PYTHON_TIMEOUT_MS);
  try {
    const res = await fetch(url, {
      method: "GET",
      signal: controller.signal,
      headers: { Accept: "application/json" },
    });
    clearTimeout(timeoutId);
    if (!res.ok) return null;
    const data = (await res.json()) as PythonHealthResponse;
    return data?.status === "healthy" ? data : null;
  } catch (e) {
    clearTimeout(timeoutId);
    if ((e as Error).name === "AbortError") {
      console.warn("[AI-BRIDGE] Python health check timeout");
    }
    return null;
  }
}

export function isPythonConfigured(): boolean {
  return PYTHON_BASE_URL.trim().length > 0;
}
