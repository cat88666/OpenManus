import React, { useState, useEffect } from 'react';
import { TrendingUp, Briefcase, CheckCircle, BookOpen } from 'lucide-react';
import axios from 'axios';

interface DashboardProps {
  userId: string;
}

interface DashboardData {
  total_opportunities: number;
  total_applications: number;
  total_projects: number;
  knowledge_assets_count: number;
  recent_opportunities: any[];
  recent_projects: any[];
}

export default function Dashboard({ userId }: DashboardProps) {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, [userId]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `http://localhost:8000/api/v1/users/${userId}/dashboard`
      );
      setData(response.data);
      setError(null);
    } catch (err) {
      setError('无法加载仪表板数据');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-400">加载中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-700 rounded-lg p-4 text-red-300">
        {error}
      </div>
    );
  }

  const metrics = [
    {
      label: '总机会数',
      value: data?.total_opportunities || 0,
      icon: Briefcase,
      color: 'bg-blue-500/20 text-blue-400'
    },
    {
      label: '申请数',
      value: data?.total_applications || 0,
      icon: TrendingUp,
      color: 'bg-green-500/20 text-green-400'
    },
    {
      label: '项目数',
      value: data?.total_projects || 0,
      icon: CheckCircle,
      color: 'bg-purple-500/20 text-purple-400'
    },
    {
      label: '知识资产',
      value: data?.knowledge_assets_count || 0,
      icon: BookOpen,
      color: 'bg-orange-500/20 text-orange-400'
    }
  ];

  return (
    <div className="space-y-8">
      {/* 关键指标 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric, index) => {
          const Icon = metric.icon;
          return (
            <div
              key={index}
              className="bg-slate-800 border border-slate-700 rounded-lg p-6 hover:border-slate-600 transition"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">{metric.label}</p>
                  <p className="text-3xl font-bold text-white mt-2">{metric.value}</p>
                </div>
                <div className={`${metric.color} p-3 rounded-lg`}>
                  <Icon className="w-6 h-6" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* 最近的机会 */}
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
        <h2 className="text-xl font-bold text-white mb-4">🎯 最近的机会</h2>
        {data?.recent_opportunities && data.recent_opportunities.length > 0 ? (
          <div className="space-y-3">
            {data.recent_opportunities.slice(0, 5).map((opp) => (
              <div
                key={opp.id}
                className="flex items-center justify-between p-3 bg-slate-700/50 rounded border border-slate-600 hover:border-slate-500 transition"
              >
                <div className="flex-1">
                  <p className="text-white font-medium">{opp.title}</p>
                  <p className="text-gray-400 text-sm">
                    {opp.platform} • ${opp.budget} • 评分: {opp.ai_score || 'N/A'}
                  </p>
                </div>
                <span className={`px-3 py-1 rounded text-sm font-medium ${
                  opp.status === 'discovered' ? 'bg-blue-500/20 text-blue-400' :
                  opp.status === 'reviewed' ? 'bg-yellow-500/20 text-yellow-400' :
                  opp.status === 'applied' ? 'bg-purple-500/20 text-purple-400' :
                  'bg-green-500/20 text-green-400'
                }`}>
                  {opp.status}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-400">暂无机会</p>
        )}
      </div>

      {/* 最近的项目 */}
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
        <h2 className="text-xl font-bold text-white mb-4">📋 最近的项目</h2>
        {data?.recent_projects && data.recent_projects.length > 0 ? (
          <div className="space-y-3">
            {data.recent_projects.slice(0, 5).map((project) => (
              <div
                key={project.id}
                className="flex items-center justify-between p-3 bg-slate-700/50 rounded border border-slate-600 hover:border-slate-500 transition"
              >
                <div className="flex-1">
                  <p className="text-white font-medium">{project.title}</p>
                  <p className="text-gray-400 text-sm">
                    预算: ${project.budget} • 截止: {project.deadline ? new Date(project.deadline).toLocaleDateString() : 'N/A'}
                  </p>
                </div>
                <span className={`px-3 py-1 rounded text-sm font-medium ${
                  project.status === 'in_progress' ? 'bg-blue-500/20 text-blue-400' :
                  project.status === 'review' ? 'bg-yellow-500/20 text-yellow-400' :
                  project.status === 'delivered' ? 'bg-green-500/20 text-green-400' :
                  'bg-purple-500/20 text-purple-400'
                }`}>
                  {project.status}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-400">暂无项目</p>
        )}
      </div>
    </div>
  );
}
