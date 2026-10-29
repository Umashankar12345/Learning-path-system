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
    <aside className="w-full flex flex-col gap-5">
      {/* User Identity Panel */}
      <div className="sidebar p-4">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-600 text-white font-black text-base flex items-center justify-center shadow-md flex-shrink-0">
            {user?.username?.slice(0, 2).toUpperCase()}
          </div>
          <div className="min-w-0 flex-1">
            <h4 className="text-sm font-extrabold truncate">
              {user?.first_name || user?.username}
            </h4>
            <p className="text-xs text-muted truncate">@{user?.username}</p>
          </div>
        </div>

        {/* Quick KPI badges inside sidebar */}
        <div className="mt-3 pt-3 border-t border-[#dde3ec] grid grid-cols-2 gap-2 text-center text-xs">
          <div className="bg-[#eef2f7] py-1.5 px-2 rounded-lg border border-[#dde3ec]">
            <div className="flex items-center justify-center gap-1 text-amber-500 font-bold">
              <Flame className="w-3.5 h-3.5 fill-amber-500" />
              <span>{streak}d</span>
            </div>
            <span className="text-[10px] text-muted font-semibold uppercase">Streak</span>
          </div>
          <div className="bg-[#eef2f7] py-1.5 px-2 rounded-lg border border-[#dde3ec]">
            <div className="flex items-center justify-center gap-1 text-indigo-600 font-bold">
              <Clock className="w-3.5 h-3.5" />
              <span>{hours}h</span>
            </div>
            <span className="text-[10px] text-muted font-semibold uppercase">Learned</span>
          </div>
        </div>
      </div>

      {/* Main Navigation Panel */}
      <div className="panel p-2.5">
        <div className="px-3 py-1.5 text-[11px] font-bold uppercase tracking-wider text-muted">
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
                    ? "bg-[#eef0ff] text-indigo-700 font-extrabold shadow-sm border border-[#d9dcff]"
                    : "text-muted hover:text-indigo-600 hover:bg-[#eef2f7]"
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
        <div className="mt-3 pt-3 border-t border-[#dde3ec]">
          <div className="px-3 py-1.5 text-[11px] font-bold uppercase tracking-wider text-muted">
            Developer & Admin
          </div>
          <div className="space-y-1 mt-1">
            <a
              href="http://127.0.0.1:8000/api/docs/"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-muted hover:text-indigo-600 hover:bg-[#eef2f7] transition-colors"
            >
              <FileCode className="w-4 h-4 text-slate-400" />
              <span>Swagger API Docs</span>
            </a>
            <a
              href="http://127.0.0.1:8000/admin/"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-muted hover:text-indigo-600 hover:bg-[#eef2f7] transition-colors"
            >
              <Shield className="w-4 h-4 text-slate-400" />
              <span>Django Admin</span>
            </a>
          </div>
        </div>
      </div>

      {/* Enrolled Paths Fast Switcher */}
      {activePaths.length > 0 && (
        <div className="panel p-3">
          <div className="px-2 py-1 text-[11px] font-bold uppercase tracking-wider text-muted flex items-center justify-between">
            <span>Enrolled Paths</span>
            <span className="text-muted">{activePaths.length}</span>
          </div>

          <div className="space-y-2 mt-2">
            {activePaths.map((p) => (
              <Link
                key={p.id}
                to={`/paths/${p.id}`}
                className="group block p-2.5 rounded-xl hover:bg-[#eef0ff] border border-transparent hover:border-[#d9dcff] transition-all"
              >
                <div className="flex items-center justify-between text-xs font-bold group-hover:text-indigo-700">
                  <span className="truncate pr-2">{p.skill.name}</span>
                  <span className="text-[11px] font-extrabold text-muted">
                    {p.progress_percentage}%
                  </span>
                </div>
                <div className="progress w-full h-1.5 mt-2 overflow-hidden">
                  <div
                    className="progress-bar h-1.5"
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
