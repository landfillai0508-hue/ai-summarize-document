"""customized exception module."""


class LargeLanguageAPIError(Exception):

    def __init__(self):
        super().__init__("Calling large language model api failed.")


class NoReportSatisfyAllMustRequirements(Exception):

    def __init__(self):
        super().__init__("No report satisfy all must requirements.")
