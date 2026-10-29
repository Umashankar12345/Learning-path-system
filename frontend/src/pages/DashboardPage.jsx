import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import {
  BookOpen,
  CheckCircle2,
  Clock,
  Flame,
  ArrowRight,
  Sparkles,
  ExternalLink,
  PlusCircle,
  Loader2,
  TrendingUp,
  Award,
  Layers,
  Compass,
} from "lucide-react";

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();
  const toast = useToast();

  const fetchDashboardData = async () => {
    try {
      const res = await api.get("/dashboard/stats/");
      setStats(res.data);
    } catch (err) {
      console.error("Failed to load dashboard metrics:", err);
      toast.error("Could not sync latest dashboard stats.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-slate-600 font-semibold text-base">Loading your learning metrics...</p>
        </div>
      </div>
    );
  }

  const {
    active_paths_count = 0,
    total_items = 0,
    completed_items = 0,
    overall_progress = 0,
    total_hours_learned = 0,
    day_streak = 0,
    next_recommended_item,
    weekly_activity = [],
    paths = [],
  } = stats || {};

  const maxWeeklyHours = Math.max(...weekly_activity.map((d) => d.hours), 1);

  return (
    <div className="min-h-screen bg-slate-50/60 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-10">
        {/* Centered Welcome Banner */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6 pb-6 border-b border-slate-200">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200 mb-3">
              <Compass className="w-3.5 h-3.5" />
              Learner Dashboard
            </div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 tracking-tight">
              Welcome back, {user?.first_name || user?.username}!
            </h1>
            <p className="text-base sm:text-lg text-slate-600 mt-2">
              All learning hours, completions, and recommendations computed directly from your database.
            </p>
          </div>
          <Link
            to="/skills"
            className="inline-flex items-center justify-center gap-2 px-5 py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-base font-bold shadow-md hover:shadow-indigo-500/20 transition-all self-start md:self-auto"
          >
            <PlusCircle className="w-5 h-5" />
            Explore New Goal
          </Link>
        </div>

        {/* 4 Stat Overview Cards with Larger Fonts */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Active Paths */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-indigo-200 transition-all flex items-center gap-5">
            <div className="w-14 h-14 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center flex-shrink-0 shadow-inner">
              <BookOpen className="w-7 h-7" />
            </div>
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Active Paths</p>
              <h3 className="text-3xl sm:text-4xl font-black text-slate-900 mt-1">{active_paths_count}</h3>
            </div>
          </div>

          {/* Completion Rate */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-emerald-200 transition-all flex items-center gap-5">
            <div className="w-14 h-14 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center flex-shrink-0 shadow-inner">
              <CheckCircle2 className="w-7 h-7" />
            </div>
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Progress</p>
              <h3 className="text-3xl sm:text-4xl font-black text-slate-900 mt-1">
                {overall_progress}%
              </h3>
              <span className="text-xs font-semibold text-slate-500">{completed_items}/{total_items} items done</span>
            </div>
          </div>

          {/* Hours Learned */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-blue-200 transition-all flex items-center gap-5">
            <div className="w-14 h-14 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center flex-shrink-0 shadow-inner">
              <Clock className="w-7 h-7" />
            </div>
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Hours Learned</p>
              <h3 className="text-3xl sm:text-4xl font-black text-slate-900 mt-1">
                {total_hours_learned} <span className="text-base font-semibold text-slate-500">hrs</span>
              </h3>
            </div>
          </div>

          {/* Day Streak */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:border-amber-200 transition-all flex items-center gap-5">
            <div className="w-14 h-14 rounded-2xl bg-amber-50 text-amber-500 flex items-center justify-center flex-shrink-0 shadow-inner">
              <Flame className="w-7 h-7" />
            </div>
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Daily Streak</p>
              <h3 className="text-3xl sm:text-4xl font-black text-slate-900 mt-1">
                {day_streak} <span className="text-base font-semibold text-slate-500">{day_streak === 1 ? "day" : "days"}</span>
              </h3>
            </div>
          </div>
        </div>

        {/* Action Center: Next Recommendation & Weekly Hours Activity */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Next Recommended Resource */}
          <div className="lg:col-span-1 bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white rounded-2xl p-7 shadow-lg flex flex-col justify-between border border-slate-800">
            <div>
              <div className="flex items-center gap-2 text-indigo-300 text-xs font-bold uppercase tracking-wider mb-4">
                <Sparkles className="w-4 h-4 text-indigo-400" />
                Next Up For You
              </div>

              {next_recommended_item ? (
                <div>
                  <div className="flex flex-wrap items-center gap-2 mb-3">
                    <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-indigo-500/20 text-indigo-200 border border-indigo-400/30 uppercase">
                      {next_recommended_item.resource.resource_type}
                    </span>
                    <span className="px-2.5 py-1 rounded-md text-xs font-bold bg-white/10 text-slate-200">
                      Level {next_recommended_item.resource.difficulty}
                    </span>
                  </div>
                  <h4 className="text-xl font-extrabold text-white leading-snug">
                    {next_recommended_item.resource.title}
                  </h4>
                  <p className="text-sm text-slate-300 mt-2.5 line-clamp-3">
                    {next_recommended_item.resource.description || "Continue this module to steadily increase your mastery score."}
                  </p>
                  <div className="flex items-center gap-2 text-xs font-semibold text-indigo-300 mt-4">
                    <Clock className="w-4 h-4" />
                    Estimated time: ~{next_recommended_item.resource.duration_minutes} minutes
                  </div>
                </div>
              ) : (
                /* Empty state for next recommended item */
                <div className="py-8 text-center flex flex-col items-center">
                  <div className="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center text-indigo-300 mb-3">
                    <Award className="w-6 h-6" />
                  </div>
                  <h5 className="font-bold text-white text-base">All Caught Up!</h5>
                  <p className="text-xs text-slate-400 mt-1 max-w-xs leading-relaxed">
                    {paths.length === 0
                      ? "Enroll in a skill path to start receiving recommendations."
                      : "You've successfully completed all active milestones!"}
                  </p>
                </div>
              )}
            </div>

            <div className="mt-8 pt-5 border-t border-slate-800">
              {next_recommended_item ? (
                <div className="flex items-center justify-between gap-3">
                  <a
                    href={next_recommended_item.resource.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 px-4 py-2.5 rounded-xl transition-all shadow"
                  >
                    Open Resource
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                  <Link
                    to={`/paths/${next_recommended_item.path}`}
                    className="text-xs font-bold text-indigo-300 hover:text-white transition-colors"
                  >
                    View in Path →
                  </Link>
                </div>
              ) : (
                <Link
                  to="/skills"
                  className="w-full inline-flex items-center justify-center gap-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 py-3 rounded-xl transition-all"
                >
                  Browse Skill Catalog
                  <ArrowRight className="w-4 h-4" />
                </Link>
              )}
            </div>
          </div>

          {/* Weekly Hours Activity Chart */}
          <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-7 shadow-sm flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2.5">
                  <TrendingUp className="w-5 h-5 text-indigo-600" />
                  <h3 className="font-extrabold text-slate-900 text-lg">Weekly Activity (Last 7 Days)</h3>
                </div>
                <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-slate-100 text-slate-600">
                  Live DB Queries
                </span>
              </div>
              <p className="text-sm text-slate-500 mb-6">
                Hours calculated in real-time as you complete course milestones.
              </p>
            </div>

            {/* Visual Bar Chart */}
            <div className="grid grid-cols-7 gap-3 sm:gap-5 items-end h-44 pt-4 border-b border-slate-200">
              {weekly_activity.map((dayData, idx) => {
                const heightPercent = maxWeeklyHours > 0 ? (dayData.hours / maxWeeklyHours) * 100 : 0;
                return (
                  <div key={idx} className="flex flex-col items-center gap-2.5 h-full justify-end group">
                    <span className="text-xs font-bold text-slate-600 group-hover:text-indigo-600 transition-colors">
                      {dayData.hours > 0 ? `${dayData.hours}h` : "0"}
                    </span>
                    <div className="w-full max-w-[44px] bg-slate-100 rounded-t-xl h-32 relative flex items-end overflow-hidden group-hover:bg-slate-200 transition-colors">
                      <div
                        className="w-full bg-gradient-to-t from-indigo-600 to-violet-500 rounded-t-xl transition-all duration-500 shadow-sm"
                        style={{ height: `${Math.max(heightPercent, dayData.hours > 0 ? 12 : 3)}%` }}
                      ></div>
                    </div>
                    <span className="text-xs font-bold text-slate-600">{dayData.day}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Active Learning Paths Section */}
        <div className="bg-white rounded-2xl border border-slate-200 p-7 sm:p-8 shadow-sm">
          <div className="flex items-center justify-between mb-8 pb-4 border-b border-slate-100">
            <div>
              <h3 className="text-2xl font-black text-slate-900">Your Enrolled Paths</h3>
              <p className="text-sm text-slate-500 mt-0.5">Click any path to continue your sequence or rate modules</p>
            </div>
            {paths.length > 0 && (
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-700">
                {paths.length} Active {paths.length === 1 ? "Path" : "Paths"}
              </span>
            )}
          </div>

          {/* Empty State when zero paths */}
          {paths.length === 0 ? (
            <div className="text-center py-16 px-4 bg-slate-50/70 rounded-2xl border-2 border-dashed border-slate-200 flex flex-col items-center justify-center">
              <div className="w-16 h-16 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-4 shadow-sm">
                <BookOpen className="w-8 h-8" />
              </div>
              <h4 className="text-xl font-bold text-slate-900">No Learning Paths Started Yet</h4>
              <p className="text-slate-600 text-sm mt-2 max-w-md mx-auto mb-6 leading-relaxed">
                Choose a skill to generate an ordered, difficulty-ranked curriculum with articles, videos, and hands-on projects.
              </p>
              <Link
                to="/skills"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 transition-all shadow-md hover:shadow-indigo-500/25"
              >
                Choose Your First Skill
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          ) : (
            <div className="space-y-5">
              {paths.map((path) => (
                <div
                  key={path.id}
                  className="p-6 rounded-2xl border border-slate-200 bg-slate-50/40 hover:bg-white hover:border-indigo-300 hover:shadow-md transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-6"
                >
                  <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-2.5 mb-2">
                      <span className="text-xs font-bold text-indigo-700 bg-indigo-50 px-2.5 py-0.5 rounded-md border border-indigo-200">
                        {path.skill.category}
                      </span>
                      {path.progress_percentage === 100 ? (
                        <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-md border border-emerald-200 flex items-center gap-1">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          Completed
                        </span>
                      ) : (
                        <span className="text-xs font-bold text-amber-700 bg-amber-50 px-2.5 py-0.5 rounded-md border border-amber-200">
                          In Progress
                        </span>
                      )}
                    </div>
                    <h4 className="text-xl font-extrabold text-slate-900">{path.skill.name}</h4>
                    <p className="text-xs sm:text-sm font-medium text-slate-500 mt-1">
                      {path.completed_items} of {path.total_items} items finished • ~{Math.round(path.total_duration_minutes / 60)} hrs total syllabus
                    </p>

                    {/* Progress Bar with rounded ends */}
                    <div className="mt-4 w-full bg-slate-200 rounded-full h-3 overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-indigo-600 to-violet-600 h-3 rounded-full transition-all duration-500"
                        style={{ width: `${path.progress_percentage}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="flex items-center gap-5 sm:self-center">
                    <div className="text-right">
                      <span className="text-2xl font-black text-slate-900">
                        {path.progress_percentage}%
                      </span>
                      <p className="text-[11px] font-bold text-slate-400 uppercase">Score</p>
                    </div>
                    <Link
                      to={`/paths/${path.id}`}
                      className="inline-flex items-center gap-2 px-5 py-3 rounded-xl text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 transition-colors shadow-sm"
                    >
                      Continue
                      <ArrowRight className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
