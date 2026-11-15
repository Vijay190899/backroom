import { PageTransition } from "@/components/motion/page-transition";
import { TodayBrief } from "@/components/today/today-brief";

export default function TodayPage() {
  return (
    <PageTransition>
      <TodayBrief />
    </PageTransition>
  );
}
