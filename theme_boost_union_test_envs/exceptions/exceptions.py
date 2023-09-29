class BoostUnionTestEnvValueError(ValueError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


# if version argument has been skipped on varargs methods
class VersionArgumentNeededError(BoostUnionTestEnvValueError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


# if the name for the test infrastructure is already in use
class NameAlreadyTakenError(BoostUnionTestEnvValueError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


# if the git reference given to `init` is not a valid git reference
class InvalidGitReferenceError(BoostUnionTestEnvValueError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


# if the chosen user interface type has not been implemented yet
class UserInterfaceNotYetImplemented(BoostUnionTestEnvValueError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


# if user tries to use commands on an infrastructure that has not yet been initialized
class InfrastructureDoesNotExistYetError(BoostUnionTestEnvValueError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
