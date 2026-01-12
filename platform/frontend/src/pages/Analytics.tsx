import React from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface AnalyticsProps {
  userId: string;
}

export default function Analytics({ userId }: AnalyticsProps) {
  // 模拟数据
  const trendData = [
    { date: '1月1日', opportunities: 10, applications: 3, success: 1 },
    { date: '1月2日', opportunities: 12, applications: 4, success: 1 },
    { date: '1月3日', opportunities: 15, applications: 5, success: 2 },
    { date: '1月4日', opportunities: 14, applications: 4, success: 1 },
    { date: '1月5日', opportunities: 18, applications: 6, success: 2 },
    { date: '1月6日', opportunities: 20, applications: 7, success: 2 },
    { date: '1月7日', opportunities: 22, applications: 8, success: 3 },
  ];

  const platformData = [
    { name: 'Upwork', value: 45 },
    { name: 'LinkedIn', value: 30 },
    { name: 'Toptal', value: 25 },
  ];

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b'];

  const metrics = [
    { label: '成功率', value: '75%', change: '↑ 5%' },
    { label: '平均预算', value: '$2,500', change: '↑ $200' },
    { label: '总收入', value: '$15,000', change: '↑ $3,000' },
    { label: '平均响应时间', value: '2.5h', change: '↓ 0.5h' },
  ];

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-white">📈 数据分析</h1>

      {/* 关键指标 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric, index) => (
          <div key={index} className="bg-slate-800 border border-slate-700 rounded-lg p-4">
            <p className="text-gray-400 text-sm">{metric.label}</p>
            <p className="text-2xl font-bold text-white mt-2">{metric.value}</p>
            <p className="text-green-400 text-sm mt-1">{metric.change}</p>
          </div>
        ))}
      </div>

      {/* 趋势分析 */}
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
        <h2 className="text-xl font-bold text-white mb-4">30天趋势</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={trendData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
            <XAxis dataKey="date" stroke="#9ca3af" />
            <YAxis stroke="#9ca3af" />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
              labelStyle={{ color: '#f1f5f9' }}
            />
            <Legend />
            <Line type="monotone" dataKey="opportunities" stroke="#3b82f6" name="机会数" />
            <Line type="monotone" dataKey="applications" stroke="#10b981" name="申请数" />
            <Line type="monotone" dataKey="success" stroke="#f59e0b" name="成功数" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* 平台分布 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4">平台分布</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={platformData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name} ${value}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {platformData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4">预算分布</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={[
              { range: '$0-1k', count: 5 },
              { range: '$1k-2k', count: 12 },
              { range: '$2k-5k', count: 18 },
              { range: '$5k-10k', count: 8 },
              { range: '$10k+', count: 3 },
            ]}>
              <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
              <XAxis dataKey="range" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
                labelStyle={{ color: '#f1f5f9' }}
              />
              <Bar dataKey="count" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
