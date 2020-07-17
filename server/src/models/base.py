from sqlalchemy.exc import DatabaseError

from extensions import db


class _BaseCRUD(object):
    """Clase base que añade la funcionalidad CRUD al modelo que herede esta clase.
       Tambien gestiona to-do lo relacionado con las sesiones"""

    def save(self):
        db.session.add(self)
        self._commit()
        return self

    def update(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return self.save()

    def delete(self):
        db.session.delete(self)
        self._commit()

    def _commit(self):
        try:
            db.session.commit()
        except DatabaseError as e:
            db.session.rollback()
            raise e
        return self


class BaseModel(_BaseCRUD, db.Model):
    """Clase abstracta base que incluye los metodos crud"""

    __abstract__ = True
