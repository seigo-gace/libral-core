// server/crypto/aegisClient.ts
type EncryptReq = { recipient: string; data: string; policyId: string };
type EncryptRes = { pgp: string };
type SignReq = { data: string; ctxLabels?: Record<string, string> };
type SignRes = { sig: string };
type VerifyReq = { data: string; sig: string; requireContext?: boolean };
type VerifyRes = { ok: boolean; details?: any };
type DecryptReq = { blob: string; policyId: string };
type DecryptRes = { plain: string };
type WkdPathReq = { email: string };
type WkdPathRes = { path: string };
type InspectReq = { blob: string };
type InspectRes = { [key: string]: any };

const AEGIS = process.env.AEGIS_URL || "http://localhost:8787";

export async function encrypt(req: EncryptReq): Promise<EncryptRes> {
  const r = await fetch(`${AEGIS}/v1/encrypt`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(req)
  });
  if (!r.ok) throw new Error(`encrypt failed ${r.status}`);
  return r.json() as Promise<EncryptRes>;
}

export async function decrypt(req: DecryptReq): Promise<DecryptRes> {
  const r = await fetch(`${AEGIS}/v1/decrypt`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(req)
  });
  if (!r.ok) throw new Error(`decrypt failed ${r.status}`);
  return r.json() as Promise<DecryptRes>;
}

export async function sign(req: SignReq): Promise<SignRes> {
  const r = await fetch(`${AEGIS}/v1/sign`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(req)
  });
  if (!r.ok) throw new Error(`sign failed ${r.status}`);
  return r.json() as Promise<SignRes>;
}

export async function verify(req: VerifyReq): Promise<VerifyRes> {
  const r = await fetch(`${AEGIS}/v1/verify`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(req)
  });
  if (!r.ok) throw new Error(`verify failed ${r.status}`);
  return r.json() as Promise<VerifyRes>;
}

export async function getWkdPath(req: WkdPathReq): Promise<WkdPathRes> {
  const r = await fetch(`${AEGIS}/v1/wkd-path?email=${encodeURIComponent(req.email)}`, {
    method: "GET",
    headers: { "content-type": "application/json" }
  });
  if (!r.ok) throw new Error(`wkd-path failed ${r.status}`);
  return r.json() as Promise<WkdPathRes>;
}

export async function inspect(req: InspectReq): Promise<InspectRes> {
  const r = await fetch(`${AEGIS}/v1/inspect`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(req)
  });
  if (!r.ok) throw new Error(`inspect failed ${r.status}`);
  return r.json() as Promise<InspectRes>;
}

// Mock implementation for development when Aegis-PGP Core is not available
export const mockAegisClient = {
  async encrypt(req: EncryptReq): Promise<EncryptRes> {
    console.log(`[MOCK] Encrypting for ${req.recipient} with policy ${req.policyId}`);
    return { pgp: Buffer.from(`MOCK_ENCRYPTED_${Date.now()}`).toString('base64') };
  },

  async decrypt(req: DecryptReq): Promise<DecryptRes> {
    console.log(`[MOCK] Decrypting with policy ${req.policyId}`);
    return { plain: Buffer.from(`MOCK_DECRYPTED_${Date.now()}`).toString('base64') };
  },

  async sign(req: SignReq): Promise<SignRes> {
    console.log(`[MOCK] Signing with context:`, req.ctxLabels);
    return { sig: Buffer.from(`MOCK_SIGNATURE_${Date.now()}`).toString('base64') };
  },

  async verify(req: VerifyReq): Promise<VerifyRes> {
    console.log(`[MOCK] Verifying signature, require context: ${req.requireContext}`);
    return { ok: true, details: { mock: true, verified_at: Date.now() } };
  },

  async getWkdPath(req: WkdPathReq): Promise<WkdPathRes> {
    const hash = Buffer.from(req.email).toString('hex').slice(0, 16);
    return { path: `/.well-known/openpgpkey/hu/${hash}` };
  },

  async inspect(req: InspectReq): Promise<InspectRes> {
    return { 
      type: 'mock',
      size: req.blob.length,
      timestamp: Date.now(),
      info: 'Mock inspection result'
    };
  }
};

// Auto-fallback to mock if Aegis service is unavailable
export const aegisClient = process.env.NODE_ENV === 'development' ? mockAegisClient : {
  encrypt, decrypt, sign, verify, getWkdPath, inspect
};