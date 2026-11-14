import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono, Newsreader } from "next/font/google";
import localFont from "next/font/local";

import { Providers } from "@/components/providers";
import { AppShell } from "@/components/shell/app-shell";
import { API_URL } from "@/lib/api";
import { themeInitScript } from "@/lib/theme";

import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
// Mono only appears inside the evidence drawer, so it is fetched on first use.
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"], preload: false });
// Text serif (standfirsts, story decks): Newsreader at its text optical size.
const newsreader = Newsreader({ variable: "--font-newsreader", subsets: ["latin"] });
// Headline serif: Newsreader's display cut (opsz 60, weight 500) as a 31 KB Latin subset,
// built from the OFL variable font (src/fonts/OFL.txt). The full variable font with
// its opsz axis is 132 KB and cost the phone LCP budget (DECISIONS L-69).
const newsreaderDisplay = localFont({
  src: "../fonts/newsreader-display.woff2",
  variable: "--font-newsreader-display",
  weight: "500",
  display: "swap",
});

export const metadata: Metadata = {
  title: { default: "Backroom", template: "%s · Backroom" },
  description:
    "An agentic back office for a local café: it finds money in the business data and carries out the fix.",
};

export const viewport: Viewport = {
  viewportFit: "cover",
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#f2ece1" },
    { media: "(prefers-color-scheme: dark)", color: "#13110e" },
  ],
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${geistSans.variable} ${geistMono.variable} ${newsreader.variable} ${newsreaderDisplay.variable} h-full antialiased`}
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
        {/* The brief and health calls go cross-origin: open that connection during HTML parse. */}
        <link rel="preconnect" href={API_URL} crossOrigin="anonymous" />
      </head>
      <body className="min-h-full">
        <a
          href="#main"
          className="sr-only rounded-md bg-ink px-4 py-2 text-background focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50"
        >
          Skip to content
        </a>
        <Providers>
          <AppShell>{children}</AppShell>
        </Providers>
      </body>
    </html>
  );
}
