import React, { useState, useEffect } from 'react';
import { Plus, Search, Filter, Star } from 'lucide-react';
import axios from 'axios';

interface OpportunitiesProps {
  userId: string;
}

interface Opportunity {
  id: string;
  title: string;
  platform: string;
  budget: number;
  ai_score: number;
  status: string;
  tech_stack: string[];
  created_at: string;
}

export default function Opportunities({ userId }: OpportunitiesProps) {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState('all');
  const [platformFilter, setPlatformFilter] = useState('all');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    platform: 'upwork',
    budget: 0,
    tech_stack: []
  });

  useEffect(() => {
    fetchOpportunities();
  }, [userId, statusFilter, platformFilter]);

  const fetchOpportunities = async () => {
    try {
      setLoading(true);
      const params = {
        skip: 0,
        limit: 20,
        status: statusFilter === 'all' ? null : statusFilter,
        platform: platformFilter === 'all' ? null : platformFilter
      };
      
      const response = await axios.get(
        `http://localhost:8000/api/v1/users/${userId}/opportunities`,
        { params }
      );
      setOpportunities(response.data.items);
      setError(null);
    } catch (err) {
      setError('无法加载机会列表');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateOpportunity = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post(
        `http://localhost:8000/api/v1/opportunities`,
        formData,
        { params: { user_id: userId } }
      );
      setShowCreateForm(false);
      setFormData({
        title: '',
        description: '',
        platform: 'upwork',
        budget: 0,
        tech_stack: []
      });
      fetchOpportunities();
    } catch (err) {
      setError('创建机会失败');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-400">加载中...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 标题和操作按钮 */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-white">🎯 机会管理</h1>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition"
        >
          <Plus className="w-5 h-5" />
          创建机会
        </button>
      </div>

      {/* 创建表单 */}
      {showCreateForm && (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4">创建新机会</h2>
          <form onSubmit={handleCreateOpportunity} className="space-y-4">
            <div>
              <label className="block text-gray-300 text-sm font-medium mb-2">标题</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="输入机会标题"
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
                required
              />
            </div>

            <div>
              <label className="block text-gray-300 text-sm font-medium mb-2">描述</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="输入机会描述"
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
                rows={4}
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-gray-300 text-sm font-medium mb-2">平台</label>
                <select
                  value={formData.platform}
                  onChange={(e) => setFormData({ ...formData, platform: e.target.value })}
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded text-white focus:border-blue-500 focus:outline-none"
                >
                  <option value="upwork">Upwork</option>
                  <option value="linkedin">LinkedIn</option>
                  <option value="toptal">Toptal</option>
                </select>
              </div>

              <div>
                <label className="block text-gray-300 text-sm font-medium mb-2">预算</label>
                <input
                  type="number"
                  value={formData.budget}
                  onChange={(e) => setFormData({ ...formData, budget: parseFloat(e.target.value) })}
                  placeholder="0"
                  className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
                  min="0"
                  step="100"
                />
              </div>
            </div>

            <div className="flex gap-2">
              <button
                type="submit"
                className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded transition"
              >
                创建
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="flex-1 bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded transition"
              >
                取消
              </button>
            </div>
          </form>
        </div>
      )}

      {/* 过滤器 */}
      <div className="flex gap-4">
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-gray-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 bg-slate-800 border border-slate-700 rounded text-white focus:border-blue-500 focus:outline-none"
          >
            <option value="all">所有状态</option>
            <option value="discovered">已发现</option>
            <option value="reviewed">已审核</option>
            <option value="applied">已申请</option>
            <option value="won">已赢得</option>
          </select>

          <select
            value={platformFilter}
            onChange={(e) => setPlatformFilter(e.target.value)}
            className="px-4 py-2 bg-slate-800 border border-slate-700 rounded text-white focus:border-blue-500 focus:outline-none"
          >
            <option value="all">所有平台</option>
            <option value="upwork">Upwork</option>
            <option value="linkedin">LinkedIn</option>
            <option value="toptal">Toptal</option>
          </select>
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="bg-red-900/20 border border-red-700 rounded-lg p-4 text-red-300">
          {error}
        </div>
      )}

      {/* 机会列表 */}
      <div className="space-y-3">
        {opportunities.length > 0 ? (
          opportunities.map((opp) => (
            <div
              key={opp.id}
              className="bg-slate-800 border border-slate-700 rounded-lg p-4 hover:border-slate-600 transition"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-white">{opp.title}</h3>
                  <p className="text-gray-400 text-sm mt-1">
                    {opp.platform} • ${opp.budget}
                  </p>
                  <div className="flex gap-2 mt-2">
                    {opp.tech_stack?.map((tech) => (
                      <span
                        key={tech}
                        className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs"
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="text-right">
                  <div className="flex items-center gap-1 justify-end">
                    <Star className="w-5 h-5 text-yellow-400" />
                    <span className="text-xl font-bold text-white">{opp.ai_score || 'N/A'}</span>
                  </div>
                  <span className={`inline-block px-3 py-1 rounded text-sm font-medium mt-2 ${
                    opp.status === 'discovered' ? 'bg-blue-500/20 text-blue-400' :
                    opp.status === 'reviewed' ? 'bg-yellow-500/20 text-yellow-400' :
                    opp.status === 'applied' ? 'bg-purple-500/20 text-purple-400' :
                    'bg-green-500/20 text-green-400'
                  }`}>
                    {opp.status}
                  </span>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-400">暂无机会</p>
          </div>
        )}
      </div>
    </div>
  );
}
