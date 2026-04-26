import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
export function ScenarioComparisonChart({ data }) {
    return (_jsx("div", { className: "h-72", children: _jsx(ResponsiveContainer, { width: "100%", height: "100%", children: _jsxs(BarChart, { data: data, children: [_jsx(CartesianGrid, { stroke: "rgba(255,255,255,.08)", vertical: false }), _jsx(XAxis, { dataKey: "name", stroke: "#64748B", tickLine: false, axisLine: false }), _jsx(YAxis, { stroke: "#64748B", tickLine: false, axisLine: false }), _jsx(Tooltip, { contentStyle: { background: '#0F1B2E', border: '1px solid rgba(255,255,255,.08)', borderRadius: 12 } }), _jsx(Legend, {}), _jsx(Bar, { dataKey: "base", fill: "#2563EB", radius: [6, 6, 0, 0] }), _jsx(Bar, { dataKey: "stressed", fill: "#DC2626", radius: [6, 6, 0, 0] })] }) }) }));
}
