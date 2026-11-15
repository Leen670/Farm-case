import type { ButtonHTMLAttributes, ReactNode } from "react";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  tone?: "green" | "cream";
  icon?: ReactNode;
  trailing?: ReactNode;
};

export function PixelButton({
  tone = "cream",
  icon,
  trailing,
  className = "",
  type = "button",
  children,
  ...props
}: Props) {
  return (
    <button type={type} className={`pixel-btn pixel-btn-${tone} ${className}`} {...props}>
      <span className="pixel-btn-rim">
        <span className="pixel-btn-face">
          {icon}
          <span className="pixel-btn-label">{children}</span>
          {trailing}
        </span>
      </span>
    </button>
  );
}
