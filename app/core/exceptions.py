class GameverseException(Exception):
    """Base exception for all gameverse operations."""
    def __init__(self, message: str, code: str = "GAME_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class InsufficientResourcesException(GameverseException):
    def __init__(self, message: str = "Resurslar yetarli emas!"):
        super().__init__(message, code="INSUFFICIENT_RESOURCES")


class BuildingPrerequisiteNotMetException(GameverseException):
    def __init__(self, message: str = "Bino qurish uchun talablar bajarilmagan!"):
        super().__init__(message, code="PREREQUISITE_NOT_MET")


class KingdomNotFoundException(GameverseException):
    def __init__(self, message: str = "Qirollik topilmadi!"):
        super().__init__(message, code="KINGDOM_NOT_FOUND")


class UserNotFoundException(GameverseException):
    def __init__(self, message: str = "Foydalanuvchi topilmadi!"):
        super().__init__(message, code="USER_NOT_FOUND")


class TroopRecruitException(GameverseException):
    def __init__(self, message: str = "Qo'shin yollashda xatolik!"):
        super().__init__(message, code="TROOP_RECRUIT_ERROR")


class BattleException(GameverseException):
    def __init__(self, message: str = "Jang o'tkazishda xatolik!"):
        super().__init__(message, code="BATTLE_ERROR")


class ShieldActiveException(GameverseException):
    def __init__(self, message: str = "Raqib qalqon himoyasida!"):
        super().__init__(message, code="SHIELD_ACTIVE")


class ClanException(GameverseException):
    def __init__(self, message: str = "Klan operatsiyasida xatolik!"):
        super().__init__(message, code="CLAN_ERROR")


class DuplicateTransactionException(GameverseException):
    def __init__(self, message: str = "Ushbu operatsiya allaqachon bajarilgan!"):
        super().__init__(message, code="DUPLICATE_TRANSACTION")
