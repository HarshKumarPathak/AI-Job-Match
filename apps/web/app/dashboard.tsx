"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Application,
  ApplicationStatus,
  AlertMatch,
  JobAlert,
  createApplication,
  createCandidate,
  createOrUpdateAlert,
  checkAlert,
  getApplications,
  getAlert,
  getLearningResources,
  getRecommendations,
  refreshRecommendations,
  getSavedJobs,
  getSkillGaps,
  saveJob,
  updateAlert,
  updateApplication,
  uploadResume,
  logout,
  LearningResource,
  Recommendation,
  SkillGap,
} from "../lib/api";

const DEFAULT_CANDIDATE_ID = 1;
const STATUSES: ApplicationStatus[] = ["saved", "applied", "interview", "rejected", "offer"];

export default function Dashboard() {
  const [candidateId, setCandidateId] = useState(DEFAULT_CANDIDATE_ID);
  const [jobs, setJobs] = useState<Recommendation[]>([]);
  const [gaps, setGaps] = useState<SkillGap[]>([]);
  const [resources, setResources] = useState<LearningResource[]>([]);
  const [search, setSearch] = useState("");
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [location, setLocation] = useState("");
  const [employmentType, setEmploymentType] = useState("");
  const [source, setSource] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [profileOpen, setProfileOpen] = useState(false);
  const [applications, setApplications] = useState<Application[]>([]);
  const [savedJobIds, setSavedJobIds] = useState<Set<number>>(new Set());
  const [alert, setAlert] = useState<JobAlert | null>(null);
  const [alertMatches, setAlertMatches] = useState<AlertMatch[]>([]);
  const [alertScore, setAlertScore] = useState(70);
  const [alertOpen, setAlertOpen] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    const saved = window.localStorage.getItem("ai-job-match-candidate");
    if (saved) setCandidateId(Number(saved));
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      async function load() {
        try {
          setLoading(true);
          setError("");
          const [recommendations, skillGaps, tracked, saved, existingAlert] = await Promise.all([
            getRecommendations(candidateId, {
              q: search || undefined,
              remote: remoteOnly ? true : undefined,
              location: location || undefined,
              employmentType: employmentType || undefined,
              source: source || undefined,
            }),
            getSkillGaps(candidateId),
            getApplications(candidateId),
            getSavedJobs(candidateId),
            getAlert(candidateId),
          ]);
          setJobs(recommendations);
          setGaps(skillGaps);
          setApplications(tracked);
          setSavedJobIds(new Set(saved.map((item) => item.job_id)));
          setAlert(existingAlert);
          if (existingAlert) setAlertScore(existingAlert.minimum_score);
          setResources(await getLearningResources(skillGaps.slice(0, 5).map((gap) => gap.skill)));
          const matches = await checkAlert(candidateId);
          setAlertMatches(matches);
        } catch {
          setError("Profile/job data load nahi hua. Pehle profile setup karo aur demo jobs seed karo.");
        } finally {
          setLoading(false);
        }
      }

      void load();
    }, 300);

    return () => window.clearTimeout(timer);
  }, [candidateId, search, remoteOnly, location, employmentType, source, refreshKey]);

  const savedJobs = useMemo(
    () => jobs.filter((job) => savedJobIds.has(job.job_id)),
    [jobs, savedJobIds],
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
      setRefreshKey((value) => value + 1);
    } catch {
      setError("Profile save nahi hua. API check karo.");
    }
  }

  async function handleSave(jobId: number) {
    try {
      await saveJob(candidateId, jobId);
      setSavedJobIds((current) => new Set(current).add(jobId));
    } catch {
      setError("Job save nahi hua.");
    }
  }

  async function handleApply(jobId: number) {
    try {
      const application = await createApplication(candidateId, jobId);
      setApplications((current) => {
        const remaining = current.filter((item) => item.job_id !== jobId);
        return [application, ...remaining];
      });
    } catch {
      setError("Application track nahi hui.");
    }
  }

  async function handleStatusChange(application: Application, status: ApplicationStatus) {
    try {
      const updated = await updateApplication(application.id, status, application.notes);
      setApplications((current) => current.map((item) => item.id === updated.id ? updated : item));
    } catch {
      setError("Application status update nahi hua.");
    }
  }

  async function handleRefreshRecommendations() {
    try {
      setLoading(true);
      setError("");
      const refreshed = await refreshRecommendations(candidateId, {
        q: search || undefined,
        remote: remoteOnly ? true : undefined,
        location: location || undefined,
        employmentType: employmentType || undefined,
        source: source || undefined,
      });
      setJobs(refreshed);
    } catch {
      setError("Recommendations refresh nahi hue. API check karo.");
    } finally {
      setLoading(false);
    }
  }

  async function handleAlert() {
    try {
      const updated = await createOrUpdateAlert(candidateId, alertScore);
      setAlert(updated);
      setAlertOpen(false);
      setAlertMatches(await checkAlert(candidateId));
    } catch {
      setError("Alert save nahi hua.");
    }
  }

  if (loading) return <main className="shell"><p>Loading your job matches...</p></main>;

  return (
    <main className="shell">
      <header className="hero">
        <div>
          <p className="eyebrow">AI JOB MATCH</p>
          <h1>Find jobs that fit you.</h1>
          <p className="muted">Ranked using your skills, resume text, preferred role, location and job requirements.</p>
        </div>
        <div className="heroActions">
          <button className="primary" onClick={() => setProfileOpen(true)}>Update profile</button>
          <button className="secondary" onClick={() => setAlertOpen(true)}>Job alert</button>
          <button className="secondary" onClick={() => { logout(); window.location.reload(); }}>Sign out</button>
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
            <div><p className="eyebrow">PROFILE</p><h2>Tell us about yourself</h2></div>
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

      {alertOpen && (
        <section className="panel alertPanel">
          <div className="panelHead">
            <div><p className="eyebrow">ALERTS</p><h2>Get notified about strong matches</h2></div>
            <button type="button" onClick={() => setAlertOpen(false)}>Close</button>
          </div>
          <p className="muted">Set the minimum match score you want to consider a strong job match.</p>
          <div className="alertForm">
            <label>Minimum score <input type="number" min="0" max="100" value={alertScore} onChange={(e) => setAlertScore(Number(e.target.value))} /></label>
            <button className="primary" onClick={handleAlert}>Save alert</button>
          </div>
        </section>
      )}

      <section className="panel filterPanel">
        <div className="panelHead">
          <div><p className="eyebrow">SEARCH & FILTERS</p><h2>Refine your matches</h2></div>
        </div>
        <div className="filters wide">
          <input placeholder="Search title, company or description..." value={search} onChange={(e) => setSearch(e.target.value)} />
          <input placeholder="Location" value={location} onChange={(e) => setLocation(e.target.value)} />
          <select value={employmentType} onChange={(e) => setEmploymentType(e.target.value)}>
            <option value="">Any employment type</option>
            <option value="internship">Internship</option>
            <option value="full-time">Full-time</option>
            <option value="part-time">Part-time</option>
            <option value="contract">Contract</option>
          </select>
          <input placeholder="Source" value={source} onChange={(e) => setSource(e.target.value)} />
          <button className={remoteOnly ? "active" : ""} onClick={() => setRemoteOnly((value) => !value)}>Remote only</button>
        </div>
      </section>

      <section className="grid two">
        <div className="panel">
          <div className="panelHead">
            <div><p className="eyebrow">RECOMMENDATIONS</p><h2>Best matches</h2></div>
            <div className="panelActions">
              <span className="muted">{jobs.length} results</span>
              <button className="secondary" onClick={handleRefreshRecommendations}>Refresh matches</button>
            </div>
          </div>
          <div className="jobList">
            {jobs.map((job) => (
              <article className="jobCard" key={job.job_id}>
                <div className="jobTop">
                  <div>
                    <h3><a className="jobTitleLink" href={`/jobs/${job.job_id}`}>{job.title}</a></h3>
                    <p>{job.company} · {job.location ?? "Location not listed"} · {job.employment_type ?? "Type not listed"} · {job.source ?? "Source not listed"}</p>
                  </div>
                  <span className="score">{Math.round(job.match_score)}% match</span>
                </div>
                <div className="chips">
                  {job.matched_skills.map((skill) => <span className="chip good" key={skill}>✓ {skill}</span>)}
                  {job.missing_skills.slice(0, 4).map((skill) => <span className="chip missing" key={skill}>Need {skill}</span>)}
                </div>
                <div className="jobFooter">
                  <p>{job.reasons.join(" · ")}</p>
                  {job.apply_url ? (
                    <div className="jobActions">
                      <button className="save" onClick={() => handleSave(job.job_id)} disabled={savedJobIds.has(job.job_id)}>
                        {savedJobIds.has(job.job_id) ? "Saved" : "Save"}
                      </button>
                      <a className="apply" href={job.apply_url} target="_blank" rel="noreferrer" onClick={() => handleApply(job.job_id)}>Apply →</a>
                    </div>
                  ) : <span>{job.remote ? "Remote" : "On-site"}</span>}
                </div>
              </article>
            ))}
            {!jobs.length && <p className="muted">No jobs match these filters.</p>}
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
        <div><p className="eyebrow">LEARNING</p><h2>Useful resources</h2></div>
        <div className="resourceGrid">
          {resources.map((resource) => (
            <a className="resource" href={resource.url} target="_blank" rel="noreferrer" key={resource.skill}>
              <span>{resource.resource_type}</span><h3>{resource.title}</h3>
              <p>Improve <strong>{resource.skill}</strong> · {resource.level}</p>
            </a>
          ))}
        </div>
      </section>

      <section className="panel tracking">
        <div className="panelHead">
          <div><p className="eyebrow">APPLICATIONS</p><h2>Your application progress</h2></div>
          <span className="muted">{applications.length} tracked</span>
        </div>
        <div className="trackingGrid">
          {applications.map((application) => {
            const job = jobs.find((item) => item.job_id === application.job_id);
            return (
              <div className="trackingCard" key={application.id}>
                <strong>{job?.title ?? `Job #${application.job_id}`}</strong>
                <span>{job?.company ?? "Saved application"}</span>
                <select value={application.status} onChange={(e) => handleStatusChange(application, e.target.value as ApplicationStatus)}>
                  {STATUSES.map((status) => <option value={status} key={status}>{status}</option>)}
                </select>
              </div>
            );
          })}
          {!applications.length && <p className="muted">Apply to a recommended job and it will appear here.</p>}
        </div>
      </section>

      <section className="panel savedPanel">
        <p className="eyebrow">SAVED JOBS</p>
        <h2>Jobs you want to revisit</h2>
        <div className="savedList">
          {savedJobs.map((job) => <div className="savedItem" key={job.job_id}><strong>{job.title}</strong><span>{job.company}</span>{job.apply_url && <a href={job.apply_url} target="_blank" rel="noreferrer">Open job →</a>}</div>)}
          {!savedJobs.length && <p className="muted">Save a job to keep it on your list.</p>}
        </div>
      </section>

      <section className="panel alertResults">
        <div className="panelHead">
          <div><p className="eyebrow">JOB ALERT</p><h2>{alert ? `Matches above ${Math.round(alert.minimum_score)}%` : "No alert configured yet"}</h2></div>
          {alert && <button className="secondary" onClick={async () => {
            try {
              const updated = await updateAlert(alert.id, alert.minimum_score, !alert.enabled);
              setAlert(updated);
            } catch { setError("Alert update nahi hua."); }
          }}>{alert.enabled ? "Pause alert" : "Enable alert"}</button>}
        </div>
        {alertMatches.length ? <div className="alertList">{alertMatches.slice(0, 5).map((match) => <div className="alertItem" key={match.job_id}><strong>{match.title}</strong><span>{match.company} · {Math.round(match.score)}% match</span></div>)}</div> : <p className="muted">No current jobs cross your alert threshold.</p>}
      </section>
    </main>
  );
}
