import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Menu, X, Rocket } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Opportunities from './pages/Opportunities';
import Projects from './pages/Projects';
import KnowledgeBase from './pages/KnowledgeBase';
import Analytics from './pages/Analytics';

function App() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [userId, setUserId] = useState('demo-user-001');

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
        {/* 导航栏 */}
        <nav className="bg-slate-950 border-b border-slate-700 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              {/* Logo */}
              <Link to="/" className="flex items-center gap-2 text-white font-bold text-xl">
                <Rocket className="w-6 h-6 text-blue-500" />
                <span>AI数字员工平台</span>
              </Link>

              {/* 桌面导航 */}
              <div className="hidden md:flex gap-8">
                <Link to="/" className="text-gray-300 hover:text-white transition">
                  仪表板
                </Link>
                <Link to="/opportunities" className="text-gray-300 hover:text-white transition">
                  机会
                </Link>
                <Link to="/projects" className="text-gray-300 hover:text-white transition">
                  项目
                </Link>
                <Link to="/knowledge" className="text-gray-300 hover:text-white transition">
                  知识库
                </Link>
                <Link to="/analytics" className="text-gray-300 hover:text-white transition">
                  分析
                </Link>
              </div>

              {/* 用户信息 */}
              <div className="hidden md:flex items-center gap-4">
                <input
                  type="text"
                  value={userId}
                  onChange={(e) => setUserId(e.target.value)}
                  placeholder="用户ID"
                  className="px-3 py-2 bg-slate-800 text-white rounded border border-slate-700 text-sm"
                />
              </div>

              {/* 移动菜单按钮 */}
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="md:hidden text-gray-300 hover:text-white"
              >
                {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>

            {/* 移动导航 */}
            {isMenuOpen && (
              <div className="md:hidden pb-4 space-y-2">
                <Link to="/" className="block text-gray-300 hover:text-white py-2">
                  仪表板
                </Link>
                <Link to="/opportunities" className="block text-gray-300 hover:text-white py-2">
                  机会
                </Link>
                <Link to="/projects" className="block text-gray-300 hover:text-white py-2">
                  项目
                </Link>
                <Link to="/knowledge" className="block text-gray-300 hover:text-white py-2">
                  知识库
                </Link>
                <Link to="/analytics" className="block text-gray-300 hover:text-white py-2">
                  分析
                </Link>
              </div>
            )}
          </div>
        </nav>

        {/* 主内容 */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard userId={userId} />} />
            <Route path="/opportunities" element={<Opportunities userId={userId} />} />
            <Route path="/projects" element={<Projects userId={userId} />} />
            <Route path="/knowledge" element={<KnowledgeBase userId={userId} />} />
            <Route path="/analytics" element={<Analytics userId={userId} />} />
          </Routes>
        </main>

        {/* 页脚 */}
        <footer className="bg-slate-950 border-t border-slate-700 mt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center text-gray-400 text-sm">
              <p>AI数字员工平台 v1.0 | 智能外包接单和交付系统</p>
              <p className="mt-2">
                <a href="https://github.com/cat88666/OpenManus" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300">
                  GitHub
                </a>
              </p>
            </div>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}

export default App;
