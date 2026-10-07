from app.services.learning import resources_for_skills


def test_learning_resources_are_returned_for_known_skills() -> None:
    resources = resources_for_skills(["sql", "unknown"])
    assert len(resources) == 1
    assert resources[0].skill == "sql"
