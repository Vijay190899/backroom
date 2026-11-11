import type { LucideIcon } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";

/** A route whose real content lands in a later milestone. */
export function PlaceholderPage(props: {
  title: string;
  subtitle: string;
  icon: LucideIcon;
  emptyTitle: string;
  emptyBody: string;
  milestone: string;
}) {
  return (
    <>
      <PageHeader title={props.title} subtitle={props.subtitle} />
      <EmptyState
        icon={props.icon}
        title={props.emptyTitle}
        body={props.emptyBody}
        milestone={props.milestone}
      />
    </>
  );
}
