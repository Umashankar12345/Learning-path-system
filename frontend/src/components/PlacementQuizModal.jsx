import { useCallback, useEffect, useState } from "react";
import { ArrowLeft, ArrowRight, CheckCircle2, Loader2, X } from "lucide-react";
import api from "../api/client";

function getErrorMessage(error) {
  const data = error.response?.data;
  if (typeof data?.error === "string") return data.error;
  if (data && typeof data === "object") {
    const collectMessages = (value) => {
      if (typeof value === "string") return [value];
      if (Array.isArray(value)) return value.flatMap(collectMessages);
      if (value && typeof value === "object") {
        return Object.values(value).flatMap(collectMessages);
      }
      return [];
    };
    const messages = collectMessages(data);
    if (messages.length) return messages.join(" ");
  }
  if (error.request && !error.response) {
    return "Could not reach the learning server. Check that the backend is running, then retry.";
  }
  return error.message || "Could not complete the placement assessment. Please try again.";
}

export default function PlacementQuizModal({ initialSkill = null, onClose, onComplete }) {
  const [skills, setSkills] = useState([]);
  const [selectedSkill, setSelectedSkill] = useState(initialSkill);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [questionIndex, setQuestionIndex] = useState(0);
  const [result, setResult] = useState(null);
  const [loadingSkills, setLoadingSkills] = useState(!initialSkill);
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (initialSkill) return;
    let active = true;
    api.get("/skills/")
      .then((response) => {
        if (active) setSkills(response.data);
      })
      .catch((requestError) => {
        console.error("Could not load skills for placement:", requestError);
        if (active) setError(getErrorMessage(requestError));
      })
      .finally(() => {
        if (active) setLoadingSkills(false);
      });
    return () => {
      active = false;
    };
  }, [initialSkill]);

  const startAssessment = useCallback(async (skill) => {
    setSelectedSkill(skill);
    setLoadingQuestions(true);
    setError("");
    setQuestions([]);
    setAnswers({});
    setQuestionIndex(0);
    setResult(null);
    try {
      const response = await api.get(`/tracks/${skill.id}/placement-quiz/`);
      if (
        !Array.isArray(response.data) ||
        response.data.length !== 10 ||
        response.data.some(
          (question) =>
            !Number.isInteger(question.id) ||
            typeof question.question_text !== "string" ||
            !Array.isArray(question.options) ||
            question.options.length !== 4 ||
            !question.options.every((option) => typeof option === "string") ||
            ![1, 2, 3].includes(question.difficulty)
        )
      ) {
        throw new Error("This skill's placement quiz is incomplete. Please try again later.");
      }
      setQuestions(response.data);
    } catch (requestError) {
      console.error("Could not load placement questions:", requestError);
      setQuestions([]);
      setError(getErrorMessage(requestError));
    } finally {
      setLoadingQuestions(false);
    }
  }, []);

  useEffect(() => {
    if (initialSkill) startAssessment(initialSkill);
  }, [initialSkill, startAssessment]);

  const handleSubmit = async () => {
    if (!selectedSkill || questions.length !== 10 || Object.keys(answers).length !== questions.length) {
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      const response = await api.post(
        `/tracks/${selectedSkill.id}/placement-submit/`,
        {
          answers: questions.map((question) => ({
            question_id: question.id,
            selected_option: answers[question.id],
          })),
        }
      );
      setResult(response.data);
    } catch (requestError) {
      console.error("Could not submit placement assessment:", requestError);
      setError(getErrorMessage(requestError));
    } finally {
      setSubmitting(false);
    }
  };

  const question = questions[questionIndex];
  const answeredCount = Object.keys(answers).length;
  const progress = questions.length ? (answeredCount / questions.length) * 100 : 0;

  return (
    <div
      className="fixed inset-0 z-[70] flex items-center justify-center overflow-y-auto bg-slate-950/70 px-4 py-8 backdrop-blur-sm"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="placement-title"
        className="my-auto w-full max-w-2xl overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-2xl shadow-slate-950/30"
      >
        <div className="flex items-start justify-between gap-4 border-b border-slate-100 px-6 py-5 sm:px-8">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-indigo-600">
              Adaptive placement
            </p>
            <h2 id="placement-title" className="mt-1 text-xl font-black text-slate-900 sm:text-2xl">
              {result ? "Your learning level" : "Find your starting point"}
            </h2>
            <p className="mt-1 text-sm text-slate-500">
              {selectedSkill?.name || "Choose a skill to begin the 10-question diagnostic."}
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close placement quiz"
            className="rounded-xl p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-900"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="max-h-[min(70vh,620px)] overflow-y-auto px-6 py-6 sm:px-8">
          {error && (
            <div role="alert" className="mb-5 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">
              {error}
            </div>
          )}

          {result ? (
            <div>
              <div className="rounded-2xl bg-gradient-to-br from-indigo-600 to-violet-600 p-6 text-white">
                <p className="text-sm font-semibold text-indigo-100">Recommended starting level</p>
                <div className="mt-1 flex flex-wrap items-end justify-between gap-3">
                  <h3 className="text-3xl font-black">{result.recommended_level_label}</h3>
                  <span className="rounded-full bg-white/15 px-3 py-1 text-sm font-bold">
                    {result.score}% · {result.correct_answers}/{result.total_questions}
                  </span>
                </div>
                <p className="mt-3 text-sm text-indigo-100">
                  Your pathway is ready. Earlier-level modules have been marked complete based on this assessment.
                </p>
              </div>
              <div className="mt-5 space-y-3">
                {result.skill_gap_breakdown.map((level) => (
                  <div key={level.difficulty} className="rounded-xl border border-slate-200 p-4">
                    <div className="flex items-center justify-between gap-3">
                      <span className="font-bold text-slate-800">{level.label}</span>
                      <span className="text-sm font-semibold text-slate-500">
                        {level.correct}/{level.total} correct
                      </span>
                    </div>
                    <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-500"
                        style={{ width: `${level.accuracy}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
              <button
                type="button"
                onClick={() => onComplete(result.path_id)}
                className="mt-6 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600 px-5 py-3 font-bold text-white shadow-lg shadow-indigo-600/20 transition hover:bg-indigo-700"
              >
                Open my personalized roadmap
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          ) : !selectedSkill ? (
            loadingSkills ? (
              <div className="flex items-center justify-center py-16">
                <Loader2 className="h-7 w-7 animate-spin text-indigo-600" />
              </div>
            ) : (
              <div className="grid gap-3 sm:grid-cols-2">
                {skills.map((skill) => (
                  <button
                    key={skill.id}
                    type="button"
                    onClick={() => startAssessment(skill)}
                    className="rounded-2xl border border-slate-200 p-4 text-left transition hover:border-indigo-300 hover:bg-indigo-50/60"
                  >
                    <span className="text-xs font-bold uppercase tracking-wider text-indigo-600">
                      {skill.category}
                    </span>
                    <span className="mt-1 block font-extrabold text-slate-900">{skill.name}</span>
                    <span className="mt-2 flex items-center gap-1 text-xs font-semibold text-slate-500">
                      Start diagnostic <ArrowRight className="h-3.5 w-3.5" />
                    </span>
                  </button>
                ))}
              </div>
            )
          ) : loadingQuestions ? (
            <div className="flex items-center justify-center py-16">
              <Loader2 className="h-7 w-7 animate-spin text-indigo-600" />
            </div>
          ) : question ? (
            <>
              <div className="flex items-center justify-between gap-3 text-xs font-bold text-slate-500">
                <span>Question {questionIndex + 1} of {questions.length}</span>
                <span>{answeredCount} answered</span>
              </div>
              <div
                role="progressbar"
                aria-label="Placement quiz progress"
                aria-valuenow={answeredCount}
                aria-valuemin={0}
                aria-valuemax={questions.length}
                className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100"
              >
                <div
                  className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 transition-all"
                  style={{ width: `${progress}%` }}
                />
              </div>

              <div className="mt-6">
                <span className="rounded-full bg-indigo-50 px-3 py-1 text-xs font-bold text-indigo-700">
                  {["", "Beginner", "Intermediate", "Advanced"][question.difficulty]}
                </span>
                <h3 className="mt-3 text-lg font-extrabold leading-snug text-slate-900 sm:text-xl">
                  {question.question_text}
                </h3>
                <div className="mt-5 space-y-2.5">
                  {question.options.map((option, index) => {
                    const selected = answers[question.id] === index;
                    return (
                      <button
                        key={`${question.id}-${index}`}
                        type="button"
                        aria-pressed={selected}
                        onClick={() => setAnswers((current) => ({ ...current, [question.id]: index }))}
                        className={`flex w-full items-center gap-3 rounded-xl border p-3.5 text-left text-sm font-semibold transition ${
                          selected
                            ? "border-indigo-500 bg-indigo-50 text-indigo-800 ring-2 ring-indigo-100"
                            : "border-slate-200 text-slate-700 hover:border-indigo-200 hover:bg-slate-50"
                        }`}
                      >
                        <span className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-black ${
                          selected ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-500"
                        }`}>
                          {String.fromCharCode(65 + index)}
                        </span>
                        {option}
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="mt-7 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-5">
                <button
                  type="button"
                  onClick={() => setQuestionIndex((index) => Math.max(0, index - 1))}
                  disabled={questionIndex === 0}
                  className="inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-bold text-slate-600 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  <ArrowLeft className="h-4 w-4" /> Previous
                </button>
                {questionIndex < questions.length - 1 ? (
                  <button
                    type="button"
                    onClick={() => setQuestionIndex((index) => index + 1)}
                    disabled={answers[question.id] === undefined}
                    className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-bold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    Next <ArrowRight className="h-4 w-4" />
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={handleSubmit}
                    disabled={answeredCount !== questions.length || submitting}
                    className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-bold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />}
                    Get my placement
                  </button>
                )}
              </div>
            </>
          ) : (
            <div className="py-8 text-center">
              <p className="text-sm text-slate-600">
                {error
                  ? "The diagnostic questions could not be loaded."
                  : "No diagnostic questions are currently available."}
              </p>
              {selectedSkill && (
                <button
                  type="button"
                  onClick={() => startAssessment(selectedSkill)}
                  disabled={loadingQuestions}
                  className="mt-4 inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-indigo-700 disabled:cursor-wait disabled:opacity-60"
                >
                  {loadingQuestions && <Loader2 className="h-4 w-4 animate-spin" />}
                  Retry loading questions
                </button>
              )}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
