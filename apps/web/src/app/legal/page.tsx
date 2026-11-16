import type { Metadata } from "next";
import type { ReactNode } from "react";

import { PageTransition } from "@/components/motion/page-transition";
import { PageHeader } from "@/components/page-header";

export const metadata: Metadata = { title: "Privacy and legal notice" };

const UPDATED = "16 November 2026";

// The operator's details come from the deployment's environment (Vercel project settings),
// not from git: a postal address belongs on the page, not in the repository's history.
// OPERATOR_ADDRESS separates lines with ";".
const operator = {
  name: process.env.OPERATOR_NAME?.trim() ?? "",
  email: process.env.OPERATOR_EMAIL?.trim() ?? "",
  address: (process.env.OPERATOR_ADDRESS ?? "")
    .split(";")
    .map((line) => line.trim())
    .filter(Boolean),
};

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="glass panel mt-6">
      <h2 className="font-display text-2xl font-medium tracking-tight text-ink sm:text-3xl">{title}</h2>
      <div className="mt-3 max-w-[44rem] space-y-3 font-serif text-[1.0625rem] leading-relaxed text-ink/85">
        {children}
      </div>
    </section>
  );
}

function A({ href, children }: { href: string; children: ReactNode }) {
  return (
    <a href={href} className="link-draw text-ink" rel="noreferrer">
      {children}
    </a>
  );
}

export default function LegalPage() {
  const imprint = operator.address.length > 0;
  return (
    <PageTransition>
      <PageHeader
        kicker="Legal"
        title="Privacy and legal notice"
        subtitle="A portfolio demo with fictional businesses and data. No accounts, no cookies, no tracking, no advertising."
      />

      <Section title={imprint ? "Legal notice (Impressum, § 5 DDG)" : "Who runs this site"}>
        {operator.name ? (
          <p>
            {operator.name}
            {operator.address.map((line) => (
              <span key={line}>
                <br />
                {line}
              </span>
            ))}
            {operator.email && (
              <>
                <br />
                Email: <A href={`mailto:${operator.email}`}>{operator.email}</A>
              </>
            )}
          </p>
        ) : (
          <p>The operator&rsquo;s name and contact address will be shown here.</p>
        )}
        <p>
          The operator is the controller for the processing described below (Art. 4(7) GDPR). The
          source code is public on <A href="https://github.com/Vijay190899/backroom">GitHub</A>.
        </p>
      </Section>

      <Section title="What this site is">
        <p>
          Backroom is a demonstration of an agentic back office for a café. Every business, person,
          portal and number in it is fictional; the sales patterns are derived from a public practice
          dataset. You can&rsquo;t sign up, there are no forms, and the site sets no cookies and runs
          no analytics or advertising.
        </p>
      </Section>

      <Section title="When you visit">
        <p>
          <strong className="font-medium text-ink">The website</strong> is delivered by Vercel Inc.
          (USA). To serve pages and keep the service secure, Vercel processes your IP address, the
          time, the page requested and your browser&rsquo;s identification in its server logs.
          Vercel acts as a processor under its data processing addendum; transfers to the USA rely
          on the EU Standard Contractual Clauses, and Vercel states that it is certified under the
          EU&ndash;U.S. Data Privacy Framework.
        </p>
        <p>
          <strong className="font-medium text-ink">The Backroom API</strong> runs on Amazon Web
          Services in Frankfurt, Germany. It keeps no access logs. To protect it from abuse it counts
          requests per IP address in memory for one minute and then forgets them, and its error log
          has IP addresses removed.
        </p>
        <p>
          Both rest on our legitimate interest in a working, secure website (Art. 6(1)(f) GDPR).
          Fonts, images and scripts come from this site itself: no requests go to font services,
          content networks or trackers.
        </p>
      </Section>

      <Section title="Storage in your browser">
        <p>
          No cookies. The site keeps three small values in your browser, only for features you use:
          your light or dark theme and, if you entered one, the live-mode access code (local
          storage), and whether the intro has already played in this session (session storage).
          These are strictly necessary for those features (§ 25(2) no. 2 TDDDG). You can delete them
          in your browser&rsquo;s settings at any time.
        </p>
      </Section>

      <Section title="AI in this demo">
        <p>
          The brief&rsquo;s wording and the browser agent&rsquo;s decisions come from AI models
          (Anthropic&rsquo;s Claude, reached through OpenRouter, USA). Every number shown is computed
          by code and checked against the data before it appears. The models receive only the
          demo&rsquo;s fictional business data, never information about visitors. Without the
          operator&rsquo;s access code, visitors see recorded runs and can&rsquo;t start new model
          calls.
        </p>
      </Section>

      <Section title="Your rights">
        <p>
          You have the right to access (Art. 15 GDPR), rectification (Art. 16), erasure (Art. 17),
          restriction of processing (Art. 18), data portability (Art. 20) and to object to
          processing based on legitimate interests (Art. 21). To use them, write to the operator
          above. You can also complain to a data protection supervisory authority (Art. 77), for
          example the one where you live. There is no automated decision-making or profiling.
        </p>
        <p className="text-sm text-muted-foreground">Last updated {UPDATED}.</p>
      </Section>
    </PageTransition>
  );
}
