const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Recommendation = {
  job_id: number;
  title: string;
  company: string;
  location: string | null;
  remote: boolean;
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
