const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Recommendation = {
  job_id: number;
  title: string;
  company: string;
  location: string | null;
  remote: boolean;
  employment_type: string | null;
  source: string | null;
  apply_url: string | null;
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  reasons: string[];
};

export type SkillGap = {
  skill: string;
  priority: number;
  jobs_requiring_skill: number;
  reason: string;
};

export type LearningResource = {
  skill: string;
  level: string;
  resource_type: string;
  title: string;
  url: string;
  reason: string;
};

export type ApplicationStatus = "saved" | "applied" | "interview" | "rejected" | "offer";

export type Application = {
  id: number;
  candidate_id: number;
  job_id: number;
  status: ApplicationStatus;
  notes: string;
  applied_at: string | null;
  updated_at: string;
};

export type SavedJob = {
  id: number;
  candidate_id: number;
  job_id: number;
  created_at: string;
};

export type JobAlert = {
  id: number;
  candidate_id: number;
  minimum_score: number;
  enabled: boolean;
  created_at: string;
};

export type AlertMatch = {
  job_id: number;
  title: string;
  company: string;
  score: number;
  apply_url: string | null;
};

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init);
  if (!response.ok) throw new Error((await response.text()) || "Request failed");
  return response.json();
}

export async function getRecommendations(
  candidateId: number,
  filters: { q?: string; remote?: boolean; location?: string; employmentType?: string; source?: string } = {},
): Promise<Recommendation[]> {
  const params = new URLSearchParams({ limit: "20" });
  if (filters.q) params.set("q", filters.q);
  if (filters.remote !== undefined) params.set("remote", String(filters.remote));
  if (filters.location) params.set("location", filters.location);
  if (filters.employmentType) params.set("employment_type", filters.employmentType);
  if (filters.source) params.set("source", filters.source);

  return request<Recommendation[]>(
    `${API_URL}/recommendations/${candidateId}?${params.toString()}`,
    { cache: "no-store" },
  );
}

export async function getSkillGaps(candidateId: number): Promise<SkillGap[]> {
  const data = await request<{ candidate_id: number; analyzed_jobs: number; gaps: SkillGap[] }>(
    `${API_URL}/skill-gaps/${candidateId}?job_limit=10`,
    { cache: "no-store" },
  );
  return data.gaps;
}

export async function getLearningResources(skills: string[]): Promise<LearningResource[]> {
  if (!skills.length) return [];
  const params = new URLSearchParams();
  skills.forEach((skill) => params.append("skills", skill));
  return request<LearningResource[]>(`${API_URL}/learning?${params.toString()}`, { cache: "no-store" });
}

export async function createCandidate(payload: {
  name: string;
  email: string;
  preferred_roles: string[];
  preferred_locations: string[];
  experience_years: number;
  education: string;
}): Promise<{ id: number }> {
  return request<{ id: number }>(`${API_URL}/candidates`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function uploadResume(candidateId: number, file: File): Promise<void> {
  const form = new FormData();
  form.append("file", file);
  await request(`${API_URL}/candidates/${candidateId}/resumes`, { method: "POST", body: form });
}

export async function saveJob(candidateId: number, jobId: number): Promise<SavedJob> {
  return request<SavedJob>(`${API_URL}/tracking/saved`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ candidate_id: candidateId, job_id: jobId }),
  });
}

export async function getSavedJobs(candidateId: number): Promise<SavedJob[]> {
  return request<SavedJob[]>(`${API_URL}/tracking/saved/${candidateId}`, { cache: "no-store" });
}

export async function createApplication(candidateId: number, jobId: number): Promise<Application> {
  return request<Application>(`${API_URL}/tracking/applications`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ candidate_id: candidateId, job_id: jobId, status: "applied", notes: "" }),
  });
}

export async function getApplications(candidateId: number): Promise<Application[]> {
  return request<Application[]>(`${API_URL}/tracking/applications/${candidateId}`, { cache: "no-store" });
}

export async function updateApplication(
  applicationId: number,
  status: ApplicationStatus,
  notes = "",
): Promise<Application> {
  return request<Application>(`${API_URL}/tracking/applications/${applicationId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status, notes }),
  });
}

export async function getAlert(candidateId: number): Promise<JobAlert | null> {
  const response = await fetch(`${API_URL}/alerts/${candidateId}`, { cache: "no-store" });
  if (response.status === 404) return null;
  if (!response.ok) throw new Error("Could not load alert");
  return response.json();
}

export async function createOrUpdateAlert(candidateId: number, minimumScore: number): Promise<JobAlert> {
  return request<JobAlert>(`${API_URL}/alerts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ candidate_id: candidateId, minimum_score: minimumScore }),
  });
}

export async function updateAlert(
  alertId: number,
  minimumScore: number,
  enabled: boolean,
): Promise<JobAlert> {
  return request<JobAlert>(`${API_URL}/alerts/${alertId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ minimum_score: minimumScore, enabled }),
  });
}

export async function checkAlert(candidateId: number): Promise<AlertMatch[]> {
  return request<AlertMatch[]>(`${API_URL}/alerts/${candidateId}/matches`, { cache: "no-store" });
}
