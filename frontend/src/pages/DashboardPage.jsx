import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";
import {
  BookOpen,
  CheckCircle,
  Clock,
  Flame,
  ArrowRight,
  Sparkles,
  ExternalLink,
  PlusCircle,
  Loader2,
  TrendingUp,
} from "lucide-react";

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  const fetchDashboardData = async () => {
    try {
      const res = await api.get("/dashboard/stats/");
      setStats(res.data);
    } catch (err) {
      console.error("Failed to load dashboard metrics:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
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

  // Maximum hours for normalizing weekly chart bars
  const maxWeeklyHours = Math.max(...weekly_activity.map((d) => d.hours), 1);

  return (
    <div className="min-h-screen bg-slate-50 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Welcome Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              Hello, {user?.first_name || user?.username}! 👋
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              Here is your personalized learning progress tracked directly from the database.
            </p>
          </div>
          <Link
            to="/skills"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold shadow-sm transition-all self-start sm:self-auto"
          >
            <PlusCircle className="w-4 h-4" />
            Add New Goal
          </Link>
        </div>

        {/* 4 Stat Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          {/* Active Paths */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center flex-shrink-0">
              <BookOpen className="w-6 h-6" />
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Active Paths</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-0.5">{active_paths_count}</h3>
            </div>
          </div>

          {/* Completion Rate */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center flex-shrink-0">
              <CheckCircle className="w-6 h-6" />
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Completion</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-0.5">
                {overall_progress}% <span className="text-xs font-normal text-slate-500">({completed_items}/{total_items})</span>
              </h3>
            </div>
          </div>

          {/* Hours Learned */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center flex-shrink-0">
              <Clock className="w-6 h-6" />
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Hours Learned</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-0.5">{total_hours_learned} hrs</h3>
            </div>
          </div>

          {/* Day Streak */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center flex-shrink-0">
              <Flame className="w-6 h-6" />
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">Day Streak</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-0.5">{day_streak} {day_streak === 1 ? "day" : "days"}</h3>
            </div>
          </div>
        </div>

        {/* Action Center: Next Recommendation & Weekly Hours Activity */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Next Recommended Resource (AI / Rule-based) */}
          <div className="lg:col-span-1 bg-gradient-to-br from-indigo-900 to-slate-900 text-white rounded-2xl p-6 shadow-md flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 text-indigo-300 text-xs font-semibold uppercase tracking-wider mb-4">
                <Sparkles className="w-4 h-4 text-indigo-400" />
                Next Recommended Step
              </div>

              {next_recommended_item ? (
                <div>
                  <span className="inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/30 text-indigo-200 mb-3 border border-indigo-400/30 capitalize">
                    {next_recommended_item.resource.resource_type} • Level {next_recommended_item.resource.difficulty}
                  </span>
                  <h4 className="text-lg font-bold text-white leading-snug">
                    {next_recommended_item.resource.title}
                  </h4>
                  <p className="text-xs text-slate-300 mt-2 line-clamp-3">
                    {next_recommended_item.resource.description || "Continue this module to progress towards your skill mastery."}
                  </p>
                  <p className="text-xs text-indigo-200 mt-3 font-medium">
                    Duration: ~{next_recommended_item.resource.duration_minutes} mins
                  </p>
                </div>
              ) : (
                <div className="py-6 text-slate-300 text-sm">
                  {paths.length === 0
                    ? "You don't have any active learning paths yet. Choose a goal to start!"
                    : "Outstanding job! You have completed all recommended items across your paths."}
                </div>
              )}
            </div>

            <div className="mt-6 pt-4 border-t border-slate-700/60">
              {next_recommended_item ? (
                <div className="flex items-center justify-between gap-3">
                  <a
                    href={next_recommended_item.resource.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 px-3.5 py-2 rounded-xl transition-all shadow"
                  >
                    Open Resource
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                  <Link
                    to={`/paths/${next_recommended_item.path}`}
                    className="text-xs font-medium text-indigo-300 hover:text-white transition-colors"
                  >
                    View in Path →
                  </Link>
                </div>
              ) : (
                <Link
                  to="/skills"
                  className="inline-flex items-center gap-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 px-4 py-2 rounded-xl transition-all"
                >
                  Explore New Skills
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              )}
            </div>
          </div>

          {/* Weekly Hours Activity Chart */}
          <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-indigo-600" />
                  <h3 className="font-bold text-slate-900 text-base">Weekly Learning Hours (Last 7 Days)</h3>
                </div>
                <span className="text-xs font-medium text-slate-500">From database completion logs</span>
              </div>
              <p className="text-xs text-slate-500 mb-6">
                Hours calculated dynamically when items are marked completed.
              </p>
            </div>

            {/* Visual Bar Chart */}
            <div className="grid grid-cols-7 gap-2 sm:gap-4 items-end h-40 pt-4 border-b border-slate-200">
              {weekly_activity.map((dayData, idx) => {
                const heightPercent = maxWeeklyHours > 0 ? (dayData.hours / maxWeeklyHours) * 100 : 0;
                return (
                  <div key={idx} className="flex flex-col items-center gap-2 h-full justify-end group">
                    <span className="text-[10px] font-semibold text-slate-600 group-hover:text-indigo-600 transition-colors">
                      {dayData.hours > 0 ? `${dayData.hours}h` : "0"}
                    </span>
                    <div className="w-full max-w-[40px] bg-slate-100 rounded-t-lg h-28 relative flex items-end overflow-hidden">
                      <div
                        className="w-full bg-gradient-to-t from-indigo-600 to-violet-500 rounded-t-lg transition-all duration-500"
                        style={{ height: `${Math.max(heightPercent, dayData.hours > 0 ? 10 : 2)}%` }}
                      ></div>
                    </div>
                    <span className="text-xs font-semibold text-slate-500">{dayData.day}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Active Learning Paths List */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-bold text-slate-900">Your Learning Paths</h3>
              <p className="text-xs text-slate-500">Track and advance through your enrolled topics</p>
            </div>
          </div>

          {paths.length === 0 ? (
            <div className="text-center py-12 bg-slate-50 rounded-xl border border-dashed border-slate-300">
              <BookOpen className="w-10 h-10 text-slate-400 mx-auto mb-3" />
              <h4 className="text-slate-800 font-semibold text-sm">No learning paths started yet</h4>
              <p className="text-slate-500 text-xs mt-1 max-w-sm mx-auto mb-4">
                Choose a skill to generate a structured curriculum with difficulty-ranked milestones.
              </p>
              <Link
                to="/skills"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 transition-all shadow-sm"
              >
                Choose a Skill
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {paths.map((path) => (
                <div
                  key={path.id}
                  className="p-5 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-white hover:border-indigo-300 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-semibold text-indigo-600 bg-indigo-50 px-2.5 py-0.5 rounded-full border border-indigo-100">
                        {path.skill.category}
                      </span>
                    </div>
                    <h4 className="text-base font-bold text-slate-900">{path.skill.name}</h4>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {path.completed_items} of {path.total_items} modules completed • {Math.round(path.total_duration_minutes / 60)} hrs total
                    </p>

                    {/* Progress Bar */}
                    <div className="mt-3 w-full bg-slate-200 rounded-full h-2.5 overflow-hidden">
                      <div
                        className="bg-indigo-600 h-2.5 rounded-full transition-all duration-500"
                        style={{ width: `${path.progress_percentage}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 sm:self-center">
                    <span className="text-sm font-bold text-slate-700 min-w-[45px] text-right">
                      {path.progress_percentage}%
                    </span>
                    <Link
                      to={`/paths/${path.id}`}
                      className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 transition-colors shadow-sm"
                    >
                      Continue Path
                      <ArrowRight className="w-3.5 h-3.5" />
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
