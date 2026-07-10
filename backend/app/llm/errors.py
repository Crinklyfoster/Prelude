class ProviderError(Exception):
    pass

class RetryableProviderError(ProviderError):
    pass

class FatalProviderError(ProviderError):
    pass
