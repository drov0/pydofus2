class NotificationTypeEnum:

    TUTORIAL: int = 0

    ERROR: int = 1

    INVITATION: int = 2

    PRIORITY_INVITATION: int = 3

    INFORMATION: int = 4

    SERVER_INFORMATION: int = 5

    SURVEY_INVITATION: int = 6

    WARNING: int = 7

    NOTIFICATION_PRIORITY: list = [
        ERROR,
        WARNING,
        PRIORITY_INVITATION,
        INVITATION,
        SERVER_INFORMATION,
        INFORMATION,
        TUTORIAL,
        SURVEY_INVITATION,
    ]
