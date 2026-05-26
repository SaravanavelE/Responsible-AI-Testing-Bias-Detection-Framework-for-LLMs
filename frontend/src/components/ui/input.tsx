import * as React from "react";
import { cn } from "@/lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => (
    <input
      type={type}
      ref={ref}
      className={cn(
        "flex h-10 w-full rounded-lg border border-slate-600/80 bg-slate-900 px-3 py-2 text-sm text-slate-100",
        "placeholder:text-slate-500",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500/60 focus-visible:border-cyan-500/50",
        "disabled:cursor-not-allowed disabled:opacity-50",
        "[&:-webkit-autofill]:shadow-[inset_0_0_0_1000px_#0f172a] [&:-webkit-autofill]:[-webkit-text-fill-color:#f1f5f9]",
        className
      )}
      {...props}
    />
  )
);
Input.displayName = "Input";

export { Input };
