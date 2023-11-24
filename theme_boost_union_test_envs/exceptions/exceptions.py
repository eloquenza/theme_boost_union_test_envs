class BoostUnionTestEnvValueError(ValueError):
    """Base class for all our value errors in our application.

    Args:
        ValueError (_type_): Our super class.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class VersionArgumentNeededError(BoostUnionTestEnvValueError):
    """Exception raised if a mandatory version parameter has been skipped on any of the varargs method that allow a variable number of versions."""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class NameAlreadyTakenError(BoostUnionTestEnvValueError):
    """Exception raised if the new name for a test infrastructure is already in use"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InvalidGitReferenceError(BoostUnionTestEnvValueError):
    """Exception raised if the git reference given to `init` is not a valid git reference, either it's type is not valid or the reference itself is not valid."""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class UserInterfaceNotYetImplemented(BoostUnionTestEnvValueError):
    """Exception raised if the chosen user interface type has not been implemented yet"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InfrastructureDoesNotExistYetError(BoostUnionTestEnvValueError):
    """Exception raised if user tries to issue commands for an infrastructure that has not yet been initialized"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class TestbedDoesNotExistYetError(BoostUnionTestEnvValueError):
    """Exception raised if user tries to issue commands for an infrastructure but the test bed itself has not been initialized yet"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class MoodleTestEnvironmentDoesNotExistYetError(BoostUnionTestEnvValueError):
    """Exception raised if user tries to use commands on an moodle test container that has not yet been created"""

    def __init__(self, version: str, *args: object) -> None:
        super().__init__(*args)
        self.version = version


class InvalidMoodleVersionError(BoostUnionTestEnvValueError):
    """Exception raised if user tries to issue a download or test container for an invalid/unknown/non-existing Moodle version"""

    def __init__(self, version: str, *args: object) -> None:
        super().__init__(*args)
        self.version = version


class UnsupportedMoodleVersionError(BoostUnionTestEnvValueError):
    """Exception raised if user tries to issue a download or test container for an unsupported (i.e. too old) Moodle version"""

    def __init__(self, version: str, *args: object) -> None:
        super().__init__(*args)
        self.version = version
