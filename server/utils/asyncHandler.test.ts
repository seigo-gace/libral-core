import { describe, it, expect, vi } from "vitest";
import { asyncHandler } from "./asyncHandler";

describe("asyncHandler", () => {
  it("calls handler and passes through return", async () => {
    const handler = vi.fn().mockResolvedValue(undefined);
    const wrapped = asyncHandler(handler);
    const req = {} as any;
    const res = {} as any;
    const next = vi.fn();
    await wrapped(req, res, next);
    expect(handler).toHaveBeenCalledWith(req, res, next);
    expect(next).not.toHaveBeenCalled();
  });

  it("calls next(err) when handler rejects", async () => {
    const err = new Error("test");
    const handler = vi.fn().mockRejectedValue(err);
    const wrapped = asyncHandler(handler);
    const next = vi.fn();
    await wrapped({} as any, {} as any, next);
    expect(next).toHaveBeenCalledWith(err);
  });
});
