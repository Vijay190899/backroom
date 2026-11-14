"use client";

import { Button } from "@/components/ui/button";

/**
 * Route-level boundary: a lazily loaded piece (the evidence drawer, the reject dialog)
 * that fails to download lands here instead of on Next's default error screen.
 */
export default function Error({ retry }: { error: unknown; retry: () => void }) {
  return (
    <section role="alert" className="border-y border-line py-16 text-center">
      <p className="kicker text-press-ink">Something went wrong</p>
      <h1 className="mt-3 font-display text-4xl font-medium tracking-tight text-ink">
        This page didn&rsquo;t finish loading.
      </h1>
      <p className="mx-auto mt-3 max-w-md text-muted-foreground">
        Check the connection, then try again.
      </p>
      <Button size="lg" className="mt-6" onClick={() => retry()}>
        Try again
      </Button>
    </section>
  );
}
