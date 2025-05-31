from app import db
from app.models.medida_cautelar import MedidaCautelar
from app.models.motivos import Motivo


class MotivoRepository:
    """Repository layer for managing Motivo database interactions."""

    @staticmethod
    def get_all():
        """Retrieve all records."""
        return Motivo.query.all()

    @staticmethod
    def get_by_id(record_id):
        """Retrieve a record by its ID."""
        return Motivo.query.get(record_id)

    @staticmethod
    def get_by_name(name):
        """Retrieve a motivo by its name."""
        return Motivo.query.filter_by(nombre=name).first()

    @staticmethod
    def create(data):
        """Create a new record."""
        new_record = Motivo(**data)
        db.session.add(new_record)
        db.session.commit()
        return new_record

    @staticmethod
    def update(record_id, data):
        """Update an existing record by its ID."""
        record = Motivo.query.get(record_id)
        if not record:
            return None
        for key, value in data.items():
            setattr(record, key, value)
        db.session.commit()
        return record

    @staticmethod
    def delete(record_id):
        """Delete a record by its ID."""
        record = Motivo.query.get(record_id)
        if record:
            db.session.delete(record)
            db.session.commit()
        return record

    @staticmethod
    def add_motivo_to_medida(medida_id, motivo_id):
        """Relaciona un motivo con una medida cautelar."""
        medida = MedidaCautelar.query.get(medida_id)
        motivo = Motivo.query.get(motivo_id)

        if not medida or not motivo:
            return None  # Manejar si alguno no existe

        if motivo not in medida.motivos:
            medida.motivos.append(motivo)
            db.session.commit()

        return medida

    @staticmethod
    def remove_motivo_from_medida(medida_id, motivo_id):
        """Elimina la relación entre una medida cautelar y un motivo."""
        medida = MedidaCautelar.query.get(medida_id)
        motivo = Motivo.query.get(motivo_id)

        if not medida or not motivo:
            return None  # Manejar si alguno no existe

        if motivo in medida.motivos:
            medida.motivos.remove(motivo)
            db.session.commit()

        return medida

    @staticmethod
    def get_motivos_by_medida(medida_id):
        """Obtiene todos los motivos asociados a una medida cautelar."""
        medida = MedidaCautelar.query.get(medida_id)
        return medida.motivos if medida else []

    @staticmethod
    def get_medidas_by_motivo(motivo_id):
        """Obtiene todas las medidas cautelares asociadas a un motivo."""
        motivo = Motivo.query.get(motivo_id)
        return motivo.medidas if motivo else []