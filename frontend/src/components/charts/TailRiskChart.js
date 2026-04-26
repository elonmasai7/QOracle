import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Cell, ResponsiveContainer, Tooltip, XAxis, YAxis, Bar, BarChart } from 'recharts';
export function TailRiskChart({ data }) {
    return (_jsx("div", { className: "h-72", children: _jsx(ResponsiveContainer, { width: "100%", height: "100%", children: _jsxs(BarChart, { data: data, children: [_jsx(XAxis, { dataKey: "percentile", stroke: "#64748B", tickLine: false, axisLine: false }), _jsx(YAxis, { stroke: "#64748B", tickLine: false, axisLine: false }), _jsx(Tooltip, { contentStyle: { background: '#0F1B2E', border: '1px solid rgba(255,255,255,.08)', borderRadius: 12 } }), _jsx(Bar, { dataKey: "loss", radius: [6, 6, 0, 0], children: data.map((entry) => (_jsx(Cell, { fill: entry.marker === 'CVaR' ? '#DC2626' : entry.marker === 'VaR' ? '#D97706' : '#2563EB' }, entry.percentile))) })] }) }) }));
}
