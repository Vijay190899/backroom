import { Gauge, Info, Sunrise, Waypoints, Workflow, type LucideIcon } from "lucide-react";

export type NavItem = { href: string; label: string; icon: LucideIcon };

export const NAV_ITEMS: NavItem[] = [
  { href: "/", label: "Today", icon: Sunrise },
  { href: "/memory", label: "Memory", icon: Waypoints },
  { href: "/skills", label: "Skills", icon: Workflow },
  { href: "/bench", label: "Bench", icon: Gauge },
  { href: "/about", label: "About", icon: Info },
];

export function isActive(pathname: string, href: string): boolean {
  return href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(`${href}/`);
}

/** Forward when the target sits right of (after) the current section, else back. */
export function navDirection(pathname: string, href: string): "nav-forward" | "nav-back" {
  const at = NAV_ITEMS.findIndex((item) => isActive(pathname, item.href));
  const to = NAV_ITEMS.findIndex((item) => item.href === href);
  return to > at ? "nav-forward" : "nav-back";
}
