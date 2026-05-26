"use client";

import { cn } from "@/lib/utils";

const SEVERITIES = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"] as const;

const colors: Record<string, string> = {
  CRITICAL: "bg-red-500/20 border-red-500/40 text-red-400",
  HIGH: "bg-orange-500/20 border-orange-500/40 text-orange-400",
  MEDIUM: "bg-amber-500/20 border-amber-500/40 text-amber-400",
  LOW: "bg-blue-500/20 border-blue-500/40 text-blue-400",
  INFO: "bg-slate-500/20 border-slate-500/40 text-slate-400",
};

interface SeverityBlocksProps {
  data: { severity: string; count: number }[];
}

export function SeverityBlocks({ data }: SeverityBlocksProps) {
  const map = Object.fromEntries(data.map((d) => [d.severity.toUpperCase(), d.count]));

  return (
    <div className="grid grid-cols-5 gap-3">
      {SEVERITIES.map((sev) => (
        <div
          key={sev}
          className={cn("rounded-lg border p-4 text-center backdrop-blur", colors[sev])}
        >
          <p className="text-[10px] font-bold tracking-widest">{sev}</p>
          <p className="mt-1 text-2xl font-bold">{map[sev] ?? 0}</p>
        </div>
      ))}
    </div>
  );
}
