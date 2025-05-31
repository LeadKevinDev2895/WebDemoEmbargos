from app import db
from app.models.entidad import Entidad

class EntidadRepository:
    @staticmethod
    def get_by_id(entidad_id):
        """Obtiene una Entidad por ID"""
        return Entidad.query.get(entidad_id)

    @staticmethod
    def get_all():
        """Obtiene todas las Entidades"""
        return Entidad.query.all()

    @staticmethod
    def create(data):
        """Crea una nueva Entidad"""
        entidad = Entidad(**data)
        db.session.add(entidad)
        db.session.commit()
        return entidad

    @staticmethod
    def update(entidad_id, data):
        """Actualiza una Entidad por ID"""
        entidad = Entidad.query.get(entidad_id)
        if not entidad:
            return None
        for key, value in data.items():
            setattr(entidad, key, value)
        db.session.commit()
        return entidad

    @staticmethod
    def delete(entidad_id):
        """Elimina una Entidad por ID"""
        entidad = Entidad.query.get(entidad_id)
        if not entidad:
            return None
        db.session.delete(entidad)
        db.session.commit()
        return True
