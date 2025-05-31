
from app import db
from app.models.demandado import Demandado

class DemandadoRepository:
    """Repository layer for managing Demandado database interactions."""

    @staticmethod
    def get_all():
        """Retrieve all records."""
        return Demandado.query.all()

    @staticmethod
    def get_by_id(record_id):
        """Retrieve a record by its ID."""
        return Demandado.query.get(record_id)

    @staticmethod
    def create(data):
        """Create a new record."""
        new_record = Demandado(**data)
        db.session.add(new_record)
        db.session.commit()
        return new_record

    @staticmethod
    def update(record_id, data):
        """Update an existing record by its ID."""
        record = Demandado.query.get(record_id)
        if not record:
            return None
        for key, value in data.items():
            setattr(record, key, value)
        db.session.commit()
        return record

    @staticmethod
    def delete(record_id):
        """Delete a record by its ID."""
        record = Demandado.query.get(record_id)
        if record:
            db.session.delete(record)
            db.session.commit()
        return record
