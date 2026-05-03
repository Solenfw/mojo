from server.app.db import models


def test_users_model_has_expected_fields():
    assert models.Users.__tablename__ == "users"
    assert hasattr(models.Users, "username")
    assert hasattr(models.Users, "email")
    assert hasattr(models.Users, "hashed_password")
