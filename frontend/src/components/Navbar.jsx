import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  BookOpen,
  Code2,
  Compass,
  FileCode,
  Github,
  Home,
  LogOut,
  Menu,
  Trophy,
  User,
  X,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();

  const location = useLocation();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const navItems = [
    { label: "Home", to: "/", icon: Home },
    { label: "Explore Skills", to: "/skills", icon: BookOpen },
    { label: "Leaderboard", to: "/leaderboard", icon: Trophy },
    { label: "Coding Arena", to: "/challenges", icon: Code2 },
    ...(isAuthenticated
      ? [{ label: "Dashboard", to: "/dashboard", icon: Compass }]
      : []),
    {
      label: "API Docs",
      href: "http://127.0.0.1:8000/api/docs/",
      icon: FileCode,
    },
    {
      label: "Source",
      href: "https://github.com/Umashankar12345/Learning-path-system",
      icon: Github,
    },
  ];

  const handleLogout = () => {
    setMenuOpen(false);
    logout();
    navigate("/login");
  };

  const renderNavItem = (item, mobile = false) => {
    const Icon = item.icon;
    const isActive = item.to === location.pathname;
    const itemClass = mobile
      ? `flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-semibold transition-colors ${
          isActive
            ? "bg-indigo-50 text-indigo-700"
            : "text-slate-600 hover:bg-slate-50 hover:text-indigo-700"
        }`
      : `flex shrink-0 items-center gap-2 rounded-full px-3 py-2 text-[13px] font-semibold transition-all ${
          isActive
            ? "bg-white text-indigo-700 shadow-sm ring-1 ring-slate-200/80"
            : "text-slate-600 hover:bg-white/80 hover:text-indigo-700"
        }`;

    if (item.href) {
      return (
        <a
          key={item.label}
          href={item.href}
          target="_blank"
          rel="noopener noreferrer"
          onClick={() => setMenuOpen(false)}
          className={itemClass}
        >
          <Icon className={`h-4 w-4 ${item.label === "Leaderboard" ? "text-amber-500" : "text-indigo-500"}`} />
          <span>{item.label}</span>
        </a>
      );
    }

    return (
      <Link
        key={item.to}
        to={item.to}
        onClick={() => setMenuOpen(false)}
        aria-current={isActive ? "page" : undefined}
        className={itemClass}
      >
        <Icon className={`h-4 w-4 ${isActive ? "text-indigo-600" : "text-slate-400"}`} />
        <span>{item.label}</span>
      </Link>
    );
  };

  return (
    <header className="site-header sticky top-0 z-50 border-b border-slate-200/80 bg-white/90 backdrop-blur-xl">
      <div className="mx-auto flex h-[4.5rem] max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <Link
          to="/"
          onClick={() => setMenuOpen(false)}
          className="group flex shrink-0 items-center gap-2.5"
          aria-label="LearningPath.ai home"
        >
          <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-600 via-indigo-600 to-violet-500 text-white shadow-lg shadow-indigo-600/25 transition-transform group-hover:-rotate-3 group-hover:scale-105">
            <Compass className="h-5 w-5" />
          </span>
          <span className="text-[17px] font-black tracking-tight text-slate-900 sm:text-lg">
            LearningPath<span className="text-indigo-600">.ai</span>
          </span>
        </Link>

        <nav
          aria-label="Main navigation"
          className="hidden items-center gap-0.5 rounded-full border border-slate-200/80 bg-slate-100/70 p-1 shadow-inner xl:flex"
        >
          {navItems.map((item) => renderNavItem(item))}
        </nav>

        <div className="ml-auto flex shrink-0 items-center gap-2 sm:gap-3">
          {isAuthenticated ? (
            <>
              <Link
                to="/dashboard"
                className="flex max-w-36 items-center gap-2 rounded-full border border-slate-200 bg-white px-2.5 py-2 text-sm font-bold text-slate-800 shadow-sm transition hover:border-indigo-200 hover:bg-indigo-50/60 sm:px-3"
              >
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-indigo-100 text-indigo-700">
                  <User className="h-3.5 w-3.5" />
                </span>
                <span className="hidden truncate sm:inline">{user?.username}</span>
              </Link>
              <button
                onClick={handleLogout}
                className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-2 text-xs font-bold text-rose-600 transition hover:bg-rose-50 hover:text-rose-700 sm:px-3"
              >
                <LogOut className="h-4 w-4" />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="hidden rounded-full px-3 py-2 text-sm font-bold text-slate-600 transition hover:bg-slate-100 hover:text-indigo-700 sm:inline-flex sm:px-4"
              >
                Sign In
              </Link>
              <Link
                to="/signup"
                className="rounded-full bg-gradient-to-r from-indigo-600 to-violet-600 px-4 py-2.5 text-sm font-bold text-white shadow-md shadow-indigo-600/20 transition hover:-translate-y-0.5 hover:shadow-lg hover:shadow-indigo-600/25"
              >
                Get Started
              </Link>
            </>
          )}

          <button
            type="button"
            aria-label={menuOpen ? "Close navigation menu" : "Open navigation menu"}
            aria-expanded={menuOpen}
            aria-controls="mobile-primary-navigation"
            onClick={() => setMenuOpen((open) => !open)}
            className="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-700 shadow-sm transition hover:border-indigo-200 hover:bg-indigo-50 hover:text-indigo-700 xl:hidden"
          >
            {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {menuOpen && (
        <div
          id="mobile-primary-navigation"
          className="border-t border-slate-200/80 bg-white/95 px-4 py-3 shadow-xl shadow-slate-900/5 backdrop-blur-xl xl:hidden sm:px-6"
        >
          <nav aria-label="Mobile navigation" className="mx-auto grid max-w-7xl gap-1 sm:grid-cols-2">
            {navItems.map((item) => renderNavItem(item, true))}
            {!isAuthenticated && (
              <>
                {renderNavItem({ label: "Sign In", to: "/login", icon: User }, true)}
                {renderNavItem({ label: "Get Started", to: "/signup", icon: User }, true)}
              </>
            )}
          </nav>
        </div>
      )}
    </header>
  );
}
