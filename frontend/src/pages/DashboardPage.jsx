import React, { lazy, Suspense, useCallback, useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import DashboardSidebar from "../components/DashboardSidebar";
import PlacementQuizModal from "../components/PlacementQuizModal";
import {
  BookOpen,
  CalendarDays,
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
  Compass,
} from "lucide-react";

const SkillRadarChart = lazy(() => import("../components/SkillRadarChart"));

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [skillRadar, setSkillRadar] = useState([]);
  const [skillRadarError, setSkillRadarError] = useState("");
  const [dailyChallenge, setDailyChallenge] = useState(null);
  const [dailyChallengeError, setDailyChallengeError] = useState("");
  const [placementOpen, setPlacementOpen] = useState(false);
  const { user } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const fetchDashboardData = useCallback(async () => {
    try {
      const res = await api.get("/dashboard/stats/");
      setStats(res.data);
    } catch (err) {
      console.error("Failed to load dashboard metrics:", err);
      toast.error("Could not sync latest dashboard stats.");
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  useEffect(() => {
    let active = true;
    api.get("/analytics/skill-radar/")
      .then((response) => {
        if (active) {
          setSkillRadar(response.data);
          setSkillRadarError("");
        }
      })
      .catch((error) => {
        console.error("Could not load skill radar analytics:", error);
        if (active) setSkillRadarError("Skill radar analytics are unavailable right now.");
      });
    api.get("/arena/daily/")
      .then((response) => {
        if (active) {
          setDailyChallenge(response.data);
          setDailyChallengeError("");
        }
      })
      .catch((error) => {
        console.error("Could not load the daily coding challenge:", error);
        if (active) setDailyChallengeError("Today's coding challenge could not be loaded.");
      });
    return () => {
      active = false;
    };
  }, []);

  if (loading) {
    return (
      <div className="min-h-[75vh] flex flex-col items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-muted font-semibold text-base">Loading live dashboard metrics...</p>
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
    <div className="dashboard-theme min-h-screen">
      {/* 
        Professional Grid Shell:
        15rem fixed sidebar + minmax(0, 1fr) main content area.
      */}
      <div className="dashboard-shell">
        {/* Left Structure Sidebar (15rem) */}
        <DashboardSidebar
          activePaths={paths}
          streak={day_streak}
          hours={total_hours_learned}
        />

        {/* Main Content Area: Zero Minimum Shrinkage with min-w-0 */}
        <main className="min-w-0 space-y-8">
          {/* Header Bar with Flexbox & flex-wrap */}
          <header className="card p-6 sm:p-8 flex flex-wrap items-center justify-between gap-5">
            <div className="min-w-0">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold tag mb-2">
                <Compass className="w-3.5 h-3.5" />
                <span>Live Database Analytics</span>
              </div>
              <h1 className="text-2xl sm:text-3xl lg:text-4xl font-black tracking-tight">
                Welcome back, {user?.first_name || user?.username}!
              </h1>
              <p className="text-sm sm:text-base text-muted mt-1">
                Relational tracking of your modules, hours learned, and study consistency.
              </p>
            </div>

            <button
              type="button"
              onClick={() => setPlacementOpen(true)}
              className="btn-primary inline-flex items-center gap-2 px-5 py-3 text-sm font-bold shadow-md transition-all self-start sm:self-auto flex-shrink-0"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Enroll New Goal</span>
            </button>
          </header>

          {/* 4 KPI Stat Cards: Flexbox with Subtle Theme Shadows & Borders */}
          <section className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5">
            {/* Active Paths */}
            <div className="stat-card p-5 flex items-center gap-4">
              <div className="w-13 h-13 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center flex-shrink-0 shadow-inner">
                <BookOpen className="w-6 h-6" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-bold uppercase tracking-wider text-muted">Active Paths</p>
                <h3 className="text-2xl sm:text-3xl font-black mt-0.5">{active_paths_count}</h3>
                <span className="text-[11px] text-muted font-medium">Enrolled tracks</span>
              </div>
            </div>

            {/* Overall Progress */}
            <div className="stat-card p-5 flex items-center gap-4">
              <div className="w-13 h-13 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center flex-shrink-0 shadow-inner">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-bold uppercase tracking-wider text-muted">Completion</p>
                <h3 className="text-2xl sm:text-3xl font-black mt-0.5">
                  {overall_progress}%
                </h3>
                <span className="text-[11px] text-muted font-medium">{completed_items}/{total_items} modules</span>
              </div>
            </div>

            {/* Total Hours */}
            <div className="stat-card p-5 flex items-center gap-4">
              <div className="w-13 h-13 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center flex-shrink-0 shadow-inner">
                <Clock className="w-6 h-6" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-bold uppercase tracking-wider text-muted">Hours Learned</p>
                <h3 className="text-2xl sm:text-3xl font-black mt-0.5">
                  {total_hours_learned} <span className="text-sm font-semibold text-muted">hrs</span>
                </h3>
                <span className="text-[11px] text-muted font-medium">Logged study time</span>
              </div>
            </div>

            {/* Daily Streak */}
            <div className="stat-card p-5 flex items-center gap-4">
              <div className="w-13 h-13 rounded-2xl bg-amber-50 text-amber-500 flex items-center justify-center flex-shrink-0 shadow-inner">
                <Flame className="w-6 h-6 fill-amber-500" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-bold uppercase tracking-wider text-muted">Daily Streak</p>
                <h3 className="text-2xl sm:text-3xl font-black mt-0.5">
                  {day_streak} <span className="text-sm font-semibold text-muted">{day_streak === 1 ? "day" : "days"}</span>
                </h3>
                <span className="text-[11px] text-muted font-medium">Consecutive activity</span>
              </div>
            </div>
          </section>

          {/* Action Center: Two Columns with minmax(0, 1fr) */}
          <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Next Recommended Step Widget */}
            <div className="lg:col-span-1 bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white rounded-2xl p-6 sm:p-7 shadow-md flex flex-col justify-between border border-slate-800">
              <div>
                <div className="flex items-center gap-2 text-indigo-300 text-xs font-bold uppercase tracking-wider mb-4">
                  <Sparkles className="w-4 h-4 text-indigo-400" />
                  Next Recommended Milestone
                </div>

                {next_recommended_item ? (
                  <div>
                    <div className="flex flex-wrap items-center gap-2 mb-3">
                      <span className="px-2.5 py-0.5 rounded-md text-[11px] font-bold bg-indigo-500/30 text-indigo-200 border border-indigo-400/30 uppercase">
                        {next_recommended_item.resource.resource_type}
                      </span>
                      <span className="px-2.5 py-0.5 rounded-md text-[11px] font-bold bg-white/10 text-slate-200">
                        Level {next_recommended_item.resource.difficulty}
                      </span>
                    </div>
                    <h4 className="text-lg font-bold text-white leading-snug">
                      {next_recommended_item.resource.title}
                    </h4>
                    <p className="text-xs text-slate-300 mt-2 line-clamp-3 leading-relaxed">
                      {next_recommended_item.resource.description || "Advance through this module to build your portfolio competency."}
                    </p>
                    <div className="flex items-center gap-2 text-xs font-semibold text-indigo-300 mt-4">
                      <Clock className="w-3.5 h-3.5" />
                      <span>Duration: ~{next_recommended_item.resource.duration_minutes} mins</span>
                    </div>
                  </div>
                ) : (
                  <div className="py-8 text-center flex flex-col items-center">
                    <div className="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center text-indigo-300 mb-3">
                      <Award className="w-6 h-6" />
                    </div>
                    <h5 className="font-bold text-white text-base">All Caught Up!</h5>
                    <p className="text-xs text-slate-400 mt-1 max-w-xs leading-relaxed">
                      {paths.length === 0
                        ? "Enroll in a skill pathway to start receiving adaptive recommendations."
                        : "You've successfully completed all active milestones!"}
                    </p>
                  </div>
                )}
              </div>

              <div className="mt-6 pt-4 border-t border-slate-800">
                {next_recommended_item ? (
                  <div className="flex flex-wrap items-center justify-between gap-3">
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
                    className="w-full inline-flex items-center justify-center gap-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 py-2.5 rounded-xl transition-all"
                  >
                    Browse Skill Catalog
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                )}
              </div>
            </div>

            {/* Weekly Activity Hours Chart (.chart-card) */}
            <div className="lg:col-span-2 chart-card p-6 sm:p-7 flex flex-col justify-between">
              <div>
                <div className="flex flex-wrap items-center justify-between gap-3 mb-2">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-indigo-600" />
                    <h3 className="font-extrabold text-lg">Weekly Learning Activity</h3>
                  </div>
                  <span className="badge px-2.5 py-0.5 rounded-full text-[11px] font-bold">
                    Last 7 Days
                  </span>
                </div>
                <p className="text-xs text-muted mb-6">
                  Hours recorded dynamically when milestones are finished.
                </p>
              </div>

              {/* Responsive Bar Chart with .bar-track and .bar-fill */}
              <div className="grid grid-cols-7 gap-2 sm:gap-4 items-end h-40 pt-4 border-b border-[#dde3ec]">
                {weekly_activity.map((dayData, idx) => {
                  const heightPercent = maxWeeklyHours > 0 ? (dayData.hours / maxWeeklyHours) * 100 : 0;
                  return (
                    <div key={idx} className="flex flex-col items-center gap-2 h-full justify-end group min-w-0">
                      <span className="text-[11px] font-bold text-muted group-hover:text-indigo-600 transition-colors">
                        {dayData.hours > 0 ? `${dayData.hours}h` : "0"}
                      </span>
                      <div className="bar-track w-full max-w-[42px] rounded-t-xl h-28 relative flex items-end overflow-hidden">
                        <div
                          className="bar-fill w-full rounded-t-xl transition-all duration-500"
                          style={{ height: `${Math.max(heightPercent, dayData.hours > 0 ? 12 : 3)}%` }}
                        ></div>
                      </div>
                      <span className="text-xs font-bold text-muted">{dayData.day}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </section>

          <section className="grid grid-cols-1 gap-6 xl:grid-cols-3">
            <div className="chart-card min-w-0 p-6 sm:p-7 xl:col-span-2">
              <div className="mb-3 flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-indigo-300" />
                <div>
                  <h3 className="text-lg font-extrabold">Skill Radar</h3>
                  <p className="text-xs text-muted">Progress, study time, and placement scores by skill.</p>
                </div>
              </div>
              {skillRadarError ? (
                <p role="status" className="py-12 text-center text-sm text-rose-300">{skillRadarError}</p>
              ) : skillRadar.length ? (
                <div className="h-72 w-full">
                  <Suspense fallback={<div className="flex h-full items-center justify-center text-sm text-slate-400">Loading chart…</div>}>
                    <SkillRadarChart data={skillRadar} />
                  </Suspense>
                </div>
              ) : (
                <div className="flex h-72 items-center justify-center rounded-2xl border border-dashed border-slate-600/60 text-center text-sm text-slate-400">
                  Enroll in a skill path to start building your radar.
                </div>
              )}
            </div>

            <div className="flex flex-col justify-between rounded-2xl border border-indigo-400/20 bg-gradient-to-br from-indigo-950 via-slate-900 to-slate-950 p-6 shadow-xl shadow-indigo-950/20">
              <div>
                <div className="flex items-center justify-between">
                  <span className="inline-flex items-center gap-2 rounded-full bg-indigo-400/10 px-3 py-1 text-xs font-bold uppercase tracking-wider text-indigo-200">
                    <CalendarDays className="h-4 w-4" /> Daily Challenge
                  </span>
                  <span className="inline-flex items-center gap-1 text-sm font-bold text-amber-300">
                    <Flame className="h-4 w-4 fill-amber-300" />
                    {dailyChallenge?.coding_streak ?? 0}
                  </span>
                </div>
                {dailyChallengeError ? (
                  <p role="status" className="mt-6 text-sm text-rose-300">{dailyChallengeError}</p>
                ) : dailyChallenge ? (
                  <>
                    <p className="mt-6 text-xs font-semibold text-slate-400">
                      {dailyChallenge.completed_today ? "Completed today" : "Ready when you are"}
                    </p>
                    <h3 className="mt-2 text-xl font-black text-white">
                      {dailyChallenge.challenge.title}
                    </h3>
                    <p className="mt-2 line-clamp-3 text-sm leading-relaxed text-slate-300">
                      {dailyChallenge.challenge.description}
                    </p>
                    <div className="mt-4 flex flex-wrap gap-2">
                      <span className="rounded-full bg-indigo-400/10 px-3 py-1 text-xs font-bold capitalize text-indigo-200">
                        {dailyChallenge.challenge.difficulty}
                      </span>
                      {dailyChallenge.challenge.topic_tags.map((tag) => (
                        <span key={tag} className="rounded-full bg-slate-700/70 px-3 py-1 text-xs font-semibold text-slate-300">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </>
                ) : (
                  <p className="mt-6 text-sm text-slate-400">Loading today's challenge…</p>
                )}
              </div>
              {dailyChallenge && (
                <Link
                  to={`/challenges?problem=${dailyChallenge.challenge.id}`}
                  className="mt-6 inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-500 px-4 py-3 text-sm font-bold text-white transition hover:bg-indigo-400"
                >
                  {dailyChallenge.completed_today ? "Practice again" : "Take the challenge"}
                  <ArrowRight className="h-4 w-4" />
                </Link>
              )}
            </div>
          </section>

          {/* Enrolled Learning Paths Section (.panel) */}
          <section className="panel p-6 sm:p-8">
            <div className="flex flex-wrap items-center justify-between gap-4 mb-6 pb-4 border-b border-[#dde3ec]">
              <div>
                <h3 className="text-xl sm:text-2xl font-black">Enrolled Learning Paths</h3>
                <p className="text-xs sm:text-sm text-muted mt-0.5">
                  Advance through each sequence to reach 100% and claim your certificate
                </p>
              </div>
              {paths.length > 0 && (
                <span className="badge px-3 py-1 rounded-full text-xs font-bold">
                  {paths.length} {paths.length === 1 ? "Path" : "Paths"} Active
                </span>
              )}
            </div>

            {/* Empty State when zero paths */}
            {paths.length === 0 ? (
              <div className="text-center py-14 px-4 bg-slate-50/70 rounded-2xl border-2 border-dashed border-[#dde3ec] flex flex-col items-center justify-center">
                <div className="w-14 h-14 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-4 shadow-sm">
                  <BookOpen className="w-7 h-7" />
                </div>
                <h4 className="text-lg font-bold">No Learning Paths Started Yet</h4>
                <p className="text-muted text-xs sm:text-sm mt-1.5 max-w-sm mx-auto mb-5 leading-relaxed">
                  Choose a skill goal to generate an ordered, difficulty-ranked curriculum with articles, videos, and projects.
                </p>
                <Link
                  to="/skills"
                  className="btn-primary inline-flex items-center gap-2 px-5 py-2.5 text-xs font-bold shadow-sm"
                >
                  Choose Your First Skill
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {paths.map((path) => (
                  <div
                    key={path.id}
                    className="path-card p-5 sm:p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-5"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-2.5 mb-2">
                        <span className="tag px-2.5 py-0.5 rounded-md text-xs font-bold">
                          {path.skill.category}
                        </span>
                        {path.progress_percentage === 100 ? (
                          <span className="px-2.5 py-0.5 rounded-md text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            Completed
                          </span>
                        ) : (
                          <span className="badge-progress px-2.5 py-0.5 rounded-md text-xs font-bold">
                            In Progress
                          </span>
                        )}
                      </div>

                      <h4 className="text-lg font-extrabold truncate">{path.skill.name}</h4>
                      <p className="text-xs font-medium text-muted mt-1">
                        {path.completed_items} of {path.total_items} modules finished • ~{Math.round(path.total_duration_minutes / 60)} hrs syllabus
                      </p>

                      {/* Progress Bar with .progress and .progress-bar */}
                      <div className="progress mt-3.5 w-full h-2.5 overflow-hidden">
                        <div
                          className="progress-bar h-2.5 transition-all duration-500"
                          style={{ width: `${path.progress_percentage}%` }}
                        ></div>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 sm:self-center flex-shrink-0">
                      <div className="text-right">
                        <span className="text-xl font-black">
                          {path.progress_percentage}%
                        </span>
                        <p className="text-[10px] font-bold text-muted uppercase">Score</p>
                      </div>
                      <Link
                        to={`/paths/${path.id}`}
                        className="btn-primary inline-flex items-center gap-1.5 px-4 py-2.5 text-xs font-bold"
                      >
                        <span>Continue</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </main>
      </div>
      {placementOpen && (
        <PlacementQuizModal
          onClose={() => setPlacementOpen(false)}
          onComplete={(pathId) => navigate(`/paths/${pathId}`)}
        />
      )}
    </div>
  );
}
