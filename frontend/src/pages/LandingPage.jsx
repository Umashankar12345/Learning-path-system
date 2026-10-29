import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  Sparkles,
  ArrowRight,
  Target,
  BarChart3,
  CheckCircle,
  Layers,
  GraduationCap,
} from "lucide-react";

export default function LandingPage() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 lg:py-32">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 text-center">
          <div className="inline-flex items-center gap-2 bg-indigo-50 border border-indigo-200/60 text-indigo-700 px-4 py-1.5 rounded-full text-xs font-semibold uppercase tracking-wider mb-6 shadow-sm">
            <Sparkles className="w-3.5 h-3.5" />
            AI-Powered Personalized Roadmaps
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-slate-900 max-w-4xl mx-auto leading-tight">
            Master Any Skill with an <span className="bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">Adaptive Learning Path</span>
          </h1>
          <p className="mt-6 text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Choose your goal — from <strong>Python for Data Science</strong> to <strong>Full-Stack Web Development</strong>. Our recommender curates courses, articles, and real-world projects ordered by difficulty and dynamically tracks your learning progress.
          </p>

          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            {isAuthenticated ? (
              <Link
                to="/dashboard"
                className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-6 py-3.5 rounded-xl shadow-lg hover:shadow-indigo-500/25 transition-all text-base"
              >
                Go to Dashboard
                <ArrowRight className="w-4 h-4" />
              </Link>
            ) : (
              <>
                <Link
                  to="/signup"
                  className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-6 py-3.5 rounded-xl shadow-lg hover:shadow-indigo-500/25 transition-all text-base"
                >
                  Create Free Account
                  <ArrowRight className="w-4 h-4" />
                </Link>
                <Link
                  to="/skills"
                  className="inline-flex items-center gap-2 bg-white hover:bg-slate-100 text-slate-800 font-semibold px-6 py-3.5 rounded-xl border border-slate-300 shadow-sm transition-all text-base"
                >
                  Explore Skill Goals
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      {/* Feature Highlights */}
      <section className="py-16 bg-white border-y border-slate-200">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="text-center max-w-xl mx-auto mb-14">
            <h2 className="text-3xl font-bold tracking-tight text-slate-900">
              Engineered for Real Knowledge Retention
            </h2>
            <p className="mt-3 text-slate-600">
              Everything you need to systematically progress from beginner concepts to production capstone projects.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="p-6 bg-slate-50 rounded-2xl border border-slate-200 hover:border-indigo-300 transition-colors">
              <div className="w-12 h-12 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center mb-5">
                <Target className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">Difficulty-Ranked Milestones</h3>
              <p className="text-slate-600 text-sm leading-relaxed">
                Resources are automatically categorized into Beginner, Intermediate, and Advanced tiers to prevent cognitive overload.
              </p>
            </div>

            <div className="p-6 bg-slate-50 rounded-2xl border border-slate-200 hover:border-indigo-300 transition-colors">
              <div className="w-12 h-12 rounded-xl bg-violet-100 text-violet-600 flex items-center justify-center mb-5">
                <BarChart3 className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">Real Database Analytics</h3>
              <p className="text-slate-600 text-sm leading-relaxed">
                Live metrics calculating actual hours learned, completion percentages, day streaks, and weekly hours visual charts.
              </p>
            </div>

            <div className="p-6 bg-slate-50 rounded-2xl border border-slate-200 hover:border-indigo-300 transition-colors">
              <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center mb-5">
                <CheckCircle className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">Progress & Rating Sync</h3>
              <p className="text-slate-600 text-sm leading-relaxed">
                Mark items complete, record completion timestamps, and leave ratings that inform adaptive recommendations.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
