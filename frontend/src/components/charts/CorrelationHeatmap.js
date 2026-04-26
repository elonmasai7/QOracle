import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Fragment } from 'react';
import { scaleLinear } from 'd3-scale';
export function CorrelationHeatmap({ data }) {
    const labels = [...new Set(data.map((cell) => cell.x))];
    const color = scaleLinear().domain([0, 0.5, 1]).range(['#0F1B2E', '#2563EB', '#8B5CF6']);
    return (_jsx("div", { className: "overflow-x-auto", children: _jsxs("div", { className: "grid min-w-[420px] grid-cols-[100px_repeat(4,1fr)] gap-2", children: [_jsx("div", {}), labels.map((label) => (_jsx("div", { className: "px-2 text-xs font-medium text-slate-400", children: label }, label))), labels.map((row) => (_jsxs(Fragment, { children: [_jsx("div", { className: "flex items-center px-2 text-xs font-medium text-slate-400", children: row }, `${row}-label`), labels.map((column) => {
                            const cell = data.find((item) => item.x === row && item.y === column);
                            const value = cell?.value ?? 0;
                            return (_jsx("div", { className: "flex aspect-square items-center justify-center rounded-xl border border-white/5 text-xs font-semibold text-white", style: { backgroundColor: color(value) }, children: value.toFixed(2) }, `${row}-${column}`));
                        })] }, row)))] }) }));
}
