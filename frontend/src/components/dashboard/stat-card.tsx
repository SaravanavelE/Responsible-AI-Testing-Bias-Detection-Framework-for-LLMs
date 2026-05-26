"use client";

import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: string;
  variant?: "default" | "critical" | "success" | "warning";
}

const variants = {
  default: "from-cyan-600/20 to-blue-600/10 border-cyan-500/20",
  critical: "from-red-600/20 to-orange-600/10 border-red-500/30",
  success: "from-emerald-600/20 to-green-600/10 border-emerald-500/30",
  warning: "from-amber-600/20 to-yellow-600/10 border-amber-500/30",
};

export function StatCard({ title, value, subtitle, icon: Icon, trend, variant = "default" }: StatCardProps) {
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} whileHover={{ scale: 1.02 }}>
      <Card className={cn("bg-gradient-to-br border", variants[variant])}>
        <CardContent className="p-5">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs font-medium uppercase tracking-wider text-slate-400">{title}</p>
              <p className="mt-2 text-3xl font-bold text-white">{value}</p>
              {subtitle && <p className="mt-1 text-xs text-slate-500">{subtitle}</p>}
              {trend && <p className="mt-2 text-xs text-cyan-400">{trend}</p>}
            </div>
            <div className="rounded-lg bg-white/5 p-2.5">
              <Icon className="h-5 w-5 text-cyan-400" />
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
