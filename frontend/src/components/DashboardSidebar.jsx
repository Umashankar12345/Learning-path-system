import React from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  LayoutDashboard,
  Compass,
  Trophy,
  FileCode,
  Shield,
  BookOpen,
  Flame,
  Clock,
  LogOut,
  ChevronRight,
  Sparkles,
} from "lucide-react";

export default function DashboardSidebar({ activePaths = [], streak = 0, hours = 0 }) {
  const { user, logout } = useAuth();
  const location = useLocation();

  const navItems = [
    { name: "Overview", path: "/dashboard", icon: LayoutDashboard },
    { name: "Explore Skills", path: "/skills", icon: Compass },
    { name: "Leaderboard", path: "/leaderboard", icon: Trophy },
  ];

  return (
    <aside className="w-full flex flex-col gap-6">
      {/* User Identity Card */}
      <div className="bg-white rounded-2xl border border-[#e2e8f0] p-4 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 text-white font-black text-base flex items-center justify-center shadow-md flex-shrink-0">
            {user?.username?.slice(0, 2).toUpperCase()}
          </div>
          <div className="min-w-0 flex-1">
            <h4 className="text-sm font-extrabold text-[#0f172a] truncate">
              {user?.first_name || user?.username}
            </h4>
            <p className="text-xs text-[#64748b] truncate">@{user?.username}</p>
          </div>
        </div>

        {/* Quick KPI badges inside sidebar */}
        <div className="mt-3 pt-3 border-t border-[#e2e8f0] grid grid-cols-2 gap-2 text-center text-xs">
          <div className="bg-slate-50 py-1.5 px-2 rounded-lg border border-slate-100">
            <div className="flex items-center justify-center gap-1 text-amber-500 font-bold">
              <Flame className="w-3.5 h-3.5 fill-amber-500" />
              <span>{streak}d</span>
            </div>
            <span className="text-[10px] text-slate-400 font-semibold uppercase">Streak</span>
          </div>
          <div className="bg-slate-50 py-1.5 px-2 rounded-lg border border-slate-100">
            <div className="flex items-center justify-center gap-1 text-indigo-600 font-bold">
              <Clock className="w-3.5 h-3.5" />
              <span>{hours}h</span>
            </div>
            <span className="text-[10px] text-slate-400 font-semibold uppercase">Learned</span>
          </div>
        </div>
      </div>

      {/* Main Navigation Menu */}
      <div className="bg-white rounded-2xl border border-[#e2e8f0] p-2.5 shadow-sm">
        <div className="px-3 py-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-400">
          Navigation
        </div>
        <nav className="space-y-1 mt-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            const Icon = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-bold transition-all ${
                  isActive
                    ? "bg-indigo-50 text-indigo-700 font-extrabold shadow-sm"
                    : "text-slate-600 hover:text-indigo-600 hover:bg-slate-50"
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Icon className={`w-4 h-4 ${isActive ? "text-indigo-600" : "text-slate-400"}`} />
                  <span>{item.name}</span>
                </div>
                {isActive && <div className="w-1.5 h-1.5 rounded-full bg-indigo-600"></div>}
              </Link>
            );
          })}
        </nav>

        {/* Developer & Admin shortcuts */}
        <div className="mt-3 pt-3 border-t border-[#e2e8f0]">
          <div className="px-3 py-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-400">
            Developer & Admin
          </div>
          <div className="space-y-1 mt-1">
            <a
              href="http://127.0.0.1:8000/api/docs/"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:text-indigo-600 hover:bg-slate-50 transition-colors"
            >
              <FileCode className="w-4 h-4 text-slate-400" />
              <span>Swagger API Docs</span>
            </a>
            <a
              href="http://127.0.0.1:8000/admin/"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:text-indigo-600 hover:bg-slate-50 transition-colors"
            >
              <Shield className="w-4 h-4 text-slate-400" />
              <span>Django Admin</span>
            </a>
          </div>
        </div>
      </div>

      {/* Enrolled Paths Fast Switcher */}
      {activePaths.length > 0 && (
        <div className="bg-white rounded-2xl border border-[#e2e8f0] p-3 shadow-sm">
          <div className="px-2 py-1 text-[11px] font-bold uppercase tracking-wider text-slate-400 flex items-center justify-between">
            <span>Enrolled Paths</span>
            <span className="text-slate-400">{activePaths.length}</span>
          </div>

          <div className="space-y-2 mt-2">
            {activePaths.map((p) => (
              <Link
                key={p.id}
                to={`/paths/${p.id}`}
                className="group block p-2.5 rounded-xl hover:bg-indigo-50/60 border border-transparent hover:border-indigo-100 transition-all"
              >
                <div className="flex items-center justify-between text-xs font-bold text-slate-800 group-hover:text-indigo-700">
                  <span className="truncate pr-2">{p.skill.name}</span>
                  <span className="text-[11px] font-extrabold text-slate-500">
                    {p.progress_percentage}%
                  </span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-1.5 mt-2 overflow-hidden">
                  <div
                    className="bg-indigo-600 h-1.5 rounded-full"
                    style={{ width: `${p.progress_percentage}%` }}
                  ></div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </aside>
  );
}
