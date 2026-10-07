const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Recommendation = {
  job_id: number;
  title: string;
  company: string;
  location: string | null;
  remote: boolean;
  employment_type: string | null;
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

export async function getRecommendations(candidateId: number): Promise<Recommendation[]> {
  const response = await fetch(
    `${API_URL}/recommendations/${candidateId}?limit=10`,
    { cache: "no-store" },
  );
  if (!response.ok) throw new Error("Could not load recommendations");
  return response.json();
}

export async function getSkillGaps(candidateId: number): Promise<SkillGap[]> {
  const response = await fetch(
    `${API_URL}/skill-gaps/${candidateId}?job_limit=10`,
    { cache: "no-store" },
  );
  if (!response.ok) throw new Error("Could not load skill gaps");
  const data = await response.json();
  return data.gaps;
}

export async function getLearningResources(skills: string[]): Promise<LearningResource[]> {
  if (!skills.length) return [];
  const params = new URLSearchParams();
  skills.forEach((skill) => params.append("skills", skill));
  const response = await fetch(`${API_URL}/learning?${params.toString()}`, {
    cache: "no-store",
  });
  if (!response.ok) throw new Error("Could not load learning resources");
  return response.json();
}

export async function createCandidate(payload: {
  name: string;
  email: string;
  preferred_roles: string[];
  preferred_locations: string[];
  experience_years: number;
  education: string;
}): Promise<{ id: number }> {
  const response = await fetch(`${API_URL}/candidates`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error("Could not create candidate");
  return response.json();
}

export async function uploadResume(candidateId: number, file: File): Promise<void> {
  const form = new FormData();
  form.append("file", file);
  const response = await fetch(`${API_URL}/candidates/${candidateId}/resumes`, {
    method: "POST",
    body: form,
  });
  if (!response.ok) throw new Error("Could not upload resume");
}
