import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowRight, Clock3, Code2, Loader2, Play, Send, Trophy } from "lucide-react";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

const difficultyStyles = {
  beginner: "bg-emerald-50 text-emerald-700 border-emerald-200",
  intermediate: "bg-amber-50 text-amber-700 border-amber-200",
  advanced: "bg-rose-50 text-rose-700 border-rose-200",
};

function getErrorMessage(error) {
  return error.response?.data?.error || "The request failed. Please try again.";
}

export default function CodingChallengesPage() {
  const [challenges, setChallenges] = useState([]);
  const [selectedChallenge, setSelectedChallenge] = useState(null);
  const [loading, setLoading] = useState(true);
  const [catalogError, setCatalogError] = useState("");
  const [attempt, setAttempt] = useState(null);
  const [sourceCode, setSourceCode] = useState("");
  const [testResults, setTestResults] = useState(null);
  const [requestError, setRequestError] = useState("");
  const [timeLeft, setTimeLeft] = useState(null);
  const [starting, setStarting] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    let active = true;
    api.get("/challenges/")
      .then((response) => {
        if (active) {
          setChallenges(response.data);
          setCatalogError("");
        }
      })
      .catch((error) => {
        console.error("Could not load coding challenges:", error);
        if (active) setCatalogError(getErrorMessage(error));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const loadChallenge = useCallback(async (slug) => {
    setSelectedChallenge(null);
    setAttempt(null);
    setTestResults(null);
    setRequestError("");
    setTimeLeft(null);
    try {
      const response = await api.get(`/challenges/${slug}/`);
      setSelectedChallenge(response.data);
      setSourceCode(response.data.starter_code);
    } catch (error) {
      console.error("Could not load challenge details:", error);
      setRequestError(getErrorMessage(error));
    }
  }, []);

  useEffect(() => {
    if (challenges.length > 0) loadChallenge(challenges[0].slug);
  }, [challenges, loadChallenge]);

  useEffect(() => {
    if (!attempt || attempt.status !== "in_progress") return undefined;
    const updateTimer = () => {
      const seconds = Math.max(
        0,
        Math.ceil((new Date(attempt.expires_at).getTime() - Date.now()) / 1000)
      );
      setTimeLeft(seconds);
    };
    updateTimer();
    const timerId = window.setInterval(updateTimer, 1000);
    return () => window.clearInterval(timerId);
  }, [attempt]);

  const handleStart = async () => {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }
    if (!selectedChallenge) return;
    setStarting(true);
    setRequestError("");
    setTestResults(null);
    try {
      const response = await api.post(`/challenges/${selectedChallenge.id}/start/`);
      setAttempt(response.data);
      setSourceCode(response.data.starter_code);
    } catch (error) {
      console.error("Could not start coding attempt:", error);
      setRequestError(getErrorMessage(error));
    } finally {
      setStarting(false);
    }
  };

  const handleSubmit = async () => {
    if (!attempt || !sourceCode.trim()) return;
    setSubmitting(true);
    setRequestError("");
    try {
      const response = await api.post(
        `/challenge-attempts/${attempt.id}/submit/`,
        { source_code: sourceCode }
      );
      setAttempt(response.data);
      setTestResults(response.data.test_results);
    } catch (error) {
      console.error("Could not submit coding solution:", error);
      setRequestError(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  };

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60).toString().padStart(2, "0");
    const remaining = (seconds % 60).toString().padStart(2, "0");
    return `${minutes}:${remaining}`;
  };

  const canEdit = attempt?.status === "in_progress" && timeLeft > 0;

  return (
    <div className="min-h-screen bg-slate-50/70 px-4 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-indigo-50 px-3 py-1 text-xs font-bold uppercase tracking-wider text-indigo-700">
              <Code2 className="h-4 w-4" />
              Coding Arena
            </p>
            <h1 className="mt-3 text-3xl font-black tracking-tight text-slate-900 sm:text-4xl">
              Solve. Test. Improve.
            </h1>
            <p className="mt-2 max-w-2xl text-sm leading-relaxed text-slate-600 sm:text-base">
              Timed Python challenges are checked against sample and hidden test cases by the configured Judge0 execution service.
            </p>
          </div>
          <Link to="/dashboard" className="inline-flex items-center gap-2 text-sm font-bold text-indigo-700 hover:text-indigo-900">
            Dashboard <ArrowRight className="h-4 w-4" />
          </Link>
        </div>

        {catalogError && (
          <div role="alert" className="mb-5 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm font-medium text-rose-800">
            Could not load the challenge catalog: {catalogError}
          </div>
        )}
        {requestError && (
          <div role="alert" className="mb-5 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm font-medium text-amber-900">
            {requestError}
          </div>
        )}

        {loading ? (
          <div className="flex min-h-64 items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
          </div>
        ) : challenges.length === 0 ? (
          <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center text-slate-600">
            No active challenges are available yet.
          </div>
        ) : (
          <div className="grid gap-6 lg:grid-cols-[300px_minmax(0,1fr)]">
            <aside className="space-y-3">
              <h2 className="px-1 text-sm font-extrabold uppercase tracking-wider text-slate-500">
                Challenge set
              </h2>
              {challenges.map((challenge) => (
                <button
                  type="button"
                  key={challenge.id}
                  onClick={() => loadChallenge(challenge.slug)}
                  className={`w-full rounded-2xl border p-4 text-left transition ${
                    selectedChallenge?.id === challenge.id
                      ? "border-indigo-300 bg-indigo-50 shadow-sm"
                      : "border-slate-200 bg-white hover:border-indigo-200"
                  }`}
                >
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    {challenge.difficulty}
                  </span>
                  <span className="mt-1 block font-extrabold text-slate-900">{challenge.title}</span>
                  <span className="mt-2 flex items-center gap-1.5 text-xs font-semibold text-slate-500">
                    <Clock3 className="h-3.5 w-3.5" />
                    {challenge.duration_minutes} minutes
                    <span className="ml-auto">{challenge.test_case_count} test cases</span>
                  </span>
                </button>
              ))}
            </aside>

            <section className="min-w-0 overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
              {!selectedChallenge ? (
                <div className="flex min-h-80 items-center justify-center">
                  <Loader2 className="h-7 w-7 animate-spin text-indigo-600" />
                </div>
              ) : (
                <>
                  <div className="border-b border-slate-200 p-5 sm:p-7">
                    <div className="flex flex-wrap items-center gap-3">
                      <h2 className="text-2xl font-black text-slate-900">{selectedChallenge.title}</h2>
                      <span className={`rounded-full border px-3 py-1 text-xs font-bold capitalize ${difficultyStyles[selectedChallenge.difficulty]}`}>
                        {selectedChallenge.difficulty}
                      </span>
                    </div>
                    <p className="mt-3 whitespace-pre-line text-sm leading-relaxed text-slate-600">
                      {selectedChallenge.description}
                    </p>
                    <div className="mt-5 grid gap-3 sm:grid-cols-2">
                      {selectedChallenge.sample_test_cases.map((testCase, index) => (
                        <div key={`${selectedChallenge.id}-${index}`} className="rounded-xl bg-slate-50 p-3">
                          <p className="text-xs font-bold uppercase tracking-wider text-slate-500">
                            Example {index + 1}
                          </p>
                          <div className="mt-2 grid grid-cols-2 gap-3 font-mono text-xs">
                            <div>
                              <p className="mb-1 font-sans font-bold text-slate-500">Input</p>
                              <pre className="whitespace-pre-wrap text-slate-800">{testCase.stdin || "(empty)"}</pre>
                            </div>
                            <div>
                              <p className="mb-1 font-sans font-bold text-slate-500">Output</p>
                              <pre className="whitespace-pre-wrap text-slate-800">{testCase.expected_output}</pre>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="p-5 sm:p-7">
                    <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
                      <label htmlFor="solution-code" className="font-extrabold text-slate-900">
                        Python 3 solution
                      </label>
                      <div className="flex items-center gap-2">
                        {attempt?.status === "in_progress" && (
                          <span className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-2 font-mono text-sm font-bold ${
                            timeLeft < 60 ? "bg-rose-100 text-rose-700" : "bg-slate-100 text-slate-700"
                          }`}>
                            <Clock3 className="h-4 w-4" />
                            {formatTime(timeLeft ?? 0)}
                          </span>
                        )}
                        {!attempt || attempt.status !== "in_progress" ? (
                          <button
                            type="button"
                            onClick={handleStart}
                            disabled={starting || !selectedChallenge}
                            className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-bold text-white hover:bg-indigo-700 disabled:opacity-50"
                          >
                            {starting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                            {isAuthenticated ? "Start timed attempt" : "Sign in to start"}
                          </button>
                        ) : (
                          <button
                            type="button"
                            onClick={handleSubmit}
                            disabled={!canEdit || submitting}
                            className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-bold text-white hover:bg-emerald-700 disabled:opacity-50"
                          >
                            {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                            Submit to Judge0
                          </button>
                        )}
                      </div>
                    </div>
                    <textarea
                      id="solution-code"
                      value={sourceCode}
                      onChange={(event) => setSourceCode(event.target.value)}
                      disabled={!canEdit}
                      spellCheck="false"
                      aria-label="Python solution source code"
                      className="min-h-[360px] w-full resize-y rounded-2xl border border-slate-700 bg-slate-950 p-4 font-mono text-sm leading-relaxed text-emerald-100 outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-75"
                    />
                    {!isAuthenticated && (
                      <p className="mt-2 text-xs text-slate-500">
                        <Link className="font-bold text-indigo-700 underline" to="/login">Sign in</Link> to start a timed attempt and submit a solution.
                      </p>
                    )}
                    {testResults && (
                      <div className="mt-5 rounded-2xl border border-slate-200 bg-slate-50 p-4">
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <p className="inline-flex items-center gap-2 font-extrabold text-slate-900">
                            <Trophy className="h-5 w-5 text-amber-500" />
                            {attempt.status.replaceAll("_", " ")}
                          </p>
                          <p className="text-sm font-bold text-slate-600">
                            {attempt.passed_test_cases}/{attempt.total_test_cases} tests passed
                            {attempt.execution_time_ms != null && ` · ${attempt.execution_time_ms} ms`}
                          </p>
                        </div>
                        <ul className="mt-3 grid gap-2 sm:grid-cols-2">
                          {testResults.map((result) => (
                            <li
                              key={result.order}
                              className={`rounded-lg px-3 py-2 text-xs font-bold ${
                                result.passed
                                  ? "bg-emerald-100 text-emerald-800"
                                  : result.status === "time_limit"
                                    ? "bg-amber-100 text-amber-800"
                                    : "bg-rose-100 text-rose-800"
                              }`}
                            >
                              <span>
                                Test {result.order} {result.is_sample ? "(sample)" : "(hidden)"}: {result.status.replaceAll("_", " ")}
                                {result.diagnostic && (
                                  <pre className="mt-1 whitespace-pre-wrap font-mono font-normal">{result.diagnostic}</pre>
                                )}
                              </span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {timeLeft === 0 && attempt?.status === "in_progress" && (
                      <p className="mt-3 text-sm font-bold text-rose-700">
                        Time expired. Start a new attempt to try this challenge again.
                      </p>
                    )}
                  </div>
                </>
              )}
            </section>
          </div>
        )}
      </div>
    </div>
  );
}
