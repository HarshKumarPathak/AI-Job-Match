"use client";

import { useEffect, useMemo, useState } from "react";
import {
  getLearningResources,
  getRecommendations,
  getSkillGaps,
  LearningResource,
  Recommendation,
  SkillGap,
} from "../lib/api";

const CANDIDATE_ID = 1;

export default function Dashboard() {
  const [jobs, setJobs] = useState<Recommendation[]>([]);
  const [gaps, setGaps] = useState<SkillGap[]>([]);
  const [resources, setResources] = useState<LearningResource[]>([]);
  const [search, setSearch] = useState("");
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const [recommendations, skillGaps] = await Promise.all([
          getRecommendations(CANDIDATE_ID),
          getSkillGaps(CANDIDATE_ID),
        ]);
        setJobs(recommendations);
        setGaps(skillGaps);
        const topSkills = skillGaps.slice(0, 5).map((gap) => gap.skill);
        setResources(await getLearningResources(topSkills));
      } catch {
        setError("Backend data load nahi hua. API + database start karke demo data seed karo.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const filteredJobs = useMemo(
    () =>
      jobs.filter((job) => {
        const text = `${job.title} ${job.company} ${job.location ?? ""}`.toLowerCase();
        return text.includes(search.toLowerCase()) && (!remoteOnly || job.remote);
      }),
    [jobs, search, remoteOnly],
  );

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
        <div className="heroStat">
          <strong>{jobs.length}</strong>
          <span>recommended jobs</span>
        </div>
      </header>

      {error && <div className="error">{error}</div>}

      <section className="grid two">
        <div className="panel">
          <div className="panelHead">
            <div>
              <p className="eyebrow">RECOMMENDATIONS</p>
              <h2>Best matches</h2>
            </div>
            <div className="filters">
              <input
                placeholder="Search jobs..."
                value={search}
                onChange={(event) => setSearch(event.target.value)}
              />
              <button
                className={remoteOnly ? "active" : ""}
                onClick={() => setRemoteOnly((value) => !value)}
              >
                Remote
              </button>
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
                  <span>{job.remote ? "Remote" : "On-site"}</span>
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
                <div>
                  <strong>{gap.skill}</strong>
                  <span>{gap.jobs_requiring_skill} recommended jobs</span>
                </div>
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
    </main>
  );
}
