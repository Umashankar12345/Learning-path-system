import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import api from "../api/client";
import GoogleAuthButton from "../components/GoogleAuthButton";
import { Compass, AlertCircle, Loader2 } from "lucide-react";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { login } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const user = await login(username, password);
      toast.success(`Welcome back, ${user.username}!`);
      navigate("/dashboard");
    } catch (err) {
      console.error(err);
      const msg = !err.response
        ? "Cannot reach the server. Start the Django backend on port 8000 and try again."
        : (err.response?.data?.detail || "Invalid credentials. Please verify username and password.");
      setError(msg);
      toast.error(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleGoogleLogin = async (credential) => {
    try {
      const res = await api.post("/auth/google/", { credential });
      const { user, token } = res.data;
      localStorage.setItem("access_token", token.access);
      localStorage.setItem("refresh_token", token.refresh);
      localStorage.setItem("user", JSON.stringify(user));
      toast.success(`Signed in via Google as ${user.username}!`);
      window.location.href = "/dashboard";
    } catch (err) {
      console.error(err);
      const detail = err.response?.data?.error;
      toast.error(detail || "Google sign in failed. Configure Google OAuth or use username login.");
    }
  };



  return (
    <div className="min-h-[85vh] flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="inline-flex w-14 h-14 rounded-2xl bg-indigo-600 items-center justify-center text-white mb-4 shadow-lg shadow-indigo-500/25">
          <Compass className="w-7 h-7" />
        </div>
        <h2 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
          Welcome Back
        </h2>
        <p className="mt-2 text-base text-slate-600">
          Sign in to access your customized learning pathway
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-9 px-6 sm:px-10 shadow-lg shadow-slate-200/50 rounded-3xl border border-slate-200">
          {error && (
            <div className="mb-6 p-4 rounded-2xl bg-rose-50 border border-rose-200 flex items-start gap-3 text-rose-700 text-sm font-medium">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Google One-Click Login */}
          <GoogleAuthButton
            text="Continue with Google"
            onCredential={handleGoogleLogin}
            onError={() => toast.error("Google sign in failed. Please try again.")}
          />

          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200"></div>
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-3 text-slate-400 font-bold">Or sign in with username</span>
            </div>
          </div>

          <form className="space-y-5" onSubmit={handleSubmit}>
            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1.5">
                Username
              </label>
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-base"
                placeholder="e.g. learner_demo"
              />
            </div>

            <div>
              <label className="block text-sm font-bold text-slate-700 mb-1.5">
                Password
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-base"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex items-center justify-center gap-2 py-3.5 px-4 rounded-xl text-base font-bold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-md transition-all disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Signing In...
                </>
              ) : (
                "Sign In"
              )}
            </button>
          </form>

          {/* Account helpers */}
          <div className="mt-6 pt-6 border-t border-slate-100 flex flex-col gap-3">
            <p className="text-center text-sm text-slate-600 font-medium">
              Don't have an account?{" "}
              <Link to="/signup" className="font-bold text-indigo-600 hover:text-indigo-500 underline">
                Sign up for free
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
