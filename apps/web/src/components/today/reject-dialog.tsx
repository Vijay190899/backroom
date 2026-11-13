"use client";

import { Dialog } from "@base-ui/react/dialog";
import { useId, useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import type { ActionCard } from "@/lib/contracts";

const MAX_REASON = 500;

export function RejectDialog({
  card,
  open,
  onOpenChange,
  onSubmit,
}: {
  card: ActionCard;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (reason: string) => Promise<void>;
}) {
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const id = useId();

  async function submit(event: FormEvent) {
    event.preventDefault();
    const text = reason.trim();
    if (!text) {
      setError("Tell Backroom why, in a few words: it learns from this.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await onSubmit(text);
      setReason("");
      onOpenChange(false);
    } catch {
      setError("That didn't go through. Try again in a moment.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Backdrop className="fixed inset-0 z-40 bg-ink/30 transition-opacity duration-200 data-[ending-style]:opacity-0 data-[starting-style]:opacity-0" />
        <Dialog.Popup className="fixed top-1/2 left-1/2 z-50 w-[min(28rem,calc(100vw-2rem))] -translate-x-1/2 -translate-y-1/2 rounded-[var(--t-radius-card)] border border-line bg-surface p-5 shadow-xl outline-none transition-[opacity,scale] duration-200 data-[ending-style]:scale-95 data-[ending-style]:opacity-0 data-[starting-style]:scale-95 data-[starting-style]:opacity-0">
          <Dialog.Title className="font-display text-2xl text-ink">Not now</Dialog.Title>
          <Dialog.Description className="mt-1 text-sm text-muted-foreground">
            Why not &ldquo;{card.title}&rdquo;? Backroom remembers what you say and the next brief
            respects it.
          </Dialog.Description>
          <form onSubmit={submit} className="mt-4">
            <label htmlFor={id} className="text-sm font-medium text-ink">
              Reason
            </label>
            <textarea
              id={id}
              value={reason}
              onChange={(e) => setReason(e.target.value.slice(0, MAX_REASON))}
              rows={3}
              placeholder="e.g. too steep, max 8%"
              className="mt-1.5 w-full resize-none rounded-lg border border-line bg-background px-3 py-2 text-ink placeholder:text-muted-foreground/70 focus-visible:outline-2"
              aria-describedby={error ? `${id}-error` : undefined}
              aria-invalid={error ? true : undefined}
            />
            {error ? (
              <p id={`${id}-error`} role="alert" className="mt-1.5 text-sm text-neg">
                {error}
              </p>
            ) : null}
            <div className="mt-4 flex justify-end gap-2">
              <Dialog.Close render={<Button variant="ghost" size="lg" type="button" />}>
                Cancel
              </Dialog.Close>
              <Button type="submit" size="lg" disabled={busy}>
                {busy ? "Saving…" : "Skip this card"}
              </Button>
            </div>
          </form>
        </Dialog.Popup>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
