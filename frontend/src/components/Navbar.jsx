import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Compass, BookOpen, User, LogOut, Trophy, FileCode, CheckCircle2 } from "lucide-react";

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-sm">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link to="/" className="flex items-center gap-2.5 text-indigo-600 font-bold text-xl tracking-tight">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-sm">
            <Compass className="w-5 h-5" />
          </div>
          <span className="text-slate-900 font-black">LearningPath<span className="text-indigo-600">.ai</span></span>
        </Link>

        {/* Navigation links */}
        <nav className="hidden md:flex items-center gap-7">
          <Link to="/" className="text-sm font-bold text-slate-600 hover:text-indigo-600 transition-colors">
            Home
          </Link>
          <Link to="/skills" className="text-sm font-bold text-slate-600 hover:text-indigo-600 transition-colors">
            Explore Skills
          </Link>
          <Link to="/leaderboard" className="text-sm font-bold text-slate-600 hover:text-indigo-600 transition-colors flex items-center gap-1.5">
            <Trophy className="w-4 h-4 text-amber-500" />
            Leaderboard
          </Link>
          {isAuthenticated && (
            <Link to="/dashboard" className="text-sm font-bold text-slate-600 hover:text-indigo-600 transition-colors">
              Dashboard
            </Link>
          )}
          <a
            href="http://127.0.0.1:8000/api/docs/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs font-bold text-indigo-600 bg-indigo-50 hover:bg-indigo-100 px-2.5 py-1 rounded-lg border border-indigo-200 transition-colors flex items-center gap-1"
            title="Interactive Swagger OpenAPI Documentation"
          >
            <FileCode className="w-3.5 h-3.5" />
            Swagger Docs
          </a>
        </nav>

        {/* Auth CTA */}
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <div className="flex items-center gap-3">
              <Link
                to="/dashboard"
                className="flex items-center gap-2 text-sm font-bold text-slate-800 bg-slate-100 hover:bg-slate-200 px-3.5 py-2 rounded-xl transition-colors"
              >
                <User className="w-4 h-4 text-indigo-600" />
                <span>{user?.username}</span>
              </Link>
              <button
                onClick={handleLogout}
                className="flex items-center gap-1.5 text-xs font-bold text-rose-600 hover:text-rose-700 hover:bg-rose-50 px-3 py-2 rounded-xl transition-colors"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Logout</span>
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <Link
                to="/login"
                className="text-sm font-bold text-slate-700 hover:text-indigo-600 px-3.5 py-2 transition-colors"
              >
                Sign In
              </Link>
              <Link
                to="/signup"
                className="text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 px-4 py-2 rounded-xl shadow-sm transition-colors"
              >
                Get Started
              </Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
