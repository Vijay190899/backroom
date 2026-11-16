import Link from "next/link";

/** On every page: the legal notice must be reachable from anywhere on the site. */
export function SiteFooter() {
  return (
    <footer className="mt-16 flex flex-wrap items-center gap-x-5 gap-y-2 border-t border-line pt-5 text-sm text-muted-foreground">
      <p>A demo: every business, person and number in it is fictional.</p>
      <nav aria-label="Legal" className="flex gap-x-5 sm:ml-auto">
        <Link href="/legal" className="link-draw inline-flex min-h-11 items-center text-ink sm:min-h-0">
          Privacy and legal notice
        </Link>
        <a
          href="https://github.com/Vijay190899/backroom"
          className="link-draw inline-flex min-h-11 items-center text-ink sm:min-h-0"
          rel="noreferrer"
        >
          Source
        </a>
      </nav>
    </footer>
  );
}
