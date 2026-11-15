import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import { Providers } from "@/components/providers";
import { AppShell } from "@/components/shell/app-shell";
import { API_URL } from "@/lib/api";
import { motionInitScript } from "@/lib/motion-pref";
import { themeInitScript } from "@/lib/theme";

import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
// Mono only appears in evidence, the dock and the skill steps, so it is fetched on first use.
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"], preload: false });

export const metadata: Metadata = {
  title: { default: "Backroom", template: "%s · Backroom" },
  description:
    "An agentic back office for a local café: it finds money in the business data and carries out the fix.",
};

export const viewport: Viewport = {
  viewportFit: "cover",
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#f4f1ec" },
    { media: "(prefers-color-scheme: dark)", color: "#0a0908" },
  ],
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: `${themeInitScript};${motionInitScript}` }} />
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
