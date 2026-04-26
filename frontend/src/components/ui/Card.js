import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { cn } from '../../lib/cn';
export function Card({ title, subtitle, action, className, children }) {
    return (_jsxs("section", { className: cn('surface-panel p-5', className), children: [(title || subtitle || action) && (_jsxs("div", { className: "mb-4 flex items-start justify-between gap-4", children: [_jsxs("div", { children: [title ? _jsx("h3", { className: "text-sm font-semibold text-white", children: title }) : null, subtitle ? _jsx("p", { className: "mt-1 text-sm text-slate-400", children: subtitle }) : null] }), action] })), children] }));
}
