"use client";

import { useEffect, useState } from "react";
import Dashboard from "./dashboard";
import { login, register } from "../lib/api";

export default function Home() {
  const [authenticated, setAuthenticated] = useState(false);
  const [mode, setMode] = useState<"login" | "register">("login");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setAuthenticated(Boolean(window.localStorage.getItem("ai-job-match-token")));
    setLoading(false);
  }, []);

  if (loading) return <main className="shell"><p>Loading...</p></main>;
  if (authenticated) return <Dashboard />;

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const email = String(form.get("email") ?? "");
    const password = String(form.get("password") ?? "");
    const name = String(form.get("name") ?? "");
    try {
      setError("");
      if (mode === "register") await register(name, email, password);
      else await login(email, password);
      setAuthenticated(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Authentication failed");
    }
  }

  return (
    <main className="shell authShell">
      <section className="panel authPanel">
        <p className="eyebrow">AI JOB MATCH</p>
        <h1>{mode === "login" ? "Welcome back." : "Create your account."}</h1>
        <p className="muted">
          {mode === "login"
            ? "Sign in to see job recommendations based on your profile."
            : "Create a profile and start building your personalized job feed."}
        </p>
        {error && <div className="error">{error}</div>}
        <form className="authForm" onSubmit={submit}>
          {mode === "register" && <input name="name" required placeholder="Full name" />}
          <input name="email" type="email" required placeholder="Email" />
          <input name="password" type="password" minLength={8} required placeholder="Password (8+ characters)" />
          <button className="primary" type="submit">{mode === "login" ? "Sign in" : "Create account"}</button>
        </form>
        <button className="secondary authSwitch" onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(""); }}>
          {mode === "login" ? "New here? Create an account" : "Already have an account? Sign in"}
        </button>
      </section>
    </main>
  );
}
