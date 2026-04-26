import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { cn } from '../../lib/cn';
const variantStyles = {
    primary: 'bg-qr-blue text-white border border-blue-500/70 hover:bg-blue-700 hover:shadow-[0_12px_28px_rgba(37,99,235,0.28)]',
    secondary: 'bg-transparent text-white border border-white/14 hover:bg-white/6',
    ghost: 'bg-transparent text-slate-300 border border-transparent hover:bg-white/5 hover:text-white',
    danger: 'bg-qr-danger text-white border border-red-500/60 hover:bg-red-700',
};
export function Button({ children, className, disabled, icon, loading, variant = 'primary', ...props }) {
    return (_jsxs("button", { className: cn('inline-flex h-12 items-center justify-center gap-2 rounded-[10px] px-6 text-sm font-semibold transition-all duration-150 hover:-translate-y-[1px]', 'disabled:cursor-not-allowed disabled:border-white/10 disabled:bg-slate-700 disabled:text-slate-400', variantStyles[variant], className), disabled: disabled || loading, ...props, children: [loading ? _jsx("span", { className: "size-4 animate-spin rounded-full border-2 border-white/20 border-t-white" }) : icon, _jsx("span", { children: children })] }));
}
