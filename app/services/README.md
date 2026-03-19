# ⚙️ Services Layer (Business Logic)

Esta camada contém as **Regras de Negócio** puras da aplicação. É aqui onde o "comportamento" do sistema é definido.

## 🎯 Objetivo
- Orquestrar operações complexas que envolvem múltiplos repositórios.
- Validar condições de negócio (ex: verificar se um e-mail já existe).
- Normalizar dados (Capitalização, formatação de datas).
- Gerenciar cache de alta performance via **TTLCache**.

## 📄 Arquivos e Responsabilidades

| Arquivo | Descrição |
| :--- | :--- |
| `patient_service.py` | Orquestra a criação de pacientes completos (atômico) e lida com cache de detalhes. |
| `disorder_service.py` | Gerencia o catálogo clínico e agregação de dados complexos para o frontend. |
| `anamnese_service.py` | Lógica de geração de questionários baseada em perfis e salvamento de respostas. |
| `medical_record_service.py` | Processamento de registros clínicos e segurança. |
| `gender_service.py` | Gestão de gêneros com invalidação de cache. |
| `auth_service.py` | Validação de credenciais e workflow de login. |
| `user_service.py` | Regras para criação e atualização de psicólogos. |
| `password_service.py` | Lógica de geração de tokens e expiração para reset de senha. |
| `patient_disorder_service.py` | Gestão de vínculos diagnósticos. |
| `appointment_service.py` | Regras de agendamento, recorrência automática e detecção de conflitos de horário. |
| `behavior_service.py` | Gestão de comportamentos observados no paciente com normalização de texto. |
| `medication_service.py` | Catálogo de medicamentos e gestão de prescrições por paciente. |
| `goal_service.py` | Fluxo atômico para atrelar metas e calcular viabilidade de prazo por datas lógicas. |
| `activity_service.py` | Histórico evolutivo (percentuais) unificados e centralização de múltiplos filtros complexos. |
| `log_service.py` | Serviço core responsável por prover automação Thread-Local (Contexto via `flask.g`) ciente de N-usuários e formatar traduções das ações usando a tabela de mensagens base. |
| `pathology_service.py` | CRUD de patologias (comorbidades) do catálogo clínico. |
| `responsible_service.py` | Gestão independente de responsáveis vinculados a um paciente: adicionar, editar e remover, com invalidação de cache. |
| `address_service.py` | Gestão independente de endereços vinculados a um paciente: adicionar, editar e remover, suportando endereços de paciente e de responsável. |

## 🚀 Otimizações de Performance
- **Cache TTL**: Listagens pesadas ou que mudam pouco são armazenadas em memória para redução de IO.
- **Atomicidade**: Processos que exigem consistência (como criar um paciente com endereço) são feitos em um único fluxo de serviço.
