"use client";

import { useEffect, useMemo, useState } from "react";
import {
  createCandidate,
  getLearningResources,
  getRecommendations,
  getSkillGaps,
  getApplications,
  createApplication,
  saveJob,
  LearningResource,
  Recommendation,
  SkillGap,
  uploadResume,
} from "../lib/api";

const DEFAULT_CANDIDATE_ID = 1;

export default function Dashboard() {
  const [candidateId, setCandidateId] = useState(DEFAULT_CANDIDATE_ID);
  const [jobs, setJobs] = useState<Recommendation[]>([]);
  const [gaps, setGaps] = useState<SkillGap[]>([]);
  const [resources, setResources] = useState<LearningResource[]>([]);
  const [search, setSearch] = useState("");
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [profileOpen, setProfileOpen] = useState(false);
  const [applications, setApplications] = useState<Record<number, string>>({});

  useEffect(() => {
    const saved = window.localStorage.getItem("ai-job-match-candidate");
    if (saved) setCandidateId(Number(saved));
  }, []);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        setError("");
        const [recommendations, skillGaps] = await Promise.all([
          getRecommendations(candidateId),
          getSkillGaps(candidateId),
        ]);
        setJobs(recommendations);
        setGaps(skillGaps);
        setResources(await getLearningResources(skillGaps.slice(0, 5).map((gap) => gap.skill)));
        const tracked = await getApplications(candidateId);
        setApplications(Object.fromEntries(tracked.map((item) => [item.job_id, item.status])));
      } catch {
        setError("Profile/job data load nahi hua. Pehle profile setup karo aur demo jobs seed karo.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [candidateId]);

  const filteredJobs = useMemo(
    () =>
      jobs.filter((job) => {
        const text = `${job.title} ${job.company} ${job.location ?? ""}`.toLowerCase();
        return text.includes(search.toLowerCase()) && (!remoteOnly || job.remote);
      }),
    [jobs, search, remoteOnly],
  );

  async function saveProfile(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      const candidate = await createCandidate({
        name: String(form.get("name") ?? ""),
        email: String(form.get("email") ?? ""),
        preferred_roles: String(form.get("roles") ?? "").split(",").map((x) => x.trim()).filter(Boolean),
        preferred_locations: String(form.get("locations") ?? "").split(",").map((x) => x.trim()).filter(Boolean),
        experience_years: Number(form.get("experience") ?? 0),
        education: String(form.get("education") ?? ""),
      });
      const file = form.get("resume");
      if (file instanceof File && file.size > 0) await uploadResume(candidate.id, file);
      window.localStorage.setItem("ai-job-match-candidate", String(candidate.id));
      setCandidateId(candidate.id);
      setProfileOpen(false);
    } catch {
      setError("Profile save nahi hua. API check karo.");
    }
  }

  if (loading) return <main className="shell"><p>Loading your job matches...</p></main>;

  return (
    <main className="shell">
      <header className="hero">
        <div>
          <p className="eyebrow">AI JOB MATCH</p>
          <h1>Find jobs that fit you.</h1>
          <p className="muted">
            Recommendations are based on your current skills, preferred role and job requirements.
          </p>
        </div>
        <div className="heroActions">
          <button className="primary" onClick={() => setProfileOpen(true)}>Update profile</button>
          <div className="heroStat">
            <strong>{jobs.length}</strong>
            <span>recommended jobs</span>
          </div>
        </div>
      </header>

      {error && <div className="error">{error}</div>}

      {profileOpen && (
        <form className="panel profile" onSubmit={saveProfile}>
          <div className="panelHead">
            <div>
              <p className="eyebrow">PROFILE</p>
              <h2>Tell us about yourself</h2>
            </div>
            <button type="button" onClick={() => setProfileOpen(false)}>Close</button>
          </div>
          <div className="formGrid">
            <input name="name" required placeholder="Name" />
            <input name="email" type="email" required placeholder="Email" />
            <input name="roles" placeholder="Preferred roles (e.g. AI Engineer, Backend)" />
            <input name="locations" placeholder="Preferred locations (e.g. Remote, Bengaluru)" />
            <input name="experience" type="number" min="0" step="0.5" placeholder="Experience years" />
            <input name="education" placeholder="Education" />
            <label className="fileInput">Resume (PDF/DOCX/TXT)<input name="resume" type="file" accept=".pdf,.docx,.txt" /></label>
          </div>
          <button className="primary" type="submit">Save profile & resume</button>
        </form>
      )}

      <section className="grid two">
        <div className="panel">
          <div className="panelHead">
            <div>
              <p className="eyebrow">RECOMMENDATIONS</p>
              <h2>Best matches</h2>
            </div>
            <div className="filters">
              <input placeholder="Search jobs..." value={search} onChange={(event) => setSearch(event.target.value)} />
              <button className={remoteOnly ? "active" : ""} onClick={() => setRemoteOnly((value) => !value)}>Remote</button>
            </div>
          </div>

          <div className="jobList">
            {filteredJobs.map((job) => (
              <article className="jobCard" key={job.job_id}>
                <div className="jobTop">
                  <div>
                    <h3>{job.title}</h3>
                    <p>{job.company} · {job.location ?? "Location not listed"}</p>
                  </div>
                  <span className="score">{Math.round(job.match_score)}% match</span>
                </div>
                <div className="chips">
                  {job.matched_skills.map((skill) => <span className="chip good" key={skill}>{skill}</span>)}
                  {job.missing_skills.slice(0, 4).map((skill) => <span className="chip missing" key={skill}>{skill}</span>)}
                </div>
                <div className="jobFooter">
                  <p>{job.reasons.join(" · ")}</p>
                  {job.apply_url ? <div className="jobActions"><button className="save" onClick={() => saveJob(candidateId, job.job_id).catch(() => setError("Job save nahi hua."))}>Save</button><a className="apply" href={job.apply_url} target="_blank" rel="noreferrer" onClick={() => createApplication(candidateId, job.job_id).then(() => setApplications((current) => ({ ...current, [job.job_id]: "applied" }))).catch(() => setError("Application track nahi hui."))}>Apply →</a></div> : <span>{job.remote ? "Remote" : "On-site"}</span>}
                </div>
              </article>
            ))}
            {!filteredJobs.length && <p className="muted">No jobs match these filters.</p>}
          </div>
        </div>

        <aside className="panel">
          <p className="eyebrow">SKILL GAP</p>
          <h2>What to learn next</h2>
          <p className="muted">Skills that appear most often among your recommended jobs.</p>
          <div className="gapList">
            {gaps.slice(0, 8).map((gap) => (
              <div className="gap" key={gap.skill}>
                <div><strong>{gap.skill}</strong><span>{gap.jobs_requiring_skill} recommended jobs</span></div>
                <b>{gap.priority}</b>
              </div>
            ))}
            {!gaps.length && <p className="muted">No major skill gaps found yet.</p>}
          </div>
        </aside>
      </section>

      <section className="panel resources">
        <div>
          <p className="eyebrow">LEARNING</p>
          <h2>Useful resources</h2>
        </div>
        <div className="resourceGrid">
          {resources.map((resource) => (
            <a className="resource" href={resource.url} target="_blank" rel="noreferrer" key={resource.skill}>
              <span>{resource.resource_type}</span>
              <h3>{resource.title}</h3>
              <p>Improve <strong>{resource.skill}</strong> · {resource.level}</p>
            </a>
          ))}
        </div>
      </section>

      <section className="panel tracking">
        <p className="eyebrow">APPLICATIONS</p>
        <h2>Your application progress</h2>
        <div className="trackingGrid">
          {Object.entries(applications).map(([jobId, status]) => {
            const job = jobs.find((item) => item.job_id === Number(jobId));
            return job ? <div className="trackingCard" key={jobId}><strong>{job.title}</strong><span>{job.company}</span><b>{status}</b></div> : null;
          })}
          {!Object.keys(applications).length && <p className="muted">Apply to a recommended job and it will appear here.</p>}
        </div>
      </section>
    </main>
  );
}
