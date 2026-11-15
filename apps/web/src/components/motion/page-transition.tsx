import { ViewTransition, type ReactNode } from "react";

/**
 * Wraps a page's content so route changes fade through (L-79, L-81). Every page's wrapper
 * shares the view-transition name `page`, so the old and new page pair up under one name
 * and globals.css times them by name: the core of the spec, so it holds in every browser
 * with view transitions (Safari included), not only those with transition classes.
 * Only nav-link changes (`nav-forward` / `nav-back`) animate; browser back, refresh and
 * in-page updates (the brief's stories) do not. Lives in each page: layouts persist.
 */
export function PageTransition({ children }: { children: ReactNode }) {
  return (
    <ViewTransition
      name="page"
      share={{ "nav-forward": "page-swap", "nav-back": "page-swap", default: "none" }}
      enter="none"
      exit="none"
      update="none"
      default="none"
    >
      <div>{children}</div>
    </ViewTransition>
  );
}
