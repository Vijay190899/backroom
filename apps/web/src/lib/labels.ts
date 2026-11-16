import type { SkillSummary } from "@/lib/contracts";

/** Display names for the (fictional) merchant portals. */
export const PORTAL_LABEL: Record<string, string> = {
  grainline: "Grainline",
  tilldesk: "TillDesk",
  localboard: "Localboard",
};

export const TASK_LABEL: Record<SkillSummary["task"], string> = {
  "grainline.reorder_item": "Reorder an item",
  "grainline.download_invoice": "Download an invoice",
  "grainline.cancel_order": "Cancel an order",
  "tilldesk.change_price": "Change a menu price",
  "localboard.post_special": "Post today's special",
};
