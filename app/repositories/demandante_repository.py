
from app import db
from app.models.demandante import Demandante

class DemandanteRepository:
    """Repository layer for managing Demandante database interactions."""

    @staticmethod
    def get_all():
        """Retrieve all records."""
        return Demandante.query.all()

    @staticmethod
    def get_by_id(record_id):
        """Retrieve a record by its ID."""
        return Demandante.query.get(record_id)

    @staticmethod
    def create(data):
        """Create a new record."""
        new_record = Demandante(**data)
        db.session.add(new_record)
        db.session.commit()
        return new_record

    @staticmethod
    def update(record_id, data):
        """Update an existing record by its ID."""
        record = Demandante.query.get(record_id)
        if not record:
            return None
        for key, value in data.items():
            setattr(record, key, value)
        db.session.commit()
        return record

    @staticmethod
    def delete(record_id):
        """Delete a record by its ID."""
        record = Demandante.query.get(record_id)
        if record:
            db.session.delete(record)
            db.session.commit()
        return record
