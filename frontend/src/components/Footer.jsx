import React from "react";
import { Link } from "react-router-dom";
import { Compass, Github, Database, Layers, ShieldCheck, Heart } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-white border-t border-slate-200 mt-auto">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6 text-center md:text-left">
          {/* Brand */}
          <div className="flex flex-col items-center md:items-start gap-2">
            <Link to="/" className="flex items-center gap-2 text-indigo-600 font-bold text-xl tracking-tight">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-sm">
                <Compass className="w-4 h-4" />
              </div>
              <span className="text-slate-900">LearningPath<span className="text-indigo-600">.ai</span></span>
            </Link>
            <p className="text-sm text-slate-500 max-w-sm">
              Adaptive skill pathways with difficulty-ranked milestones and database progress analytics.
            </p>
          </div>

          {/* Quick links */}
          <div className="flex flex-wrap items-center justify-center gap-6 text-sm font-semibold text-slate-600">
            <Link to="/" className="hover:text-indigo-600 transition-colors">
              Home
            </Link>
            <Link to="/skills" className="hover:text-indigo-600 transition-colors">
              Skill Catalog
            </Link>
            <Link to="/dashboard" className="hover:text-indigo-600 transition-colors">
              Dashboard
            </Link>
            <a
              href="http://127.0.0.1:8000/admin/"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-indigo-600 transition-colors"
            >
              Django Admin
            </a>
            <a
              href="https://github.com/Umashankar12345/Learning-path-system"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 hover:text-indigo-600 transition-colors"
            >
              <Github className="w-4 h-4" />
              GitHub
            </a>
          </div>
        </div>

        {/* Badges & Copyright */}
        <div className="mt-8 pt-8 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <div className="flex flex-wrap items-center justify-center gap-2">
            <span className="px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 font-medium border border-slate-200">
              Django 6 + DRF
            </span>
            <span className="px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 font-medium border border-slate-200">
              React 19 + Vite
            </span>
            <span className="px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 font-medium border border-slate-200">
              Relational DB
            </span>
            <span className="px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 font-medium border border-slate-200">
              JWT Secured
            </span>
          </div>

          <p className="text-center sm:text-right">
            © {new Date().getFullYear()} LearningPath System. Built for syllabus practicals & portfolio.
          </p>
        </div>
      </div>
    </footer>
  );
}
