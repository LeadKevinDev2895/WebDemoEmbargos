import json
from app.models.prompts import Prompts
from app import db
from datetime import datetime

class PromptsRepository:
    """Repository layer for managing Prompts database interactions."""

    @staticmethod
    def get_all():
        """Retrieve all records."""
        return Prompts.query.all()

    @staticmethod
    def get_by_id(record_id):
        """Retrieve a record by its ID."""
        return Prompts.query.get(record_id)

    def create(tipo_prompt, prompt, context, json_data):
        """
        Crea un nuevo registro en la tabla Prompts con la estructura JSON corregida.
        :param tipo_prompt: Tipo de prompt
        :param prompt: Texto del prompt
        :param context: Contexto del prompt
        :param json_data: Diccionario JSON a insertar
        """
        try:
            nuevo_prompt = Prompts(
                tipoPrompt=tipo_prompt,
                prompt=prompt,
                context=context,
                json=json.dumps(json_data),  # 🔥 Aquí se convierte el JSON a string
            )

            db.session.add(nuevo_prompt)
            db.session.commit()
            return nuevo_prompt

        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error al insertar en Prompts: {e}")

    @staticmethod
    def update(id_prompt, tipo_prompt=None, prompt=None, context=None, json_data=None):
        """
        Actualiza un prompt existente.
        """
        try:
            prompt_existente = Prompts.query.get(id_prompt)
            print(prompt_existente.tipoPrompt)
            if not prompt_existente:
                raise Exception(f"No se encontró el prompt con ID {id_prompt}")

            if tipo_prompt:
                prompt_existente.tipoPrompt = tipo_prompt
            if prompt:
                prompt_existente.prompt = prompt
            if context:
                prompt_existente.context = context
            if json_data:
                prompt_existente.json = json.dumps(json_data)  # Convertir JSON a string antes de actualizarlo

            db.session.commit()
            print(f"Prompt '{tipo_prompt}' actualizado correctamente.")
            return prompt_existente
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error al actualizar en Prompts: {e}")

    @staticmethod
    def delete(record_id):
        """Delete a record by its ID."""
        record = Prompts.query.get(record_id)
        if record:
            db.session.delete(record)
            db.session.commit()
        return record
    
    @staticmethod
    def get_one_by_tipo_prompt(tipo_prompt):
        """Retrieve a single record with a specific tipoPrompt value."""
        return Prompts.query.filter_by(tipoPrompt=tipo_prompt).first()
