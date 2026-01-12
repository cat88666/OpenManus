import React, { useState, useEffect } from 'react';
import { Plus } from 'lucide-react';
import axios from 'axios';

interface ProjectsProps {
  userId: string;
}

interface Project {
  id: string;
  title: string;
  status: string;
  budget: number;
  deadline: string;
  created_at: string;
}

export default function Projects({ userId }: ProjectsProps) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProjects();
  }, [userId]);

  const fetchProjects = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/v1/users/${userId}/projects`,
        { params: { skip: 0, limit: 20 } }
      );
      setProjects(response.data.items);
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
        <h1 className="text-3xl font-bold text-white">📋 项目管理</h1>
        <button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition">
          <Plus className="w-5 h-5" />
          创建项目
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {projects.length > 0 ? (
          projects.map((project) => (
            <div key={project.id} className="bg-slate-800 border border-slate-700 rounded-lg p-4">
              <h3 className="text-lg font-bold text-white">{project.title}</h3>
              <p className="text-gray-400 text-sm mt-2">预算: ${project.budget}</p>
              <p className="text-gray-400 text-sm">
                截止: {new Date(project.deadline).toLocaleDateString()}
              </p>
              <span className="inline-block px-3 py-1 rounded text-sm font-medium mt-3 bg-blue-500/20 text-blue-400">
                {project.status}
              </span>
            </div>
          ))
        ) : (
          <div className="col-span-full text-center py-12">
            <p className="text-gray-400">暂无项目</p>
          </div>
        )}
      </div>
    </div>
  );
}
