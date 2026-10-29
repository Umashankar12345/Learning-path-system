import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  Sparkles,
  ArrowRight,
  Target,
  BarChart3,
  CheckCircle2,
  Layers,
  GraduationCap,
  ShieldCheck,
  Star,
  Compass,
} from "lucide-react";

export default function LandingPage() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-slate-50/60 text-slate-900">
      {/* Centered Hero Section */}
      <section className="relative overflow-hidden py-20 lg:py-28">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 text-center space-y-6">
          <div className="inline-flex items-center gap-2 bg-indigo-50 border border-indigo-200 text-indigo-700 px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider shadow-sm">
            <Sparkles className="w-4 h-4" />
            Personalized Learning Path Dashboard
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-slate-900 leading-[1.12]">
            Master In-Demand Skills with an{" "}
            <span className="bg-gradient-to-r from-indigo-600 via-violet-600 to-indigo-600 bg-clip-text text-transparent">
              Adaptive Learning Path
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Choose your goal — from <strong>Python for Data Science</strong> to <strong>Full-Stack Web Development</strong>. Our recommender arranges courses, articles, and real-world projects ordered by difficulty and dynamically tracks your learning progress.
          </p>

          <div className="pt-4 flex flex-wrap items-center justify-center gap-4">
            {isAuthenticated ? (
              <Link
                to="/dashboard"
                className="inline-flex items-center gap-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-7 py-4 rounded-2xl shadow-lg hover:shadow-indigo-500/25 transition-all text-base"
              >
                Go to Dashboard
                <ArrowRight className="w-5 h-5" />
              </Link>
            ) : (
              <>
                <Link
                  to="/signup"
                  className="inline-flex items-center gap-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-7 py-4 rounded-2xl shadow-lg hover:shadow-indigo-500/25 transition-all text-base"
                >
                  Start Learning Free
                  <ArrowRight className="w-5 h-5" />
                </Link>
                <Link
                  to="/skills"
                  className="inline-flex items-center gap-2.5 bg-white hover:bg-slate-100 text-slate-800 font-bold px-7 py-4 rounded-2xl border border-slate-300 shadow-sm transition-all text-base"
                >
                  Explore Skill Goals
                </Link>
              </>
            )}
          </div>

          {/* Social Proof / Capability Badges */}
          <div className="pt-8 flex flex-wrap items-center justify-center gap-3">
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold bg-white text-slate-700 border border-slate-200 shadow-sm">
              <ShieldCheck className="w-3.5 h-3.5 text-indigo-600" />
              Django 6 + DRF Backend
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold bg-white text-slate-700 border border-slate-200 shadow-sm">
              <Star className="w-3.5 h-3.5 text-amber-500 fill-amber-400" />
              5-Star Module Ratings
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold bg-white text-slate-700 border border-slate-200 shadow-sm">
              <BarChart3 className="w-3.5 h-3.5 text-emerald-600" />
              Real Database Analytics
            </span>
          </div>
        </div>
      </section>

      {/* 3 Pillar Features with Centered Cards */}
      <section className="py-20 bg-white border-y border-slate-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <div className="text-center max-w-xl mx-auto mb-16">
            <h2 className="text-3xl sm:text-4xl font-black tracking-tight text-slate-900">
              Engineered for Maximum Retention
            </h2>
            <p className="mt-3 text-slate-600 text-base sm:text-lg">
              Everything you need to progress from foundational concepts to production-grade applications.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Pillar 1 */}
            <div className="p-8 bg-slate-50 rounded-3xl border border-slate-200 hover:border-indigo-300 hover:shadow-lg transition-all flex flex-col justify-between">
              <div>
                <div className="w-14 h-14 rounded-2xl bg-indigo-100 text-indigo-600 flex items-center justify-center mb-6 shadow-sm">
                  <Target className="w-7 h-7" />
                </div>
                <div className="inline-block px-2.5 py-0.5 rounded text-[11px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 uppercase mb-3">
                  Pillar 1
                </div>
                <h3 className="text-xl font-black text-slate-900 mb-2">Ranked Milestones</h3>
                <p className="text-slate-600 text-sm leading-relaxed">
                  Resources are organized into Beginner, Intermediate, and Advanced tiers to prevent cognitive overload.
                </p>
              </div>
            </div>

            {/* Pillar 2 */}
            <div className="p-8 bg-slate-50 rounded-3xl border border-slate-200 hover:border-indigo-300 hover:shadow-lg transition-all flex flex-col justify-between">
              <div>
                <div className="w-14 h-14 rounded-2xl bg-violet-100 text-violet-600 flex items-center justify-center mb-6 shadow-sm">
                  <BarChart3 className="w-7 h-7" />
                </div>
                <div className="inline-block px-2.5 py-0.5 rounded text-[11px] font-bold bg-violet-50 text-violet-700 border border-violet-200 uppercase mb-3">
                  Pillar 2
                </div>
                <h3 className="text-xl font-black text-slate-900 mb-2">Live DB Metrics</h3>
                <p className="text-slate-600 text-sm leading-relaxed">
                  Zero hard-coded numbers. Tracks actual hours learned, completion percentages, streaks, and weekly activity charts.
                </p>
              </div>
            </div>

            {/* Pillar 3 */}
            <div className="p-8 bg-slate-50 rounded-3xl border border-slate-200 hover:border-indigo-300 hover:shadow-lg transition-all flex flex-col justify-between">
              <div>
                <div className="w-14 h-14 rounded-2xl bg-emerald-100 text-emerald-600 flex items-center justify-center mb-6 shadow-sm">
                  <CheckCircle2 className="w-7 h-7" />
                </div>
                <div className="inline-block px-2.5 py-0.5 rounded text-[11px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 uppercase mb-3">
                  Pillar 3
                </div>
                <h3 className="text-xl font-black text-slate-900 mb-2">Progress & Ratings</h3>
                <p className="text-slate-600 text-sm leading-relaxed">
                  Toggle completion status with timestamps and submit 1–5 star ratings to feed adaptive recommendations.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
