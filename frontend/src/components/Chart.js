import React from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';

function Chart({ data, realtimeData }) {
  // Combine historical and real-time data
  const chartData = [...data];
  
  if (realtimeData.length > 0) {
    realtimeData.forEach(item => {
      chartData.push({
        time: item.time,
        cpu: item.cpu,
        memory: item.memory,
        network: item.network
      });
    });
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="tooltip-label">{payload[0].payload.time}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: {entry.value.toFixed(1)}%
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
        <XAxis 
          dataKey="time" 
          tick={{ fontSize: 12 }}
          angle={-45}
          textAnchor="end"
          height={80}
        />
        <YAxis 
          domain={[0, 100]} 
          label={{ value: 'Utilization (%)', angle: -90, position: 'insideLeft' }}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        <Line type="monotone" dataKey="cpu" name="CPU" stroke="#dc2626" strokeWidth={2} dot={{ r: 2 }} activeDot={{ r: 4 }} isAnimationActive={true} animationDuration={800} />
        <Line type="monotone" dataKey="memory" name="Memory" stroke="#2563eb" strokeWidth={2} dot={{ r: 2 }} activeDot={{ r: 4 }} isAnimationActive={true} animationDuration={800} />
        <Line type="monotone" dataKey="network" name="Network (MB/s)" stroke="#059669" strokeWidth={2} dot={{ r: 2 }} activeDot={{ r: 4 }} isAnimationActive={true} animationDuration={800} />
      </LineChart>
    </ResponsiveContainer>
  );
}

export default Chart;
