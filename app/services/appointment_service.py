from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import date, time, datetime, timedelta
from app.repositories.appointment_repository import AppointmentRepository
from app.utils.exceptions import ValidationError, NotFoundError
from app.utils.cache import TTLCache
from app.config import Config

class AppointmentService:
    def __init__(self, repository: Optional[AppointmentRepository] = None) -> None:
        self._repo = repository or AppointmentRepository()
        self._cache = TTLCache(60)

    def get_all(self, cd_usuario: Optional[int] = None, cd_paciente: Optional[int] = None) -> List[Dict[str, Any]]:
        cache_key = f"appointments:all:{cd_usuario}:{cd_paciente}"
        cached = self._cache.get(cache_key)
        if cached:
            return cached
            
        appointments = self._repo.get_all(cd_usuario, cd_paciente)
        self._cache.set(cache_key, appointments)
        return appointments

    def create_appointments(self, data: Dict[str, Any]) -> int:
        prazos = {None: 1, "": 1, "1_mes": 4, "6_meses": 24, "1_ano": 48}
        prazo_str = data.get('prazo')
        count = prazos.get(prazo_str, 1)

        dt_agendamento = data['dt_agendamento']
        hora_inicio = data['hora_inicio']
        hora_fim = data['hora_fim']
        cd_usuario = data['cd_usuario']
        cd_paciente = data['cd_paciente']

        last_id = None
        for i in range(count):
            current_date = dt_agendamento + timedelta(days=7 * i)
            if current_date < date.today():
                 raise ValidationError(f"Data {current_date} is in the past", code="MSG260")
            if hora_inicio >= hora_fim:
                 raise ValidationError("Start time must be before end time", code="MSG248")
            conflicts = self._repo.get_conflicts(cd_usuario, current_date)
            for conf in conflicts:
                conf_ini = datetime.strptime(conf['hora_inicio'], "%H:%M:%S").time()
                conf_fim = datetime.strptime(conf['hora_fim'], "%H:%M:%S").time()
                if (conf_ini <= hora_inicio < conf_fim) or (conf_ini < hora_fim <= conf_fim) or \
                   (hora_inicio <= conf_ini and hora_fim >= conf_fim):
                    raise ValidationError(f"Conflict at {current_date}: {conf_ini} - {conf_fim}", code="MSG248")

            last_id = self._repo.create({
                'cd_usuario': cd_usuario,
                'cd_paciente': cd_paciente,
                'dt_agendamento': current_date,
                'hora_inicio': hora_inicio,
                'hora_fim': hora_fim
            })

        self._cache.invalidate_all()
        return last_id

    def update_appointment(self, cd_agendamento: int, data: Dict[str, Any]) -> None:
        appointment = self._repo.get_by_id(cd_agendamento)
        if not appointment:
            raise NotFoundError("Appointment not found")

        dt_agendamento = data.get('dt_agendamento') or appointment['dt_agendamento']
        hora_inicio = data.get('hora_inicio') or appointment['hora_inicio']
        hora_fim = data.get('hora_fim') or appointment['hora_fim']
        cd_usuario = data.get('cd_usuario') or appointment['cd_usuario']
        conflicts = self._repo.get_conflicts(cd_usuario, dt_agendamento, ignore_id=cd_agendamento)
        if isinstance(hora_inicio, str):
            hora_inicio = datetime.strptime(hora_inicio, "%H:%M:%S").time()
        if isinstance(hora_fim, str):
            hora_fim = datetime.strptime(hora_fim, "%H:%M:%S").time()

        for conf in conflicts:
            conf_ini = datetime.strptime(conf['hora_inicio'], "%H:%M:%S").time()
            conf_fim = datetime.strptime(conf['hora_fim'], "%H:%M:%S").time()
            if (conf_ini <= hora_inicio < conf_fim) or (conf_ini < hora_fim <= conf_fim):
                 raise ValidationError("Conflict with existing appointment", code="MSG248")

        self._repo.update(cd_agendamento, data)
        self._cache.invalidate_all()

    def delete_appointment(self, cd_agendamento: int) -> None:
        if not self._repo.get_by_id(cd_agendamento):
             raise NotFoundError("Appointment not found")
        self._repo.delete(cd_agendamento)
        self._cache.invalidate_all()

    def mark_attendance(self, cd_agendamento: int) -> None:
        appointment = self._repo.get_by_id(cd_agendamento)
        if not appointment:
            raise NotFoundError("Appointment not found")
        
        if appointment['comparecimento'] == 'S':
            raise ValidationError("Patient already marked as attended", code="MSG253")

        self._repo.update(cd_agendamento, {'comparecimento': 'S'})
        self._cache.invalidate_all()
