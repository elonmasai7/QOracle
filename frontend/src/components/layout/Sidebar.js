import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { cn } from '../../lib/cn';
import { useAppStore } from '../../store/app-store';
const navItems = [
    { key: 'dashboard', label: 'Dashboard', short: 'DB' },
    { key: 'portfolios', label: 'Portfolios', short: 'PF' },
    { key: 'risk-engine', label: 'Risk Engine', short: 'RE' },
    { key: 'stress-testing', label: 'Stress Testing', short: 'ST' },
    { key: 'forecasting', label: 'Forecasting', short: 'FC' },
    { key: 'reports', label: 'Reports', short: 'RP' },
    { key: 'compliance', label: 'Compliance', short: 'CP' },
    { key: 'settings', label: 'Settings', short: 'SE' },
];
export function Sidebar() {
    const { activeView, setActiveView, sidebarExpanded, toggleSidebar } = useAppStore();
    return (_jsxs("aside", { className: cn('surface-panel sticky top-24 hidden h-[calc(100vh-7rem)] flex-col overflow-hidden px-3 py-4 lg:flex', sidebarExpanded ? 'w-[260px]' : 'w-[72px]'), children: [_jsxs("button", { type: "button", onClick: toggleSidebar, className: "mb-6 flex h-11 items-center rounded-xl border border-white/10 bg-white/5 px-3 text-left text-sm text-white transition hover:bg-white/8", children: [_jsx("span", { className: "inline-flex size-8 items-center justify-center rounded-lg bg-qr-blue/20 text-xs font-semibold text-blue-300", children: "QR" }), sidebarExpanded ? _jsx("span", { className: "ml-3 font-medium", children: "Workspace" }) : null] }), _jsx("nav", { className: "space-y-1.5", children: navItems.map((item) => {
                    const active = item.key === activeView;
                    return (_jsxs("button", { type: "button", onClick: () => setActiveView(item.key), className: cn('flex h-11 w-full items-center rounded-xl px-3 text-sm transition-all duration-150', active ? 'bg-blue-600/16 text-white shadow-[inset_0_0_0_1px_rgba(37,99,235,0.45)]' : 'text-slate-300 hover:bg-white/5 hover:text-white'), children: [_jsx("span", { className: "inline-flex size-8 items-center justify-center rounded-lg border border-white/10 bg-white/5 text-[11px] font-semibold", children: item.short }), sidebarExpanded ? _jsx("span", { className: "ml-3", children: item.label }) : null] }, item.key));
                }) }), _jsx("div", { className: "mt-auto rounded-xl border border-white/10 bg-gradient-to-br from-blue-600/14 to-cyan-500/10 p-4", children: sidebarExpanded ? (_jsxs(_Fragment, { children: [_jsx("p", { className: "text-xs uppercase tracking-[0.2em] text-slate-400", children: "Quantum Hybrid" }), _jsx("p", { className: "mt-2 text-sm font-medium text-white", children: "Qiskit acceleration available" }), _jsx("p", { className: "mt-1 text-xs leading-5 text-slate-400", children: "Queue quantum-assisted tail calibration on selected simulations." })] })) : (_jsx("div", { className: "mx-auto size-8 rounded-lg bg-cyan-500/20" })) })] }));
}
