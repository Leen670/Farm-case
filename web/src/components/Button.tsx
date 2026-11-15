import type { ButtonHTMLAttributes } from "react";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary";
};

export function Button({ variant = "primary", className = "", type = "button", ...props }: Props) {
  const look =
    variant === "primary"
      ? "bg-lime text-navy hover:bg-[#b7ea45] disabled:bg-[#e4e0c8] disabled:text-ink/40"
      : "bg-white text-navy border border-navy/10 hover:bg-cream disabled:text-ink/40";
  return (
    <button
      type={type}
      className={`inline-flex items-center justify-center rounded-lg px-5 py-2.5 text-sm font-extrabold tracking-wide transition disabled:cursor-not-allowed ${look} ${className}`}
      {...props}
    />
  );
}
