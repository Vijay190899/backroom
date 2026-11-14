import { ViewTransition, type ReactNode } from "react";

/**
 * Wraps a page's content so route changes slide by direction (`nav-forward` /
 * `nav-back`, set on the nav links). Untyped transitions (browser back, refresh,
 * Suspense reveals) do not slide. Lives in each page, not the layout: layouts persist.
 */
export function PageTransition({ children }: { children: ReactNode }) {
  return (
    <ViewTransition
      enter={{ "nav-forward": "nav-forward", "nav-back": "nav-back", default: "none" }}
      exit={{ "nav-forward": "nav-forward", "nav-back": "nav-back", default: "none" }}
      default="none"
    >
      <div>{children}</div>
    </ViewTransition>
  );
}
