from app.modules.user.model import User

class UserRepository:
    @staticmethod
    def get_all():
        return User.query.all()
