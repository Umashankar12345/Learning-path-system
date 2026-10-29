import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Compass, BookOpen, User, LogOut, CheckCircle2 } from "lucide-react";

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <Link to="/" className="flex items-center gap-2 text-indigo-600 font-bold text-xl tracking-tight">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-sm">
            <Compass className="w-5 h-5" />
          </div>
          <span className="text-slate-900">LearningPath<span className="text-indigo-600">.ai</span></span>
        </Link>

        {/* Navigation links */}
        <nav className="hidden md:flex items-center gap-6">
          <Link to="/" className="text-sm font-medium text-slate-600 hover:text-indigo-600 transition-colors">
            Home
          </Link>
          <Link to="/skills" className="text-sm font-medium text-slate-600 hover:text-indigo-600 transition-colors">
            Explore Skills
          </Link>
          {isAuthenticated && (
            <Link to="/dashboard" className="text-sm font-medium text-slate-600 hover:text-indigo-600 transition-colors">
              Dashboard
            </Link>
          )}
        </nav>

        {/* Auth CTA */}
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <div className="flex items-center gap-4">
              <Link
                to="/dashboard"
                className="flex items-center gap-2 text-sm font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded-lg transition-colors"
              >
                <User className="w-4 h-4 text-indigo-600" />
                <span>{user?.username}</span>
              </Link>
              <button
                onClick={handleLogout}
                className="flex items-center gap-1.5 text-sm font-medium text-rose-600 hover:text-rose-700 hover:bg-rose-50 px-3 py-1.5 rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <Link
                to="/login"
                className="text-sm font-medium text-slate-700 hover:text-indigo-600 px-3 py-2 transition-colors"
              >
                Log In
              </Link>
              <Link
                to="/signup"
                className="text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 px-4 py-2 rounded-lg shadow-sm transition-colors"
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
