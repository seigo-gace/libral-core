/**
 * API リクエストボディ用 Zod スキーマ（AUDIT_AND_UPDATE_PROPOSAL 推奨に基づく）
 * 各ルートで request.body を parse し、型安全・長さ制限・インジェクション軽減を行う。
 */
import { z } from "zod";

const maxContentLength = 100_000;
const maxQueryLength = 2_000;
const maxCategoryLength = 128;
const maxLanguageLength = 32;

/** POST /api/kb/entries */
export const kbEntryCreateSchema = z.object({
  content: z.string().min(1).max(maxContentLength),
  language: z.string().min(1).max(maxLanguageLength),
  category: z.string().min(1).max(maxCategoryLength),
});

/** PUT /api/kb/entries/:id */
export const kbEntryUpdateSchema = z.object({
  content: z.string().min(1).max(maxContentLength).optional(),
  language: z.string().min(1).max(maxLanguageLength).optional(),
  category: z.string().min(1).max(maxCategoryLength).optional(),
}).refine((data) => data.content !== undefined || data.language !== undefined || data.category !== undefined, {
  message: "At least one of content, language, category must be provided",
});

/** POST /api/kb/search */
export const kbSearchSchema = z.object({
  query: z.string().min(1).max(maxQueryLength),
  language: z.string().max(maxLanguageLength).optional(),
  category: z.string().max(maxCategoryLength).optional(),
  limit: z.number().int().min(1).max(100).optional(),
});

/** POST /api/kbe/knowledge/submit */
export const kbeSubmitSchema = z.object({
  category: z.string().min(1).max(maxCategoryLength),
  content: z.string().min(1).max(maxContentLength),
  tags: z.array(z.string().max(64)).max(20).optional(),
});

/** POST /api/kbe/knowledge/lookup */
export const kbeLookupSchema = z.object({
  query: z.string().min(1).max(maxQueryLength),
  category: z.string().max(maxCategoryLength).optional(),
});

const maxDataLength = 500_000;
const maxBlobLength = 1_000_000;

/** POST /api/aegis/encrypt */
export const aegisEncryptSchema = z.object({
  recipient: z.string().min(1).max(256),
  data: z.string().min(1).max(maxDataLength),
  policyId: z.string().max(64).optional(),
});

/** POST /api/aegis/decrypt */
export const aegisDecryptSchema = z.object({
  blob: z.string().min(1).max(maxBlobLength),
  policyId: z.string().max(64).optional(),
});

/** POST /api/aegis/sign */
export const aegisSignSchema = z.object({
  data: z.string().min(1).max(maxDataLength),
  ctxLabels: z.record(z.string().max(256)).optional(),
});

/** POST /api/aegis/verify */
export const aegisVerifySchema = z.object({
  data: z.string().min(1).max(maxDataLength),
  sig: z.string().min(1).max(maxBlobLength),
  requireContext: z.boolean().optional(),
});

export type KbEntryCreate = z.infer<typeof kbEntryCreateSchema>;
export type KbEntryUpdate = z.infer<typeof kbEntryUpdateSchema>;
export type KbSearch = z.infer<typeof kbSearchSchema>;
export type KbeSubmit = z.infer<typeof kbeSubmitSchema>;
export type KbeLookup = z.infer<typeof kbeLookupSchema>;
export type AegisEncrypt = z.infer<typeof aegisEncryptSchema>;
export type AegisDecrypt = z.infer<typeof aegisDecryptSchema>;
export type AegisSign = z.infer<typeof aegisSignSchema>;
export type AegisVerify = z.infer<typeof aegisVerifySchema>;