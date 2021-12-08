class CodeRouter:
    
    allow_app_label = ["CodeModel"]
    db_name = "Code"

    def db_for_read(self, model, **kwargs):
        if model._meta.app_label in self.allow_app_label:           # noqa
            return self.db_name

    def db_for_write(self, model, **kwargs):
        if model._meta.app_label in self.allow_app_label:           # noqa
            return self.db_name

    def allow_relation(self, object1, object2, **kwargs):
        if (object1._meta.app_label in self.allow_app_label or      # noqa
                object2._meta.app_label in self.allow_app_label):   # noqa
            return True
        return None

    def allow_migrate(self, db, app_label, model=None, **kwargs):
        if app_label in self.allow_app_label:
            return db == self.db_name
        return None
