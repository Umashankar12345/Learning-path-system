import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";
import {
  Trophy,
  Medal,
  Flame,
  Clock,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  Loader2,
  Crown,
  User,
  Compass,
} from "lucide-react";

export default function LeaderboardPage() {
  const [leaders, setLeaders] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const res = await api.get("/leaderboard/");
        setLeaders(res.data);
      } catch (err) {
        console.error("Failed to fetch leaderboard:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchLeaderboard();
  }, []);

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-slate-600 font-semibold text-base">Loading live database rankings...</p>
        </div>
      </div>
    );
  }

  const topThree = leaders.slice(0, 3);
  const remaining = leaders.slice(3);

  return (
    <div className="min-h-screen bg-slate-50/60 py-14 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-12">
        {/* Header */}
        <div className="text-center max-w-2xl mx-auto">
          <div className="inline-flex items-center gap-2 bg-amber-50 border border-amber-200 text-amber-700 px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider mb-4 shadow-sm">
            <Trophy className="w-4 h-4 text-amber-500" />
            Community Leaderboard & Achievements
          </div>
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 tracking-tight">
            Top Community Learners
          </h1>
          <p className="mt-3 text-base sm:text-lg text-slate-600">
            Real rankings computed from actual database completion logs and study hours.
          </p>
        </div>

        {/* Empty State when no one has completed an item yet */}
        {leaders.length === 0 ? (
          <div className="text-center py-20 px-4 bg-white rounded-3xl border-2 border-dashed border-slate-200 flex flex-col items-center justify-center shadow-sm">
            <div className="w-16 h-16 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center mb-4">
              <Trophy className="w-8 h-8" />
            </div>
            <h3 className="text-2xl font-black text-slate-900">
              No one has completed a module yet. Be the first!
            </h3>
            <p className="text-slate-600 text-sm mt-2 max-w-md mx-auto mb-6 leading-relaxed">
              Enroll in a skill pathway and mark your first resource complete to claim the #1 spot on the leaderboard.
            </p>
            <Link
              to="/skills"
              className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 transition-all shadow-md hover:shadow-indigo-500/25"
            >
              Start a Learning Path
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        ) : (
          <>
            {/* Dynamic Podium for Top 3 */}
            {topThree.length > 0 && (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 items-end pt-6">
                {/* 2nd Place */}
                {topThree[1] && (
                  <div className="bg-white rounded-3xl border border-slate-200 p-6 text-center order-2 sm:order-1 shadow-sm hover:shadow-md transition-all">
                    <div className="w-16 h-16 rounded-full bg-slate-100 border-4 border-slate-200 text-slate-600 flex items-center justify-center mx-auto mb-3 font-black text-xl shadow-inner">
                      🥈
                    </div>
                    <span className="inline-block px-2.5 py-0.5 rounded-full text-xs font-bold bg-slate-100 text-slate-700 mb-2">
                      Rank #{topThree[1].rank}
                    </span>
                    <h3 className="font-extrabold text-lg text-slate-900 truncate">
                      {topThree[1].name}
                    </h3>
                    <p className="text-xs text-slate-500">@{topThree[1].username}</p>
                    <div className="mt-4 pt-4 border-t border-slate-100 flex justify-center gap-4 text-xs font-bold text-slate-700">
                      <span>{topThree[1].hours_learned} hrs</span>
                      <span>•</span>
                      <span>{topThree[1].completed_count} done</span>
                    </div>
                  </div>
                )}

                {/* 1st Place */}
                {topThree[0] && (
                  <div className="bg-gradient-to-b from-amber-50 to-white rounded-3xl border-2 border-amber-300 p-8 text-center order-1 sm:order-2 shadow-xl sm:-translate-y-4 relative">
                    <div className="absolute -top-4 left-1/2 -translate-x-1/2 w-8 h-8 rounded-full bg-amber-400 text-white flex items-center justify-center shadow">
                      <Crown className="w-5 h-5 fill-white" />
                    </div>
                    <div className="w-20 h-20 rounded-full bg-amber-100 border-4 border-amber-300 text-amber-700 flex items-center justify-center mx-auto mb-3 font-black text-3xl shadow-inner">
                      🥇
                    </div>
                    <span className="inline-block px-3 py-1 rounded-full text-xs font-extrabold bg-amber-100 text-amber-800 mb-2 border border-amber-200">
                      Rank #{topThree[0].rank}
                    </span>
                    <h3 className="font-black text-xl text-slate-900 truncate">
                      {topThree[0].name}
                    </h3>
                    <p className="text-xs text-slate-500">@{topThree[0].username}</p>
                    <div className="mt-5 pt-4 border-t border-amber-100 flex justify-center gap-4 text-sm font-extrabold text-slate-800">
                      <span>{topThree[0].hours_learned} hrs learned</span>
                      <span>•</span>
                      <span>{topThree[0].completed_count} completed</span>
                    </div>
                  </div>
                )}

                {/* 3rd Place */}
                {topThree[2] && (
                  <div className="bg-white rounded-3xl border border-slate-200 p-6 text-center order-3 shadow-sm hover:shadow-md transition-all">
                    <div className="w-16 h-16 rounded-full bg-amber-50 border-4 border-amber-200 text-amber-700 flex items-center justify-center mx-auto mb-3 font-black text-xl shadow-inner">
                      🥉
                    </div>
                    <span className="inline-block px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-50 text-amber-800 mb-2">
                      Rank #{topThree[2].rank}
                    </span>
                    <h3 className="font-extrabold text-lg text-slate-900 truncate">
                      {topThree[2].name}
                    </h3>
                    <p className="text-xs text-slate-500">@{topThree[2].username}</p>
                    <div className="mt-4 pt-4 border-t border-slate-100 flex justify-center gap-4 text-xs font-bold text-slate-700">
                      <span>{topThree[2].hours_learned} hrs</span>
                      <span>•</span>
                      <span>{topThree[2].completed_count} done</span>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Detailed Leaderboard Table */}
            <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between">
                <h3 className="text-lg font-extrabold text-slate-900">Rankings Overview</h3>
                <span className="text-xs font-bold text-slate-500">Live from database</span>
              </div>

              <div className="divide-y divide-slate-100">
                {leaders.map((learner) => {
                  const isCurrentUser = user?.username === learner.username;
                  return (
                    <div
                      key={learner.id}
                      className={`p-5 flex items-center justify-between gap-4 transition-colors ${
                        isCurrentUser ? "bg-indigo-50/50" : "hover:bg-slate-50"
                      }`}
                    >
                      <div className="flex items-center gap-4 min-w-0">
                        <span className="w-8 text-center text-sm font-extrabold text-slate-500">
                          #{learner.rank}
                        </span>
                        <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-slate-700 font-bold text-sm">
                          {learner.username.slice(0, 2).toUpperCase()}
                        </div>
                        <div className="min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-slate-900 text-sm truncate">
                              {learner.name}
                            </span>
                            {isCurrentUser && (
                              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-100 text-indigo-700">
                                You
                              </span>
                            )}
                          </div>
                          <div className="flex flex-wrap items-center gap-1.5 mt-1">
                            {learner.badges.map((b) => (
                              <span
                                key={b.id}
                                className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-slate-100 text-slate-700 border border-slate-200"
                                title={b.name}
                              >
                                <span>{b.icon}</span>
                                <span>{b.name}</span>
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-6 text-right flex-shrink-0">
                        <div>
                          <span className="text-base font-extrabold text-slate-900">
                            {learner.hours_learned} hrs
                          </span>
                          <p className="text-[11px] text-slate-400 font-medium">Study Time</p>
                        </div>
                        <div className="hidden sm:block">
                          <span className="text-base font-extrabold text-slate-900">
                            {learner.completed_count}
                          </span>
                          <p className="text-[11px] text-slate-400 font-medium">Modules</p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
