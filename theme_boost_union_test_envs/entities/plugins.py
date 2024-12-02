from enum import Enum


class MoodlePlugin(str, Enum):
    def __str__(self) -> str:
        return str(self.value)

    BOOST_UNION = "boost_union"
    BOOKIT = "bookit"
    AVAILABILITY_PASSWORD = "availability_password"
