import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { ToastProvider } from "./context/ToastContext";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import ProtectedRoute from "./components/ProtectedRoute";

import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import SkillsPage from "./pages/SkillsPage";
import DashboardPage from "./pages/DashboardPage";
import PathDetailPage from "./pages/PathDetailPage";
import LeaderboardPage from "./pages/LeaderboardPage";
import CodingChallengesPage from "./pages/CodingChallengesPage";

function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <Router>
          <div className="app-shell min-h-screen flex flex-col font-sans antialiased selection:bg-indigo-500 selection:text-white">
            <Navbar />
            <main className="flex-1 flex flex-col">
              <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/signup" element={<SignupPage />} />
                <Route path="/skills" element={<SkillsPage />} />
                <Route path="/leaderboard" element={<LeaderboardPage />} />
                <Route path="/challenges" element={<CodingChallengesPage />} />
                <Route
                  path="/dashboard"
                  element={
                    <ProtectedRoute>
                      <DashboardPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/paths/:id"
                  element={
                    <ProtectedRoute>
                      <PathDetailPage />
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </main>
            <Footer />
          </div>
        </Router>
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;
