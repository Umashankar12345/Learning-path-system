import React, { useEffect, useState } from "react";
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
  Code2,
  Clock3,
} from "lucide-react";
import api from "../api/client";

export default function LandingPage() {
  const { isAuthenticated } = useAuth();
  const [challenges, setChallenges] = useState([]);
  const [challengeError, setChallengeError] = useState("");

  useEffect(() => {
    api.get("/challenges/")
      .then((response) => setChallenges(response.data))
      .catch((error) => {
        console.error("Could not load challenge catalog:", error);
        setChallengeError("Challenge catalog is currently unavailable. Please try again later.");
      });
  }, []);

  return (
    <div className="landing-page min-h-screen">
      {/* Centered Hero Section */}
      <section className="home-hero relative overflow-hidden py-20 lg:py-28">
        <div className="home-hero-content relative z-10 max-w-4xl mx-auto px-4 sm:px-6 text-center space-y-6">
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
      <section className="home-feature-section py-20 border-y">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">
          <div className="text-center max-w-xl mx-auto mb-16">
            <h2 className="text-3xl sm:text-4xl font-black tracking-tight text-slate-900">
              Engineered for Maximum Retention
            </h2>
            <p className="mt-3 text-slate-600 text-base sm:text-lg">
              Everything you need to progress from foundational concepts to production-grade applications.
            </p>
          </div>

          <div className="home-feature-grid grid md:grid-cols-3 gap-8">
            {/* Pillar 1 */}
            <div className="home-feature-card p-8 rounded-3xl border flex flex-col justify-between">
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
            <div className="home-feature-card p-8 rounded-3xl border flex flex-col justify-between">
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
            <div className="home-feature-card p-8 rounded-3xl border flex flex-col justify-between">
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

      <section className="py-20 bg-gradient-to-br from-indigo-950 via-slate-900 to-violet-950 text-white">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-wrap items-end justify-between gap-5">
            <div>
              <span className="inline-flex items-center gap-2 rounded-full border border-indigo-300/30 bg-white/10 px-3 py-1.5 text-xs font-bold uppercase tracking-wider text-indigo-100">
                <Code2 className="h-4 w-4" />
                Live coding challenges
              </span>
              <h2 className="mt-4 text-3xl sm:text-4xl font-black tracking-tight">
                Practice with real test cases and a real judge.
              </h2>
              <p className="mt-3 max-w-2xl text-slate-300">
                Timed Python problems run against sample and hidden cases through the configured Judge0 service.
                Results are returned from code execution, not simulated.
              </p>
            </div>
            <Link
              to="/challenges"
              className="home-challenge-cta inline-flex items-center gap-2 rounded-xl px-5 py-3 text-sm font-bold transition"
            >
              Open Coding Arena <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

          {challengeError ? (
            <p role="alert" className="mt-7 rounded-xl border border-rose-300/30 bg-rose-400/10 p-4 text-sm text-rose-100">
              {challengeError}
            </p>
          ) : challenges.length === 0 ? (
            <p className="mt-7 text-sm text-slate-300">Loading the current challenge catalog…</p>
          ) : (
            <div className="mt-8 grid gap-4 sm:grid-cols-2">
              {challenges.slice(0, 3).map((challenge) => (
                <Link
                  key={challenge.id}
                  to="/challenges"
                  className="rounded-2xl border border-white/10 bg-white/5 p-5 transition hover:border-indigo-300/50 hover:bg-white/10"
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-bold">{challenge.title}</span>
                    <span className="rounded-full bg-indigo-300/15 px-2.5 py-1 text-[11px] font-bold capitalize text-indigo-100">
                      {challenge.difficulty}
                    </span>
                  </div>
                  <p className="mt-3 line-clamp-2 text-sm leading-relaxed text-slate-300">
                    {challenge.description}
                  </p>
                  <span className="mt-4 inline-flex items-center gap-1.5 text-xs font-semibold text-slate-300">
                    <Clock3 className="h-3.5 w-3.5" />
                    {challenge.duration_minutes} minutes
                    <span className="mx-1">·</span>
                    {challenge.test_case_count} test cases
                  </span>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
