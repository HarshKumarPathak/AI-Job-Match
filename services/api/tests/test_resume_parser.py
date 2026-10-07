from app.services.resume_parser import extract_text


def test_txt_resume_extraction() -> None:
    data = b"Harsh Kumar\nPython SQL Machine Learning"
    assert extract_text("resume.txt", data) == "Harsh Kumar\nPython SQL Machine Learning"


def test_unsupported_resume_format() -> None:
    try:
        extract_text("resume.exe", b"not a resume")
    except ValueError as exc:
        assert "Unsupported resume format" in str(exc)
    else:
        raise AssertionError("Expected unsupported format error")
