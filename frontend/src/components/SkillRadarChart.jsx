import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

export default function SkillRadarChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <RadarChart data={data} outerRadius="72%">
        <PolarGrid stroke="rgba(148, 163, 184, .24)" />
        <PolarAngleAxis dataKey="topic" tick={{ fill: "#cbd5e1", fontSize: 11 }} />
        <PolarRadiusAxis
          angle={30}
          domain={[0, 100]}
          tick={{ fill: "#94a3b8", fontSize: 10 }}
          axisLine={false}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#111827",
            border: "1px solid rgba(148, 163, 184, .25)",
            borderRadius: "12px",
            color: "#f8fafc",
          }}
          formatter={(value, name) => [value, name === "score" ? "Skill score" : name]}
        />
        <Radar
          name="Skill score"
          dataKey="score"
          stroke="#818cf8"
          fill="#6366f1"
          fillOpacity={0.45}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}
