import { Sunrise } from "lucide-react";

import { PlaceholderPage } from "@/components/placeholder-page";

export default function TodayPage() {
  return (
    <PlaceholderPage
      title="Today"
      subtitle="The three things that matter for Hafer & Bohne, with the money behind each one."
      icon={Sunrise}
      emptyTitle="No brief yet"
      emptyBody="The morning brief is built from the till, supplier invoices and the weather. Each card will carry its evidence and a one-tap action."
      milestone="Arrives in M3"
    />
  );
}
