import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";
import { BookOpen, Sparkles, ArrowRight, Layers, Clock, CheckCircle2, Loader2 } from "lucide-react";

export default function SkillsPage() {
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creatingId, setCreatingId] = useState(null);
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSkills = async () => {
      try {
        const res = await api.get("/skills/");
        setSkills(res.data);
      } catch (err) {
        console.error("Failed to load skills:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchSkills();
  }, []);

  const handleStartPath = async (skillId) => {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }

    setCreatingId(skillId);
    try {
      const res = await api.post("/paths/", { skill_id: skillId });
      navigate(`/paths/${res.data.id}`);
    } catch (err) {
      console.error("Failed to generate path:", err);
      alert("Unable to generate path. Please try again.");
    } finally {
      setCreatingId(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <div className="inline-flex items-center gap-2 bg-indigo-50 border border-indigo-200 text-indigo-700 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider mb-4">
            <Sparkles className="w-3.5 h-3.5" />
            Curated Skill Catalogs
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
            Select Your Target Skill
          </h1>
          <p className="mt-3 text-slate-600">
            Choose a subject to generate a personalized, difficulty-ranked learning path populated with courses, articles, and capstone projects.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {skills.map((skill) => (
            <div
              key={skill.id}
              className="bg-white rounded-2xl border border-slate-200 p-6 flex flex-col justify-between hover:shadow-md hover:border-indigo-300 transition-all"
            >
              <div>
                <div className="inline-block px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-100 text-slate-700 mb-4">
                  {skill.category}
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">{skill.name}</h3>
                <p className="text-slate-600 text-sm leading-relaxed mb-6">
                  {skill.description || "Comprehensive modular learning path designed to take you from foundational concepts to production competency."}
                </p>
              </div>

              <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
                <span className="text-xs font-medium text-slate-500">
                  {skill.resource_count} curated modules
                </span>
                <button
                  onClick={() => handleStartPath(skill.id)}
                  disabled={creatingId === skill.id}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 transition-colors shadow-sm disabled:opacity-50"
                >
                  {creatingId === skill.id ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      Start Path
                      <ArrowRight className="w-3.5 h-3.5" />
                    </>
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
