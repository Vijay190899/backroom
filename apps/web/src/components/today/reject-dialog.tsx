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
    if (busy) return; // ⌘/Ctrl+Enter bypasses the disabled button
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
        <Dialog.Backdrop className="fixed inset-0 z-40 bg-ink/35 transition-opacity duration-200 data-[ending-style]:opacity-0 data-[starting-style]:opacity-0" />
        <Dialog.Popup className="fixed top-1/2 left-1/2 z-50 w-[min(28rem,calc(100vw-2rem))] -translate-x-1/2 -translate-y-1/2 rounded-[var(--t-radius-card)] border border-line bg-surface p-6 shadow-[0_0_0_1px_rgb(0_0_0/0.04),0_24px_48px_-12px_rgb(0_0_0/0.25)] outline-none transition-[opacity,scale] duration-200 data-[ending-style]:scale-95 data-[ending-style]:opacity-0 data-[starting-style]:scale-95 data-[starting-style]:opacity-0">
          <p className="kicker text-press-ink">Not now</p>
          <Dialog.Title className="mt-2 font-display text-3xl leading-tight font-medium tracking-tight text-ink">
            Why not this one?
          </Dialog.Title>
          <Dialog.Description className="mt-2 text-[0.9375rem] leading-relaxed text-muted-foreground">
            &ldquo;{card.title}&rdquo; is skipped. Backroom remembers what you say, and the next
            brief respects it.
          </Dialog.Description>
          <form onSubmit={submit} className="mt-4">
            <label htmlFor={id} className="kicker text-ink">
              Your reason
            </label>
            <textarea
              id={id}
              value={reason}
              onChange={(e) => {
                setReason(e.target.value.slice(0, MAX_REASON));
                if (error) setError(null);
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) e.currentTarget.form?.requestSubmit();
              }}
              rows={3}
              name="reason"
              placeholder="e.g. too steep, max 8%…"
              className="mt-2 w-full resize-none rounded-sm border border-ink/25 bg-background px-3 py-2.5 font-serif text-lg text-ink placeholder:text-muted-foreground focus-visible:border-press"
              aria-describedby={error ? `${id}-error` : undefined}
              aria-invalid={error ? true : undefined}
            />
            {error ? (
              <p id={`${id}-error`} role="alert" className="mt-1.5 text-sm text-neg">
                {error}
              </p>
            ) : null}
            <div className="mt-5 flex justify-end gap-2">
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
