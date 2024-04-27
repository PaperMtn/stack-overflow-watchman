
class MissingEnvVarError(Exception):
    """ Exception raised when an environment variable is missing.
    """

    def __init__(self, env_var):
        self.env_var = env_var
        self.message = f'Missing Environment Variable: {self.env_var}'
        super().__init__(self.message)
