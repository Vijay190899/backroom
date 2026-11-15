import { z } from "zod";

export const healthSchema = z.object({
  status: z.enum(["ok", "degraded"]),
  checks: z.object({
    postgres: z.enum(["ok", "down"]),
    portals: z.enum(["ok", "down"]),
    llm: z.object({ provider: z.string(), configured: z.boolean() }),
  }),
  demo_mode: z.enum(["live", "replay"]),
});
export type Health = z.infer<typeof healthSchema>;
