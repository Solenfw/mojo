from app.modules.user.repository import UserRepository

class UserService:
    @staticmethod
    def get_users():
        return UserRepository.get_all()
