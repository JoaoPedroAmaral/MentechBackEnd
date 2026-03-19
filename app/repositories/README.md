# 🗄️ Repositories Layer

Esta camada é responsável exclusivamente pelo acesso aos dados (**Data Access**). Ela isola a complexidade das consultas SQL e a infraestrutura de banco de dados do restante da aplicação.

## 🎯 Objetivo
- Executar comandos SQL (Select, Insert, Update, Delete).
- Gerenciar a criptografia de campos sensíveis no nível de banco de dados (`AES_ENCRYPT`/`AES_DECRYPT`).
- Garantir que a lógica de persistência não vaze para as regras de negócio (Services).

## 📄 Arquivos e Responsabilidades

| Arquivo | Descrição |
| :--- | :--- |
| `patient_repository.py` | CRUD de pacientes e gestão da tabela principal. |
| `address_repository.py` | Gerenciamento de endereços vinculados a pacientes ou responsáveis. Suporta busca por ID, criação, edição, remoção individual e remoção em massa por paciente. |
| `responsible_repository.py` | Gestão de dados pessoais dos responsáveis. Suporta busca por ID, criação, edição, remoção individual e remoção em massa por paciente. |
| `phone_repository.py` | Persistência de contatos telefônicos. |
| `disorder_repository.py` | Catálogo de transtornos, subtipos, gravidades e critérios. |
| `medical_record_repository.py` | Registros clínicos com criptografia de texto. |
| `gender_repository.py` | Gestão de tipos de gênero. |
| `patient_disorder_repository.py` | Tabela associativa entre pacientes e diagnósticos. |
| `user_repository.py` | Gestão de usuários (psicólogos) e credenciais. |
| `password_repository.py` | Tokens de recuperação de senha. |
| `anamnese_repository.py` | Questionários, questões e persistência de respostas. |
| `appointment_repository.py` | Persistência de agendamentos e verificação de disponibilidade. |
| `behavior_repository.py` | Registros de comportamento com suporte a criptografia. |
| `medication_repository.py` | CRUD de medicamentos e integração com prontuário do paciente. |
| `goal_repository.py` | Gestão complexa com transactions envolvendo `meta` e `paciente_meta` simultaneamente. |
| `activity_repository.py` | Extração de listagens paramétricas modulares e histórico de progressões de métrica. |
| `log_repository.py` | Persistência da auditoria que lê o código dinamicamente da Tabela de mensagens predefinidas. |
| `pathology_repository.py` | CRUD de patologias (comorbidades) do catálogo clínico. |
| `patient_medication_repository.py` | Associação entre pacientes e medicamentos prescritos com controle de posologia. |

## 🛠️ Padrão de Implementação
Todos os repositórios utilizam o utilitário `get_connection()` para obter conexões do pool e utilizam **queries parametrizadas** para prevenir SQL Injection.

```python
# Exemplo de padrão
with get_connection() as conn:
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM tabela WHERE id = %s", (id,))
        return cursor.fetchone()
```
