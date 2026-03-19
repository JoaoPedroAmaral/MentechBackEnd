from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.repositories.patient_repository import PatientRepository
from app.repositories.address_repository import AddressRepository
from app.repositories.responsible_repository import ResponsibleRepository
from app.repositories.phone_repository import PhoneRepository
from app.repositories.patient_disorder_repository import PatientDisorderRepository
from app.utils.text import normalize_and_capitalize, format_date_to_db
from app.utils.exceptions import ValidationError, NotFoundError
from app.utils.cache import TTLCache
from app.config import Config

class PatientService:
    CACHE_ALL = "patients:all"
    
    def __init__(
        self,
        patient_repo: Optional[PatientRepository] = None,
        address_repo: Optional[AddressRepository] = None,
        resp_repo: Optional[ResponsibleRepository] = None,
        phone_repo: Optional[PhoneRepository] = None,
        disorder_repo: Optional[PatientDisorderRepository] = None
    ) -> None:
        self._patient_repo = patient_repo or PatientRepository()
        self._address_repo = address_repo or AddressRepository()
        self._resp_repo = resp_repo or ResponsibleRepository()
        self._phone_repo = phone_repo or PhoneRepository()
        self._disorder_repo = disorder_repo or PatientDisorderRepository()
        self._cache = TTLCache(Config.CACHE_TTL_SECONDS)

    def get_all(self, cd_usuario: Optional[int] = None) -> List[Dict[str, Any]]:
        cache_key = f"patients:user:{cd_usuario}" if cd_usuario else "patients:all"
        cached = self._cache.get(cache_key)
        if cached:
            return cached
            
        patients = self._patient_repo.get_all(cd_usuario)
        self._cache.set(cache_key, patients)
        return patients

    def get_details(self, cd_paciente: int) -> Dict[str, Any]:
        cache_key = f"patient:details:{cd_paciente}"
        cached = self._cache.get(cache_key)
        if cached:
            return cached

        patient = self._patient_repo.get_by_id(cd_paciente)
        if not patient:
            raise NotFoundError("Patient not found")
        patient['responsavel'] = self._resp_repo.get_by_patient_id(cd_paciente)
        patient['enderecos'] = self._address_repo.get_by_patient_id(cd_paciente)
        patient['telefones'] = self._phone_repo.get_by_patient(cd_paciente)
        patient['transtornos'] = self._disorder_repo.get_by_patient(cd_paciente)
        self._cache.set(cache_key, patient)
        return patient

    def create_full_patient(self, data: Dict[str, Any]) -> int:
        nm_paciente = normalize_and_capitalize(data['nm_paciente'])
        dt_nasc = format_date_to_db(data['dt_nasc'])
        patient_id = self._patient_repo.create({
            'nm_paciente': nm_paciente,
            'dt_nasc': dt_nasc,
            'sexo': normalize_and_capitalize(data['sexo']),
            'cd_genero': data['cd_genero'],
            'tip_sang': normalize_and_capitalize(data.get('tip_sang')),
            'cd_perfil': data['cd_perfil']
        }, cd_usuario=data['cd_usuario'])
        first_resp_id = None
        if data.get('responsavel'):
            for resp_data in data['responsavel']:
                current_id = self._resp_repo.create({
                    'cd_paciente': patient_id,
                    'cpf': resp_data['cpf'],
                    'nome': normalize_and_capitalize(resp_data['nome']),
                    'dt_nascimento': format_date_to_db(resp_data['dt_nascimento'])
                })
                if first_resp_id is None:
                    first_resp_id = current_id
        if data.get('endereco_paciente'):
            addr = data['endereco_paciente']
            self._address_repo.create({
                **addr,
                'cd_paciente': patient_id,
                'tipo': 'PACIENTE',
                    'cd_responsavel': None
            })
        if data.get('endereco_responsavel') and first_resp_id:
            addr = data['endereco_responsavel']
            self._address_repo.create({
                **addr,
                'cd_paciente': patient_id,
                'tipo': 'RESPONSAVEL',
                'cd_responsavel': first_resp_id
            })
        if data.get('telefones'):
            for phone in data['telefones']:
                self._phone_repo.create({
                    **phone,
                    'cd_paciente': patient_id
                })

        self._cache.invalidate(self.CACHE_ALL)
        self._cache.invalidate(f"patients:user:{data['cd_usuario']}")
        return patient_id

    def update_patient(self, cd_paciente: int, data: Dict[str, Any]) -> None:
        if 'dt_nasc' in data and data['dt_nasc']:
            data['dt_nasc'] = format_date_to_db(data['dt_nasc'])
        
        for field in ['nm_paciente', 'sexo', 'tip_sang']:
            if field in data and data[field]:
                data[field] = normalize_and_capitalize(data[field])

        self._patient_repo.update(cd_paciente, data)
        self._cache.invalidate(f"patient:details:{cd_paciente}")
        self._cache.invalidate(self.CACHE_ALL)

    def toggle_active(self, cd_paciente: int) -> str:
        patient = self._patient_repo.get_by_id(cd_paciente)
        if not patient:
            raise NotFoundError("Patient not found")
            
        new_status = 'N' if patient['ativo'] == 'S' else 'S'
        self._patient_repo.update(cd_paciente, {'ativo': new_status})
        
        self._cache.invalidate(f"patient:details:{cd_paciente}")
        self._cache.invalidate(self.CACHE_ALL)
        return new_status
