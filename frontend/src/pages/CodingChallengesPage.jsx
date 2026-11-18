import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import {
  ArrowRight,
  CheckCircle2,
  Clock3,
  Code2,
  History,
  Loader2,
  LockKeyhole,
  Play,
  Send,
  Trophy,
  UnlockKeyhole,
} from "lucide-react";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

const difficulties = [
  { value: "all", label: "All levels" },
  { value: "easy", label: "Easy" },
  { value: "medium", label: "Medium" },
  { value: "hard", label: "Hard" },
];

const topics = ["all", "Python", "Arrays", "Strings", "SQL", "Data Science"];

const difficultyStyles = {
  easy: "bg-emerald-50 text-emerald-700 border-emerald-200",
  medium: "bg-amber-50 text-amber-700 border-amber-200",
  hard: "bg-rose-50 text-rose-700 border-rose-200",
};

function getErrorMessage(error) {
  const data = error.response?.data;
  if (typeof data?.error === "string") return data.error;
  if (typeof data?.detail === "string") return data.detail;
  return "The request failed. Please try again.";
}

function formatDate(value) {
  return new Date(value).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default function CodingChallengesPage() {
  const [searchParams] = useSearchParams();
  const requestedProblemId = Number(searchParams.get("problem")) || null;
  const [challenges, setChallenges] = useState([]);
  const [selectedChallenge, setSelectedChallenge] = useState(null);
  const [difficulty, setDifficulty] = useState("all");
  const [topic, setTopic] = useState("all");
  const [loading, setLoading] = useState(true);
  const [catalogError, setCatalogError] = useState("");
  const [attempt, setAttempt] = useState(null);
  const [sourceCode, setSourceCode] = useState("");
  const [testResults, setTestResults] = useState(null);
  const [requestError, setRequestError] = useState("");
  const [timeLeft, setTimeLeft] = useState(null);
  const [starting, setStarting] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState("problem");
  const [submissions, setSubmissions] = useState([]);
  const [historyError, setHistoryError] = useState("");
  const [solution, setSolution] = useState("");
  const [solutionError, setSolutionError] = useState("");
  const [solutionLoading, setSolutionLoading] = useState(false);
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const refreshHistory = useCallback(async () => {
    if (!isAuthenticated) return;
    try {
      const response = await api.get("/arena/submissions/");
      setSubmissions(response.data);
      setHistoryError("");
    } catch (error) {
      console.error("Could not load coding submission history:", error);
      setHistoryError(getErrorMessage(error));
    }
  }, [isAuthenticated]);

  useEffect(() => {
    let active = true;
    const params = {};
    if (difficulty !== "all") params.difficulty = difficulty;
    if (topic !== "all") params.topic = topic;

    setLoading(true);
    api.get("/arena/problems/", { params })
      .then((response) => {
        if (!active) return;
        const available = response.data;
        setChallenges(available);
        setCatalogError("");
        const requested = available.find((challenge) => challenge.id === requestedProblemId);
        const firstChallenge = requested || available[0] || null;
        setSelectedChallenge(firstChallenge);
        setAttempt(null);
        setTestResults(null);
        setRequestError("");
        setSolution("");
        setActiveTab("problem");
        setSourceCode(firstChallenge?.starter_code || "");
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
  }, [difficulty, topic, requestedProblemId]);

  useEffect(() => {
    refreshHistory();
  }, [refreshHistory]);

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

  const selectChallenge = (challenge) => {
    setSelectedChallenge(challenge);
    setAttempt(null);
    setTestResults(null);
    setRequestError("");
    setSolution("");
    setSolutionError("");
    setActiveTab("problem");
    setTimeLeft(null);
    setSourceCode(challenge.starter_code);
  };

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
        { source_code: sourceCode, language: "python3" }
      );
      setAttempt(response.data);
      setTestResults(response.data.test_results);
      await refreshHistory();
    } catch (error) {
      console.error("Could not submit coding solution:", error);
      setRequestError(getErrorMessage(error));
    } finally {
      setSubmitting(false);
    }
  };

  const openSolution = async () => {
    if (!selectedChallenge || !hasAttempted) return;
    setActiveTab("solution");
    setSolution("");
    setSolutionError("");
    setSolutionLoading(true);
    try {
      const response = await api.get(
        `/arena/problems/${selectedChallenge.id}/solution/`
      );
      setSolution(response.data.reference_solution);
    } catch (error) {
      console.error("Could not load the reference solution:", error);
      setSolutionError(getErrorMessage(error));
    } finally {
      setSolutionLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60).toString().padStart(2, "0");
    const remaining = (seconds % 60).toString().padStart(2, "0");
    return `${minutes}:${remaining}`;
  };

  const canEdit = attempt?.status === "in_progress" && timeLeft > 0;
  const challengeSubmissions = selectedChallenge
    ? submissions.filter((submission) => submission.challenge === selectedChallenge.id)
    : [];
  const hasAttempted = challengeSubmissions.length > 0;

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
              Run Python solutions against real sample and hidden test cases, then review your history and unlock reference solutions.
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

        <div className="mb-5 flex flex-wrap gap-2">
          {difficulties.map((level) => (
            <button
              key={level.value}
              type="button"
              aria-pressed={difficulty === level.value}
              onClick={() => setDifficulty(level.value)}
              className={`rounded-full border px-4 py-2 text-xs font-bold transition ${
                difficulty === level.value
                  ? "border-indigo-600 bg-indigo-600 text-white shadow-sm"
                  : "border-slate-200 bg-white text-slate-600 hover:border-indigo-200 hover:text-indigo-700"
              }`}
            >
              {level.label}
            </button>
          ))}
          <span className="mx-1 hidden border-l border-slate-300 sm:block" />
          {topics.map((item) => (
            <button
              key={item}
              type="button"
              aria-pressed={topic === item}
              onClick={() => setTopic(item)}
              className={`rounded-full border px-3.5 py-2 text-xs font-bold capitalize transition ${
                topic === item
                  ? "border-violet-600 bg-violet-600 text-white shadow-sm"
                  : "border-slate-200 bg-white text-slate-600 hover:border-violet-200 hover:text-violet-700"
              }`}
            >
              {item === "all" ? "All topics" : item}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex min-h-64 items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
          </div>
        ) : challenges.length === 0 ? (
          <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center text-slate-600">
            No problems match those filters.
          </div>
        ) : (
          <div className="grid gap-6 lg:grid-cols-[300px_minmax(0,1fr)]">
            <aside className="space-y-3">
              <h2 className="px-1 text-sm font-extrabold uppercase tracking-wider text-slate-500">
                Problem set
              </h2>
              {challenges.map((challenge) => (
                <button
                  type="button"
                  key={challenge.id}
                  onClick={() => selectChallenge(challenge)}
                  className={`w-full rounded-2xl border p-4 text-left transition ${
                    selectedChallenge?.id === challenge.id
                      ? "border-indigo-300 bg-indigo-50 shadow-sm"
                      : "border-slate-200 bg-white hover:border-indigo-200"
                  }`}
                >
                  <span className="flex items-center justify-between gap-2">
                    <span className={`rounded-full border px-2 py-0.5 text-[10px] font-bold uppercase ${difficultyStyles[challenge.difficulty]}`}>
                      {challenge.difficulty}
                    </span>
                    {challenge.is_daily_challenge && (
                      <span className="text-[10px] font-bold uppercase tracking-wider text-amber-600">Daily</span>
                    )}
                  </span>
                  <span className="mt-2 block font-extrabold text-slate-900">{challenge.title}</span>
                  <span className="mt-2 flex items-center gap-1.5 text-xs font-semibold text-slate-500">
                    <Clock3 className="h-3.5 w-3.5" />
                    {challenge.duration_minutes} minutes
                    <span className="ml-auto">{challenge.test_case_count} tests</span>
                  </span>
                  <span className="mt-2 flex flex-wrap gap-1">
                    {challenge.topic_tags.map((tag) => (
                      <span key={tag} className="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-500">{tag}</span>
                    ))}
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
                  <div className="flex flex-wrap gap-2 border-b border-slate-200 bg-slate-50/80 p-3">
                    <button
                      type="button"
                      onClick={() => setActiveTab("problem")}
                      className={`inline-flex items-center gap-2 rounded-lg px-3.5 py-2 text-xs font-bold ${
                        activeTab === "problem" ? "bg-white text-indigo-700 shadow-sm" : "text-slate-500 hover:bg-white"
                      }`}
                    >
                      <Code2 className="h-4 w-4" /> Problem
                    </button>
                    <button
                      type="button"
                      onClick={() => setActiveTab("history")}
                      className={`inline-flex items-center gap-2 rounded-lg px-3.5 py-2 text-xs font-bold ${
                        activeTab === "history" ? "bg-white text-indigo-700 shadow-sm" : "text-slate-500 hover:bg-white"
                      }`}
                    >
                      <History className="h-4 w-4" /> Submission History
                      {challengeSubmissions.length > 0 && (
                        <span className="rounded-full bg-indigo-100 px-1.5 py-0.5 text-[10px]">{challengeSubmissions.length}</span>
                      )}
                    </button>
                    <button
                      type="button"
                      disabled={!hasAttempted || !isAuthenticated}
                      onClick={openSolution}
                      title={hasAttempted ? "View the reference solution" : "Submit at least one attempt to unlock"}
                      className={`inline-flex items-center gap-2 rounded-lg px-3.5 py-2 text-xs font-bold disabled:cursor-not-allowed disabled:opacity-50 ${
                        activeTab === "solution" ? "bg-white text-indigo-700 shadow-sm" : "text-slate-500 hover:bg-white"
                      }`}
                    >
                      {hasAttempted ? <UnlockKeyhole className="h-4 w-4" /> : <LockKeyhole className="h-4 w-4" />}
                      Solution
                    </button>
                  </div>

                  {activeTab === "history" ? (
                    <div className="p-5 sm:p-7">
                      <h2 className="text-xl font-black text-slate-900">Your submissions</h2>
                      <p className="mt-1 text-sm text-slate-500">{selectedChallenge.title}</p>
                      {!isAuthenticated ? (
                        <p className="mt-6 rounded-xl bg-slate-50 p-4 text-sm text-slate-600">
                          <Link to="/login" className="font-bold text-indigo-700 underline">Sign in</Link> to view your submission history.
                        </p>
                      ) : historyError ? (
                        <p role="alert" className="mt-6 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{historyError}</p>
                      ) : challengeSubmissions.length === 0 ? (
                        <p className="mt-6 rounded-xl bg-slate-50 p-5 text-center text-sm text-slate-500">
                          No submissions for this problem yet.
                        </p>
                      ) : (
                        <div className="mt-5 overflow-x-auto">
                          <table className="w-full min-w-[560px] text-left text-sm">
                            <thead className="border-b border-slate-200 text-xs uppercase tracking-wider text-slate-500">
                              <tr>
                                <th className="px-3 py-3">Date</th>
                                <th className="px-3 py-3">Language</th>
                                <th className="px-3 py-3">Result</th>
                                <th className="px-3 py-3">Tests</th>
                                <th className="px-3 py-3">Runtime</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                              {challengeSubmissions.map((submission) => (
                                <tr key={submission.id}>
                                  <td className="px-3 py-3 text-slate-600">{formatDate(submission.created_at)}</td>
                                  <td className="px-3 py-3 font-semibold text-slate-700">{submission.language}</td>
                                  <td className="px-3 py-3">
                                    <span className={`rounded-full px-2.5 py-1 text-xs font-bold ${
                                      submission.status === "accepted"
                                        ? "bg-emerald-100 text-emerald-800"
                                        : "bg-rose-100 text-rose-700"
                                    }`}>{submission.status.replaceAll("_", " ")}</span>
                                  </td>
                                  <td className="px-3 py-3 text-slate-600">{submission.passed_count}/{submission.total_count}</td>
                                  <td className="px-3 py-3 text-slate-600">{submission.runtime_ms ?? "—"} ms</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </div>
                  ) : activeTab === "solution" ? (
                    <div className="p-5 sm:p-7">
                      <h2 className="text-xl font-black text-slate-900">Reference solution</h2>
                      {solutionLoading ? (
                        <div className="flex h-48 items-center justify-center">
                          <Loader2 className="h-7 w-7 animate-spin text-indigo-600" />
                        </div>
                      ) : solutionError ? (
                        <p role="alert" className="mt-5 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{solutionError}</p>
                      ) : (
                        <pre className="mt-5 min-h-48 overflow-x-auto rounded-2xl bg-slate-950 p-5 font-mono text-sm leading-relaxed text-emerald-100">
                          {solution}
                        </pre>
                      )}
                    </div>
                  ) : (
                    <>
                      <div className="border-b border-slate-200 p-5 sm:p-7">
                        <div className="flex flex-wrap items-center gap-3">
                          <h2 className="text-2xl font-black text-slate-900">{selectedChallenge.title}</h2>
                          <span className={`rounded-full border px-3 py-1 text-xs font-bold capitalize ${difficultyStyles[selectedChallenge.difficulty]}`}>
                            {selectedChallenge.difficulty}
                          </span>
                          {selectedChallenge.topic_tags.map((tag) => (
                            <span key={tag} className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-600">{tag}</span>
                          ))}
                        </div>
                        <p className="mt-3 whitespace-pre-line text-sm leading-relaxed text-slate-600">
                          {selectedChallenge.description}
                        </p>
                        <div className="mt-5 grid gap-3 sm:grid-cols-2">
                          {selectedChallenge.sample_test_cases.map((testCase, index) => (
                            <div key={`${selectedChallenge.id}-${index}`} className="rounded-xl bg-slate-50 p-3">
                              <p className="text-xs font-bold uppercase tracking-wider text-slate-500">Example {index + 1}</p>
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
                                <Clock3 className="h-4 w-4" /> {formatTime(timeLeft ?? 0)}
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
                                {attempt.passed_test_cases} of {attempt.total_test_cases} test cases passed
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
                </>
              )}
            </section>
          </div>
        )}
      </div>
    </div>
  );
}
