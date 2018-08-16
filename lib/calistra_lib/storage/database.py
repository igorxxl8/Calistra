# TODO: 1) дописать документацию
# TODO: 2) Рефакторинг
# TODO: 3) Логирование


class Database:
    def __init__(self, filename, cls_seq=None):
        self.cls_seq = cls_seq
        self.filename = filename

    def load(self):
        pass

    def unload(self, instance):
        pass
