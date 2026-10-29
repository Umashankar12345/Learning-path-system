import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../api/client";
import {
  ArrowLeft,
  CheckCircle2,
  Circle,
  ExternalLink,
  Star,
  Clock,
  BookOpen,
  Video,
  FileText,
  Code,
  Loader2,
  Award,
} from "lucide-react";

export default function PathDetailPage() {
  const { id } = useParams();
  const [path, setPath] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState(null);

  const fetchPath = async () => {
    try {
      const res = await api.get(`/paths/${id}/`);
      setPath(res.data);
    } catch (err) {
      console.error("Failed to fetch path:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPath();
  }, [id]);

  const handleToggleComplete = async (item) => {
    setUpdatingId(item.id);
    try {
      await api.post(`/items/${item.id}/complete/`, {
        action: item.completed ? "uncomplete" : "complete",
      });
      // Refresh path to update progress bar and state
      await fetchPath();
    } catch (err) {
      console.error("Failed to toggle completion:", err);
    } finally {
      setUpdatingId(null);
    }
  };

  const handleRate = async (itemId, ratingValue) => {
    try {
      await api.post(`/items/${itemId}/rate/`, { rating: ratingValue });
      // Update local state smoothly
      setPath((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          items: prev.items.map((it) =>
            it.id === itemId ? { ...it, rating: ratingValue } : it
          ),
        };
      });
    } catch (err) {
      console.error("Failed to rate item:", err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  if (!path) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 text-center px-4">
        <h2 className="text-xl font-bold text-slate-900">Learning path not found</h2>
        <p className="text-slate-600 text-sm mt-2 mb-4">
          This path may have been removed or you may not have permission to view it.
        </p>
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 text-indigo-600 font-semibold text-sm hover:underline"
        >
          <ArrowLeft className="w-4 h-4" /> Return to Dashboard
        </Link>
      </div>
    );
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case "video":
        return <Video className="w-4 h-4 text-rose-500" />;
      case "article":
        return <FileText className="w-4 h-4 text-emerald-500" />;
      case "project":
        return <Code className="w-4 h-4 text-indigo-500" />;
      default:
        return <BookOpen className="w-4 h-4 text-blue-500" />;
    }
  };

  const getDifficultyBadge = (difficulty) => {
    if (difficulty === 1) {
      return (
        <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
          Beginner
        </span>
      );
    }
    if (difficulty === 2) {
      return (
        <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-50 text-amber-700 border border-amber-200">
          Intermediate
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-rose-50 text-rose-700 border border-rose-200">
        Advanced
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-slate-50 py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Top Navigation */}
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 hover:text-indigo-600 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </Link>

        {/* Path Hero Card */}
        <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-md border border-indigo-100">
                {path.skill.category}
              </span>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 mt-2 tracking-tight">
                {path.skill.name}
              </h1>
            </div>
            <div className="text-right">
              <span className="text-3xl font-extrabold text-indigo-600">
                {path.progress_percentage}%
              </span>
              <p className="text-xs text-slate-500">
                {path.completed_items} of {path.total_items} Completed
              </p>
            </div>
          </div>

          <p className="text-slate-600 text-sm leading-relaxed mb-6">
            {path.skill.description || "Master this domain through an ordered, difficulty-ranked curriculum."}
          </p>

          {/* Progress Bar */}
          <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
            <div
              className="bg-indigo-600 h-3 rounded-full transition-all duration-500"
              style={{ width: `${path.progress_percentage}%` }}
            ></div>
          </div>
        </div>

        {/* Ordered Checklist Items */}
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-slate-900">
            Curated Learning Sequence (Ranked by Difficulty)
          </h2>

          {path.items.map((item, index) => {
            const isUpdating = updatingId === item.id;
            return (
              <div
                key={item.id}
                className={`bg-white rounded-2xl border p-5 sm:p-6 transition-all shadow-sm ${
                  item.completed
                    ? "border-emerald-200 bg-emerald-50/20"
                    : "border-slate-200 hover:border-slate-300"
                }`}
              >
                <div className="flex items-start gap-4">
                  {/* Complete Checkbox Button */}
                  <button
                    onClick={() => handleToggleComplete(item)}
                    disabled={isUpdating}
                    className="mt-1 flex-shrink-0 focus:outline-none"
                    title={item.completed ? "Mark Incomplete" : "Mark Complete"}
                  >
                    {isUpdating ? (
                      <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
                    ) : item.completed ? (
                      <CheckCircle2 className="w-6 h-6 text-emerald-600 fill-emerald-100" />
                    ) : (
                      <Circle className="w-6 h-6 text-slate-300 hover:text-indigo-600 transition-colors" />
                    )}
                  </button>

                  {/* Item Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 mb-2">
                      <span className="text-xs font-bold text-slate-500">
                        Step {index + 1}
                      </span>
                      <div className="flex items-center gap-1 text-xs text-slate-600 bg-slate-100 px-2 py-0.5 rounded capitalize">
                        {getTypeIcon(item.resource.resource_type)}
                        <span>{item.resource.resource_type}</span>
                      </div>
                      {getDifficultyBadge(item.resource.difficulty)}
                      <span className="flex items-center gap-1 text-xs text-slate-500 ml-auto">
                        <Clock className="w-3.5 h-3.5" />
                        {item.resource.duration_minutes} min
                      </span>
                    </div>

                    <h3
                      className={`text-base font-bold mb-1.5 ${
                        item.completed ? "text-slate-700 line-through" : "text-slate-900"
                      }`}
                    >
                      {item.resource.title}
                    </h3>

                    {item.resource.description && (
                      <p className="text-xs text-slate-600 mb-3 leading-relaxed">
                        {item.resource.description}
                      </p>
                    )}

                    {/* Bottom Action Bar */}
                    <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-100">
                      {/* External Link */}
                      <a
                        href={item.resource.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-600 hover:text-indigo-700 hover:underline"
                      >
                        Access Resource
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>

                      {/* 5-Star Rating Component */}
                      <div className="flex items-center gap-1">
                        <span className="text-[11px] font-medium text-slate-500 mr-1">
                          Rating:
                        </span>
                        {[1, 2, 3, 4, 5].map((star) => (
                          <button
                            key={star}
                            onClick={() => handleRate(item.id, star)}
                            className="p-0.5 focus:outline-none transition-transform hover:scale-110"
                            title={`Rate ${star} star${star > 1 ? "s" : ""}`}
                          >
                            <Star
                              className={`w-4 h-4 ${
                                (item.rating || 0) >= star
                                  ? "text-amber-400 fill-amber-400"
                                  : "text-slate-300"
                              }`}
                            />
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
