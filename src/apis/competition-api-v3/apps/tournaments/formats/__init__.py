class FormatRegistry:
    _engines = {}

    @classmethod
    def register(cls, format_name, format_class):
        cls._engines[format_name] = format_class

    @classmethod
    def get_format(cls, format_name):
        return cls._engines.get(format_name)
