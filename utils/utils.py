def safe_method_call(method):
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except Exception as e:
            print(f"[SafeCall] Error in {self.__class__.__name__}.{method.__name__}: {e}")
    return wrapper