import { jsx as _jsx } from "react/jsx-runtime";
import { ResponsiveContainer, Tooltip, Treemap } from 'recharts';
export function ExposureTreemap({ data }) {
    return (_jsx("div", { className: "h-72", children: _jsx(ResponsiveContainer, { width: "100%", height: "100%", children: _jsx(Treemap, { data: data, dataKey: "size", stroke: "rgba(255,255,255,.16)", fill: "#2563EB", children: _jsx(Tooltip, { contentStyle: { background: '#0F1B2E', border: '1px solid rgba(255,255,255,.08)', borderRadius: 12 } }) }) }) }));
}
