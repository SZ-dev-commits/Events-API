from models import User
from sqlalchemy.sql.functions import user


def test_user_password_hashing_behaves_correctly():
    user = User(username="John")
    user.set_password("pw123")

    assert user.username == "John"
    assert user.password_hash != "pw123"
    assert user.check_password("pw123") is True
    assert user.check_password("wrong_password") is False

