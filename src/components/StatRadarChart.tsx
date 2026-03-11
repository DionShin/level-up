'use client';

import { useRouter } from 'next/navigation';
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer,
} from 'recharts';
import type { Stat } from '@/lib/types';

interface Props {
  stats: Stat[];
}

// PolarAngleAxis의 커스텀 tick - 클릭 가능한 라벨
function CustomTick({ x, y, payload, stats, onClick }: any) {
  const stat = stats.find((s: Stat) => s.name === payload.value);
  return (
    <g onClick={() => stat && onClick(stat.id)} style={{ cursor: 'pointer' }}>
      {/* 클릭 영역 확대용 투명 rect */}
      <rect x={x - 28} y={y - 14} width={56} height={28} fill="transparent" />
      <text
        x={x}
        y={y - 4}
        textAnchor="middle"
        fontSize={11}
        fontWeight="700"
        fill={stat?.color ?? '#94a3b8'}
      >
        {stat?.icon} {payload.value}
      </text>
      <text
        x={x}
        y={y + 10}
        textAnchor="middle"
        fontSize={10}
        fill="#64748b"
      >
        {stat?.score ?? 0}
      </text>
    </g>
  );
}

export default function StatRadarChart({ stats }: Props) {
  const router = useRouter();

  const data = stats.map(s => ({
    subject: s.name,
    value: s.score,
    fullMark: 100,
  }));

  const handleClick = (statId: string) => {
    router.push(`/stat/${statId}`);
  };

  return (
    <ResponsiveContainer width="100%" height="100%">
      <RadarChart cx="50%" cy="50%" outerRadius="62%" data={data}>
        <PolarGrid stroke="#1e293b" />
        <PolarAngleAxis
          dataKey="subject"
          tick={(props) => (
            <CustomTick {...props} stats={stats} onClick={handleClick} />
          )}
        />
        <Radar
          name="Stats"
          dataKey="value"
          stroke="#3b82f6"
          fill="#3b82f6"
          fillOpacity={0.25}
          dot={{ r: 3, fill: '#60a5fa', strokeWidth: 0 }}
          activeDot={{ r: 5, fill: '#93c5fd' }}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}
