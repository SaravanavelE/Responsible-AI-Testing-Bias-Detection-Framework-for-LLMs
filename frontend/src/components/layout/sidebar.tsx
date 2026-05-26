"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  Plug,
  Scan,
  History,
  FileText,
  Shield,
  Building2,
  ScrollText,
  Settings,
  ShieldCheck,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/llm-connectivity", label: "LLM Connectivity", icon: Plug },
  { href: "/scan", label: "Vulnerability Scan", icon: Scan },
  { href: "/scan-history", label: "Scan History", icon: History },
  { href: "/reports", label: "Reports", icon: FileText },
  { href: "/policy-engine", label: "Policy Engine", icon: Shield },
  { href: "/tenants", label: "Tenant Management", icon: Building2 },
  { href: "/audit-logs", label: "Audit Logs", icon: ScrollText },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-64 flex-col border-r border-white/10 bg-slate-950/80 backdrop-blur-2xl">
      <div className="flex items-center gap-3 border-b border-white/10 px-6 py-5">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 shadow-lg shadow-cyan-500/30">
          <ShieldCheck className="h-6 w-6 text-white" />
        </div>
        <div>
          <p className="text-sm font-bold text-white">ULockAI Shield</p>
          <p className="text-[10px] text-cyan-400/80">Enterprise AI Firewall</p>
        </div>
      </div>
      <nav className="flex-1 space-y-1 overflow-y-auto p-4">
        {navItems.map((item) => {
          const active = pathname.startsWith(item.href);
          const Icon = item.icon;
          return (
            <Link key={item.href} href={item.href}>
              <motion.div
                whileHover={{ x: 4 }}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors",
                  active
                    ? "bg-gradient-to-r from-cyan-600/20 to-blue-600/10 text-cyan-300 border border-cyan-500/20"
                    : "text-slate-400 hover:bg-white/5 hover:text-white"
                )}
              >
                <Icon className="h-4 w-4 shrink-0" />
                {item.label}
              </motion.div>
            </Link>
          );
        })}
      </nav>
      <div className="border-t border-white/10 p-4">
        <div className="rounded-lg bg-emerald-500/10 px-3 py-2 text-xs text-emerald-400">
          <span className="inline-block h-2 w-2 rounded-full bg-emerald-400 mr-2 animate-pulse" />
          Firewall Active
        </div>
      </div>
    </aside>
  );
}
