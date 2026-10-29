import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../api/client";
import { useToast } from "../context/ToastContext";
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
  Code2,
  Loader2,
  Award,
  Sparkles,
} from "lucide-react";

export default function PathDetailPage() {
  const { id } = useParams();
  const [path, setPath] = useState(null);
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState(null);
  const [hoveredStars, setHoveredStars] = useState({});
  const toast = useToast();

  const fetchPath = async () => {
    try {
      const res = await api.get(`/paths/${id}/`);
      setPath(res.data);
    } catch (err) {
      console.error("Failed to fetch path:", err);
      toast.error("Could not load path details.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPath();
  }, [id]);

  const handleToggleComplete = async (item) => {
    setUpdatingId(item.id);
    const newStatus = !item.completed;
    try {
      await api.post(`/items/${item.id}/complete/`, {
        action: newStatus ? "complete" : "uncomplete",
      });

      if (newStatus) {
        toast.success(`Completed "${item.resource.title}" (+${item.resource.duration_minutes} min)`);
      } else {
        toast.info(`Marked "${item.resource.title}" as incomplete.`);
      }

      // Refresh path to update progress bar and stats
      await fetchPath();
    } catch (err) {
      console.error("Failed to toggle completion:", err);
      toast.error("Failed to update status. Please try again.");
    } finally {
      setUpdatingId(null);
    }
  };

  const handleRate = async (itemId, ratingValue) => {
    try {
      await api.post(`/items/${itemId}/rate/`, { rating: ratingValue });
      toast.success(`Rating recorded: ${ratingValue} / 5 stars`);
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
      toast.error("Unable to save rating.");
    }
  };

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-slate-600 font-semibold text-base">Loading course curriculum...</p>
        </div>
      </div>
    );
  }

  if (!path) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center bg-slate-50 text-center px-4">
        <div className="w-16 h-16 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center mb-4">
          <Award className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold text-slate-900">Learning Path Not Found</h2>
        <p className="text-slate-600 text-sm mt-2 mb-6 max-w-sm">
          This path may have been removed or you may not have permission to view it.
        </p>
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 shadow-md"
        >
          <ArrowLeft className="w-4 h-4" /> Return to Dashboard
        </Link>
      </div>
    );
  }

  const getTypeBadge = (type) => {
    switch (type) {
      case "video":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-purple-50 text-purple-700 border border-purple-200">
            <Video className="w-3.5 h-3.5" />
            Video Tutorial
          </span>
        );
      case "article":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-sky-50 text-sky-700 border border-sky-200">
            <FileText className="w-3.5 h-3.5" />
            Article Guide
          </span>
        );
      case "project":
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
            <Code2 className="w-3.5 h-3.5" />
            Hands-on Project
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200">
            <BookOpen className="w-3.5 h-3.5" />
            Structured Course
          </span>
        );
    }
  };

  const getDifficultyBadge = (difficulty) => {
    if (difficulty === 1) {
      return (
        <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
          Beginner (Level 1)
        </span>
      );
    }
    if (difficulty === 2) {
      return (
        <span className="px-3 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200">
          Intermediate (Level 2)
        </span>
      );
    }
    return (
      <span className="px-3 py-1 rounded-full text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200">
        Advanced (Level 3)
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-slate-50/60 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Navigation & Back Link */}
        <div className="flex items-center justify-between">
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-2 text-sm font-bold text-slate-600 hover:text-indigo-600 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
          <span className="text-xs font-semibold text-slate-400">
            Path ID #{path.id}
          </span>
        </div>

        {/* Hero Path Card with Centered Layout & Bold Typography */}
        <div className="bg-white rounded-3xl border border-slate-200 p-8 sm:p-10 shadow-sm">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6 mb-6">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-bold uppercase tracking-wider text-indigo-700 bg-indigo-50 px-3 py-1 rounded-full border border-indigo-200">
                  {path.skill.category}
                </span>
                {path.progress_percentage === 100 && (
                  <span className="text-xs font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Completed
                  </span>
                )}
              </div>
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 tracking-tight">
                {path.skill.name}
              </h1>
            </div>

            {/* Score Ring / Pill */}
            <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200 text-center min-w-[140px] self-start sm:self-auto">
              <span className="text-3xl sm:text-4xl font-black text-indigo-600">
                {path.progress_percentage}%
              </span>
              <p className="text-xs font-bold text-slate-500 mt-0.5">
                {path.completed_items} of {path.total_items} Finished
              </p>
            </div>
          </div>

          <p className="text-base sm:text-lg text-slate-600 leading-relaxed mb-8">
            {path.skill.description || "Master this domain through an ordered, difficulty-ranked curriculum."}
          </p>

          {/* Progress Bar with Gradient */}
          <div>
            <div className="flex items-center justify-between text-xs font-bold text-slate-500 mb-2">
              <span>Overall Roadmap Progress</span>
              <span>{Math.round(path.completed_duration_minutes / 60 * 10) / 10} / {Math.round(path.total_duration_minutes / 60 * 10) / 10} Hours Logged</span>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-3.5 overflow-hidden">
              <div
                className="bg-gradient-to-r from-indigo-600 to-violet-600 h-3.5 rounded-full transition-all duration-500 shadow-sm"
                style={{ width: `${path.progress_percentage}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Ordered Checklist Milestones */}
        <div className="space-y-4">
          <div className="flex items-center justify-between pb-2">
            <h2 className="text-xl sm:text-2xl font-black text-slate-900">
              Ordered Learning Milestones
            </h2>
            <span className="text-xs font-bold text-slate-500">
              Ranked Level 1 → 3
            </span>
          </div>

          {path.items.map((item, index) => {
            const isUpdating = updatingId === item.id;
            const currentHover = hoveredStars[item.id] || 0;
            const activeRating = currentHover || item.rating || 0;

            return (
              <div
                key={item.id}
                className={`bg-white rounded-2xl border p-6 sm:p-7 transition-all shadow-sm ${
                  item.completed
                    ? "border-emerald-200 bg-emerald-50/25"
                    : "border-slate-200 hover:border-indigo-200 hover:shadow-md"
                }`}
              >
                <div className="flex items-start gap-5">
                  {/* Complete Button */}
                  <button
                    onClick={() => handleToggleComplete(item)}
                    disabled={isUpdating}
                    className="mt-1 flex-shrink-0 focus:outline-none transition-transform hover:scale-110"
                    title={item.completed ? "Mark Incomplete" : "Mark Complete"}
                  >
                    {isUpdating ? (
                      <Loader2 className="w-7 h-7 animate-spin text-indigo-600" />
                    ) : item.completed ? (
                      <CheckCircle2 className="w-7 h-7 text-emerald-600 fill-emerald-100" />
                    ) : (
                      <Circle className="w-7 h-7 text-slate-300 hover:text-indigo-600 transition-colors" />
                    )}
                  </button>

                  {/* Main Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2.5 mb-2.5">
                      <span className="text-xs font-extrabold uppercase tracking-wider text-slate-400">
                        Step {index + 1}
                      </span>
                      {getTypeBadge(item.resource.resource_type)}
                      {getDifficultyBadge(item.resource.difficulty)}
                      {item.completed && (
                        <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
                          ✓ Done
                        </span>
                      )}
                      <span className="flex items-center gap-1 text-xs font-bold text-slate-500 ml-auto">
                        <Clock className="w-3.5 h-3.5" />
                        {item.resource.duration_minutes} min
                      </span>
                    </div>

                    <h3
                      className={`text-lg sm:text-xl font-extrabold mb-2 leading-snug ${
                        item.completed ? "text-slate-700 line-through decoration-slate-400" : "text-slate-900"
                      }`}
                    >
                      {item.resource.title}
                    </h3>

                    {item.resource.description && (
                      <p className="text-sm text-slate-600 mb-4 leading-relaxed">
                        {item.resource.description}
                      </p>
                    )}

                    {/* Action Bar: External Resource Link & Interactive Star Rating */}
                    <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-slate-100">
                      <a
                        href={item.resource.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 text-sm font-bold text-indigo-600 hover:text-indigo-700 hover:underline"
                      >
                        Access Resource Online
                        <ExternalLink className="w-4 h-4" />
                      </a>

                      {/* 5-Star Interactive Rating with Hover Feedback */}
                      <div className="flex items-center gap-2 bg-slate-50 px-3.5 py-1.5 rounded-xl border border-slate-200">
                        <span className="text-xs font-bold text-slate-600">
                          Your Rating:
                        </span>
                        <div
                          className="flex items-center gap-1"
                          onMouseLeave={() =>
                            setHoveredStars((prev) => ({ ...prev, [item.id]: 0 }))
                          }
                        >
                          {[1, 2, 3, 4, 5].map((star) => (
                            <button
                              key={star}
                              type="button"
                              onClick={() => handleRate(item.id, star)}
                              onMouseEnter={() =>
                                setHoveredStars((prev) => ({ ...prev, [item.id]: star }))
                              }
                              className="p-1 focus:outline-none transition-transform hover:scale-125"
                              title={`Rate ${star} star${star > 1 ? "s" : ""}`}
                            >
                              <Star
                                className={`w-5 h-5 transition-colors ${
                                  activeRating >= star
                                    ? "text-amber-400 fill-amber-400"
                                    : "text-slate-300"
                                }`}
                              />
                            </button>
                          ))}
                        </div>
                        {item.rating && (
                          <span className="text-xs font-extrabold text-slate-700 ml-1">
                            {item.rating}/5
                          </span>
                        )}
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
