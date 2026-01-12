import React, { useState, useEffect } from 'react';
import { Plus, Search } from 'lucide-react';
import axios from 'axios';

interface KnowledgeBaseProps {
  userId: string;
}

interface Asset {
  id: string;
  title: string;
  asset_type: string;
  quality_score: number;
  reuse_count: number;
  created_at: string;
}

export default function KnowledgeBase({ userId }: KnowledgeBaseProps) {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [assetTypeFilter, setAssetTypeFilter] = useState('all');

  useEffect(() => {
    fetchAssets();
  }, [assetTypeFilter]);

  const fetchAssets = async () => {
    try {
      const params = {
        skip: 0,
        limit: 50,
        asset_type: assetTypeFilter === 'all' ? null : assetTypeFilter
      };
      
      const response = await axios.get(
        'http://localhost:8000/api/v1/knowledge-assets',
        { params }
      );
      setAssets(response.data.items);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-gray-400">加载中...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-white">📚 知识库</h1>
        <button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition">
          <Plus className="w-5 h-5" />
          添加资产
        </button>
      </div>

      <div className="flex gap-4">
        <div className="flex items-center gap-2">
          <Search className="w-5 h-5 text-gray-400" />
          <select
            value={assetTypeFilter}
            onChange={(e) => setAssetTypeFilter(e.target.value)}
            className="px-4 py-2 bg-slate-800 border border-slate-700 rounded text-white focus:border-blue-500 focus:outline-none"
          >
            <option value="all">所有类型</option>
            <option value="code">代码</option>
            <option value="doc">文档</option>
            <option value="template">模板</option>
            <option value="workflow">工作流</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {assets.length > 0 ? (
          assets.map((asset) => (
            <div key={asset.id} className="bg-slate-800 border border-slate-700 rounded-lg p-4 hover:border-slate-600 transition">
              <h3 className="text-lg font-bold text-white">{asset.title}</h3>
              <p className="text-gray-400 text-sm mt-2">
                类型: {asset.asset_type}
              </p>
              <div className="flex justify-between items-center mt-4">
                <span className="text-yellow-400 text-sm">
                  质量: {(asset.quality_score * 100).toFixed(0)}%
                </span>
                <span className="text-blue-400 text-sm">
                  复用: {asset.reuse_count}次
                </span>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-full text-center py-12">
            <p className="text-gray-400">暂无知识资产</p>
          </div>
        )}
      </div>
    </div>
  );
}
