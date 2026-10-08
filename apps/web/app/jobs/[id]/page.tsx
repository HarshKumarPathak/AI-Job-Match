import Link from "next/link";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function getJob(id: string) {
  const response = await fetch(`${API_URL}/jobs/${id}`, { cache: "no-store" });
  if (!response.ok) return null;
  return response.json();
}

export default async function JobPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const job = await getJob(id);

  if (!job) {
    return <main className="shell"><div className="panel"><h1>Job not found</h1><Link href="/">← Back to matches</Link></div></main>;
  }

  return (
    <main className="shell">
      <div className="panel jobDetail">
        <Link href="/" className="backLink">← Back to matches</Link>
        <p className="eyebrow">{job.source ?? "JOB"}</p>
        <h1>{job.title}</h1>
        <p className="detailCompany">{job.company} · {job.location ?? "Location not listed"}</p>
        <div className="chips">
          {job.remote && <span className="chip good">Remote</span>}
          {job.employment_type && <span className="chip">{job.employment_type}</span>}
          {job.salary_min != null && <span className="chip">Salary from {job.salary_min}</span>}
          {job.salary_max != null && <span className="chip">Salary up to {job.salary_max}</span>}
        </div>
        <h2>Job description</h2>
        <div className="description">{job.description}</div>
        {job.apply_url && <a className="apply detailApply" href={job.apply_url} target="_blank" rel="noreferrer">Apply for this job →</a>}
      </div>
    </main>
  );
}
