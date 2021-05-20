class DatabaseRouter(object):
    def db_for_read(self, model, **hints):
        # Points all read operations in 'database' app to 'dev1'
        if model._meta.app_label == 'database':
            return 'dev1'
        else:
            return 'default'

    def db_for_write(self, model, **hints):
        # Points all write operations in "database" app to 'dev1'
        if model._meta.app_label == 'database':
            return 'dev1'
        else:
            return 'default'

    def allow_relation(self, ob1, ob2, **hints):
        db_set = {'default', 'dev1'}

        if ob1._state.db in db_set and ob2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True
