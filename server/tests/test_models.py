from app import models


def test_user_model_has_expected_fields():
    assert models.User.__tablename__ == "user"
    assert hasattr(models.User, "username")
    assert hasattr(models.User, "email")
    assert hasattr(models.User, "hashed_password")
