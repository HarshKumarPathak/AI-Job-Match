from app.services.resume_profile import infer_profile

def test_infer_profile_from_resume_text():
    result = infer_profile("B.Tech CSE. Machine Learning Engineer. 2 years of experience.")
    assert result["education"] == "b.tech cse. machine learning engineer. 2 years of experience."
    assert "machine learning engineer" in result["preferred_roles"]
    assert result["experience_years"] == 2.0
