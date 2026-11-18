import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import PlacementQuizModal from "../components/PlacementQuizModal";
import {
  BookOpen,
  Sparkles,
  ArrowRight,
  Layers,
  Clock,
  CheckCircle2,
  Loader2,
  Compass,
  GraduationCap,
} from "lucide-react";

export default function SkillsPage() {
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [placementSkill, setPlacementSkill] = useState(null);
  const [activeCategory, setActiveCategory] = useState("All");
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  useEffect(() => {
    const fetchSkills = async () => {
      try {
        const res = await api.get("/skills/");
        setSkills(res.data);
      } catch (err) {
        console.error("Failed to load skills:", err);
        toast.error("Failed to load skills catalog.");
      } finally {
        setLoading(false);
      }
    };
    fetchSkills();
  }, []);

  const handleStartPath = (skill) => {
    if (!isAuthenticated) {
      toast.info("Please log in or sign up to create your learning path.");
      navigate("/login");
      return;
    }
    setPlacementSkill(skill);
  };

  const categories = ["All", ...new Set(skills.map((skill) => skill.category))];
  const visibleSkills =
    activeCategory === "All"
      ? skills
      : skills.filter((skill) => skill.category === activeCategory);

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-slate-600 font-semibold text-base">Loading skill pathways...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="skills-page min-h-screen py-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto space-y-12">
        {/* Centered Hero Header */}
        <div className="text-center max-w-2xl mx-auto">
          <div className="inline-flex items-center gap-2 bg-indigo-50 border border-indigo-200 text-indigo-700 px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider mb-4 shadow-sm">
            <Sparkles className="w-3.5 h-3.5" />
            Curated Skill Catalogs
          </div>
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 tracking-tight">
            Choose Your Learning Goal
          </h1>
          <p className="mt-3 text-base sm:text-lg text-slate-600 leading-relaxed">
            Select a target discipline to generate a personalized, difficulty-ranked learning path populated with courses, articles, and hands-on projects.
          </p>
        </div>

        {/* Empty State */}
        {skills.length === 0 ? (
          <div className="text-center py-16 px-4 bg-white rounded-3xl border-2 border-dashed border-slate-200 flex flex-col items-center justify-center">
            <div className="w-16 h-16 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-4">
              <Compass className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-bold text-slate-900">No Skills Found</h3>
            <p className="text-slate-500 text-sm mt-1 max-w-sm">
              Please run the database seed script (<code className="text-xs bg-slate-100 px-1 py-0.5 rounded">python seed_data.py</code>) to load the catalog.
            </p>
          </div>
        ) : (
          <>
            <div
              className="flex flex-wrap justify-center gap-2"
              role="group"
              aria-label="Filter skills by category"
            >
              {categories.map((category) => {
                const isActive = activeCategory === category;
                return (
                  <button
                    key={category}
                    type="button"
                    aria-pressed={isActive}
                    onClick={() => setActiveCategory(category)}
                    className={`rounded-full border px-4 py-2 text-sm font-bold transition ${
                      isActive
                        ? "border-indigo-600 bg-indigo-600 text-white shadow-sm"
                        : "border-slate-200 bg-white text-slate-600 hover:border-indigo-300 hover:text-indigo-700"
                    }`}
                  >
                    {category}
                  </button>
                );
              })}
            </div>
            <div className="skills-grid grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {visibleSkills.map((skill) => (
              <div
                key={skill.id}
                className="skill-card rounded-3xl border p-7 flex flex-col justify-between group"
              >
                <div>
                  <div className="flex flex-wrap items-center gap-2 mb-4">
                    <span className="px-3 py-1 rounded-full text-xs font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
                      {skill.category}
                    </span>
                    <span className="px-3 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-600">
                      {skill.resource_count} Modules
                    </span>
                  </div>

                  <h3 className="text-xl font-black text-slate-900 mb-3 group-hover:text-indigo-600 transition-colors">
                    {skill.name}
                  </h3>

                  <p className="text-slate-600 text-sm leading-relaxed mb-6">
                    {skill.description || "Structured modular curriculum designed to guide you from fundamentals to production mastery."}
                  </p>
                </div>

                <div className="pt-5 border-t border-slate-100 flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-slate-500">
                    <GraduationCap className="w-4 h-4 text-indigo-500" />
                    <span>Ranked 1 → 3</span>
                  </div>

                  <button
                    onClick={() => handleStartPath(skill)}
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 transition-all shadow-sm"
                  >
                    Find my level
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
            </div>
          </>
        )}
      </div>
      {placementSkill && (
        <PlacementQuizModal
          initialSkill={placementSkill}
          onClose={() => setPlacementSkill(null)}
          onComplete={(pathId) => navigate(`/paths/${pathId}`)}
        />
      )}
    </div>
  );
}
