# 📋 Schemas Layer (DTOs & Validation)

Esta camada define as estruturas de dados que entram e saem da API, utilizando **Pydantic** para validação automática.

## 🎯 Objetivo
- Garantir a integridade dos dados enviados pelo cliente.
- Tipagem forte para evitar erros de tempo de execução.
- Documentação implícita dos contratos da API.
- Sanitização de campos (remoção de espaços extras, validação de e-mails/formatos).

## 📄 Arquivos e Responsabilidades

| Arquivo | Descrição |
| :--- | :--- |
| `patient.py` | Modelos para criação atômica de pacientes (inclui telefones, endereços e responsáveis embutidos). |
| `responsible.py` | DTOs independentes para adicionar e editar responsáveis via rotas `/v1/patients/{id}/responsaveis`. |
| `address.py` | DTOs independentes para adicionar e editar endereços via rotas `/v1/patients/{id}/enderecos`. |
| `disorder.py` | Estruturas para transtornos e seus elementos clínicos (subtipos, etc). |
| `anamnese.py` | Validação de respostas e requisições de geração de questionários. |
| `medical_record.py` | DTOs para registros clínicos. |
| `gender.py` | Contratos para cadastro de gêneros. |
| `auth.py` | Login e respostas de autenticação. |
| `user.py` | Cadastro e atualização de psicólogos. |
| `password.py` | Solicitações de reset de senha e validação de tokens. |
| `appointment.py` | Modelos para criação de agendamentos e regras de recorrência. |
| `behavior.py` | Validação de textos de comportamento e vínculos com pacientes. |
| `medication.py` | DTOs para medicamentos, dosagens e fabricantes. |
| `goal.py` | Checagem de datas de previsão e normalização do texto da meta (DTOs unificadores). |
| `activity.py` | Regras estritas de *len* de caracteres e resultados das ações terapêuticas. |
| `log.py` | Contratos estritos de envio do payload de auditoria e segurança contra strings de código excedentes de "10 chars". |
| `pathology.py` | Validação para o CRUD de patologias. |
| `patient_medication.py` | Contratos para gestão da prescrição de medicamentos ao paciente. |

## 🛠️ Exemplo de Validador Manual
Nos arquivos de schema, utilizamos decoradores `@validator` para regras customizadas:

```python
@validator("email")
def validate_email(cls, value: str) -> str:
    if not EMAIL_RE.match(value):
        raise ValueError("Invalid email format")
    return value
```
