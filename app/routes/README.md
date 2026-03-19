# 🛣️ API Routes (Controllers) - Documentação Completa

Esta camada gerencia exclusivamente o recebimento de requisições HTTP, a validação de dados de entrada usando schemas (`Pydantic`) e o repasse para execução de regras de negócio na camada `Services`. Este arquivo lista TODOS os endpoints atualmente refatorados para a `v1` da arquitetura.

---

## 🔐 Autenticação & Login
**Base URL:** `/v1/auth`

| Método | Endpoint | Descrição | Exemplo de Payload / Query |
| :--- | :--- | :--- | :--- |
| `POST` | `/login` | Efetua login do profissional validando as credenciais. | `{"email": "psi@test.com", "password": "123"}` |

---

## 👨‍⚕️ Usuários (Psicólogos)
**Base URL:** `/v1/users`

| Método | Endpoint | Descrição | Exemplo de Payload / Query |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Lista todos os psicólogos cadastrados. | - |
| `GET` | `/{id}` | Busca os detalhes de um psicólogo. | - |
| `POST` | `/` | Cadastra um novo profissional. | `{"nm_usuario": "João", "email": "j@t.com", "senha": "123", "confirmar_senha": "123", "cip": "12345"}` |
| `PUT` | `/{id}` | Atualiza dados básicos do profissional. | `{"nm_usuario": "João Atual", "email": "j_new@t.com", "cip": "123456"}` |
| `DELETE` | `/{id}` | Remove o usuário do sistema. | - |

---

## 🔑 Recuperação de Senha
**Base URL:** `/v1/password-resets`

| Método | Endpoint | Descrição | Exemplo de Payload / Query |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Lista os pedidos de troca. | `?user_id=1` |
| `POST` | `/` | Solicita uma troca de senha (gera token). | `{"cd_usuario": 1, "email": "j@t.com"}` |
| `PUT` | `/{id}` | Efetiva a troca da senha. | `{"cd_usuario": 1, "nova_senha": "novaPassword123"}` |

---

## 👥 Pacientes
**Base URL:** `/v1/patients`

Os pacientes possuem uma visão "360 graus" agregada. Um `GET` por ID traz telefone, endereços, responsáveis e deficiências/transtornos incorporados.

| Método | Endpoint | Descrição | Exemplo de Payload / Query |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Lista todos. | `?cd_usuario=1` |
| `GET` | `/{id}` | Retorna o Paciente formatado com agregação completa. | - |
| `POST` | `/` | Criação Atômica: Salva o paciente e automaticamente cadastra seus responsáveis e endereços (se informados). | `{"nm_paciente": "Ana", "dt_nasc": "10-05-2010", "sexo": "F", "cd_genero": 1, "cd_perfil": 2, "cd_usuario": 1, "telefones": [...], "endereco_paciente": {...}}` |
| `PUT` | `/{id}` | Atualiza nome, sexo, nascimento, tipo sanguíneo. | `{"nm_paciente": "Ana M."}` |
| `PATCH` | `/{id}/toggle` | Inverte o status de Ativo/Inativo. | - |

---

## 🧑‍👦 Responsáveis do Paciente
**Base URL:** `/v1/patients/{id}/responsaveis`

Gestão independente de responsáveis vinculados a um paciente. Cada operação verifica se o responsável pertence ao paciente da URL antes de executar. O cache de detalhes do paciente é invalidado automaticamente.

| Método | Endpoint | Descrição | Exemplo de Payload / Query |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Lista todos os responsáveis do paciente. | - |
| `POST` | `/` | Adiciona um novo responsável ao paciente. | `{"cpf": "123.456.789-00", "nome": "Maria Silva", "dt_nascimento": "15-06-1980"}` |
| `PUT` | `/{rid}` | Edita dados de um responsável específico. | `{"nome": "Maria S. Atualizado"}` |
| `DELETE` | `/{rid}` | Remove um responsável específico do paciente. | - |

---

## 🏠 Endereços do Paciente
**Base URL:** `/v1/patients/{id}/enderecos`

Gestão independente de endereços vinculados a um paciente. Suporta endereços tanto do paciente (`tipo: PACIENTE`) quanto do responsável (`tipo: RESPONSAVEL`). O cache de detalhes do paciente é invalidado automaticamente.

| Método | Endpoint | Descrição | Exemplo de Payload / Query |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Lista todos os endereços do paciente. | - |
| `POST` | `/` | Adiciona um novo endereço. | `{"tipo": "PACIENTE", "cep": "01310-100", "cidade": "São Paulo", "bairro": "Bela Vista", "logradouro": "Av. Paulista", "uf": "SP", "numero": "1000"}` |
| `PUT` | `/{eid}` | Edita um endereço específico. | `{"numero": "1001", "complemento": "Apto 42"}` |
| `DELETE` | `/{eid}` | Remove um endereço específico. | - |

---

## 🧠 Transtornos & Elementos Clínicos
O Catálogo base da medicina/psicologia para a MenTech.
**Base URL:** `/v1`

| Método | Endpoint | Descrição | Exemplo de Payload / Query |
| :--- | :--- | :--- | :--- |
| `GET` | `/disorders` | Lista simplificada (apenas a entidade principal). | - |
| `GET` | `/disorders/details` | Lista todos agregando Severidades, Critérios e Subtipos. | - |
| `GET` | `/disorders/{id}` | Busca um transtorno específico simples. | - |
| `GET` | `/disorders/{id}/details` | Traz o transtorno junto de todo o aglomerado de condições.| - |
| `POST` | `/disorders` | Criação simples (Apenas o Transtorno). | `{"nm_transtorno": "TDAH", "cid11": "6A05"}` |
| `POST` | `/disorders/full`| Criação Atômica: Salva o Transtorno, suas Gravidades e Subtipos anexos na mesma transação. | `{"disorder": {...}, "subtypes": [...], "severities": [...]}` |
| `PUT` | `/disorders/{id}`| Edição simplificada do Transtorno base. | - |
| `PUT` | `/disorders/{id}/full` | Edição com substituição dos galhos atômicos.| - |
| `DELETE` | `/disorders/{id}`| Remove Transtorno. | - |
| `GET` | `/disorders/{id}/subtypes` | Lista subtipos daquele transtorno. | - |
| `POST` | `/disorders/{id}/subtypes` | Adiciona um subtipo a um Transtorno fixo. | `{"nm_subtipo": "Desatento", "cid11": "6A05.0"}` |
| `PUT/DEL`| `/subtypes/{id}`| Atualiza/Remove o subtipo em si (endpoint base de subtipos). | - |
| `GET` | `/disorders/{id}/severities` | Lista as gravidades (Leve, Moderado, Severo). | - |
| `POST` | `/disorders/{id}/severities` | Cadastra a gravidade ao transtorno. | `{"nm_gravidade": "Leve", "grav_descricao": "..."}` |
| `PUT/DEL`| `/severities/{id}`| Atualiza/Remove a gravidade em si.| - |
| `GET` | `/disorders/{id}/criteria` | Lista Critérios diagnósticos e diferenciais. | - |
| `POST` | `/disorders/{id}/criteria` | Cadastra critérios ao transtorno. | `{"criterio_diagnostico": "Condição A"}` |
| `PUT/DEL`| `/criteria/{id}` | Atualiza/Remove o critério. | - |

---

## 🔗 Vínculos Diagnósticos (Paciente <-> Transtorno)
**Base URL:** `/v1/patient-disorders`

| Método | Endpoint | Descrição | Exemplo de Payload / Query |
| :--- | :--- | :--- | :--- |
| `GET` | `/patient/{id}`| Lista os quadros do paciente específico. | - |
| `POST` | `/` | Associa o Transtorno ao Paciente (na data X). | `{"cd_paciente": 1, "cd_transtorno": 2, "datas": "2023-11-01"}` |
| `PUT` | `/patient/{pid}/disorder/{tid}`| Atualiza a data ou observações do vínculo. | `{"datas": "2023-11-02"}`|
| `DELETE`| `/patient/{pid}/disorder/{tid}`| Remove a associação sem apagar do catálogo. | - |

---

## 📝 Anamnese (Questionários)
**Base URL:** `/v1/anamnese`

| Método | Endpoint | Descrição | Exemplo de Payload / Query |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Lista as rodadas de Anamneses geradas. | `?cd_paciente=1` |
| `GET` | `/{id}` | Traz os detalhes completos, questões preenchidas de uma aplicação. | - |
| `POST` | `/generate` | Rotina de negócio automatizada. Localiza as perguntas cadastradas pela base de seu público e **gera e anexa** o questionário ao Paciente informado.| `{"cd_paciente": 1, "cd_perfil": 2}` |
| `POST` | `/answer` | Salva a resposta dada a cada alternativa para aquela anamnese exata e suas seleções.| `{"cd_anamnese": 5, "cd_questao": 10, "txt_resposta": "Sim", "cd_alternativa": [1]}` |
| `DELETE` | `/{id}` | Remove um histórico de Anamnese. | - |
| `GET` | `/questions/{id}/alternatives`| Para preenchimento via Front-End, localiza as opções de caixa de seleção. | - |

---

## 📋 Prontuários (Registo Clínico)
Todos os dados descritivos nesta etapa (como a anotação) são criptografados nativamente utilizando `AES_ENCRYPT` ao atingirem a camada de Repository de banco de dados.
**Base URL:** `/v1/medical-records`

| Método | Endpoint | Descrição | Exemplo de Payload / Query |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Retorna o registro clínico descriptografado do MySQL.| `?cd_paciente=1` |
| `POST` | `/` | Cria a anotação criptografada vinculada a um paciente. | `{"dt_prontuario": "2023-10-30", "cd_paciente": 1, "anotacao_pront": "Evolução..."}` |
| `PUT` | `/{id}` | Altera criptografia localizando a anotação específica base. | `{"anotacao_pront": "Evolução Editada"}` |
| `DELETE` | `/{id}` | Remove permanentemente o prontuário. | - |

---

## 📅 Agendamentos
Traz suporte para sessões recorrentes com gestão inteligente de colisões de calendário.
**Base URL:** `/v1/appointments`

| Método | Endpoint | Descrição | Exemplo de Payload / Query |
| :--- | :--- | :--- | :--- |
| `GET` | `/appointments`| Lista consultas. | `?cd_usuario=1` ou `?cd_paciente=2` |
| `POST` | `/appointments`| Cria uma ou várias sessões usando recorrência, gerando checagem automática de não bater horário.| `{"cd_usuario": 1, "cd_paciente": 2, "dt_agendamento": "2023-10-20", "hora_inicio": "14:00", "hora_fim": "15:00", "prazo": "1_mes"}` *(prazos suportados: "1_mes", "6_meses", "1_ano")* |
| `PUT` | `/appointments/{id}`| Reagenda com nova verificação de conflitos na agenda do profissional. | `{"dt_agendamento": "2023-10-21"}`|
| `DELETE` | `/appointments/{id}`| Remove do tempo. | - |
| `POST` | `/appointments/{id}/attendance`| Disparo para alteração de status (`S/N`) de comparecimento verificado.| - |

---

## 🎭 Comportamentos (Histórico do Paciente)
Sessão para apontar padrões de comportamentos singulares (agitação, tiques) em terapia.
**Base URL:** `/v1/behaviors`

| Método | Endpoint | Descrição | Exemplo de Payload / Query |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Lista global ou filtrada de todo o banco comportamental. | `?cd_paciente=1` |
| `GET` | `/patient/{id}`| Atalho para exibir a visão unificada de comportamento daquele passiente. | - |
| `POST` | `/` | Registra no histórico novo comportamento (texto é formatado de forma limpa pelo `Service`). | `{"cd_paciente": 1, "comportamento_paciente": "Tem demonstrado agitações antes de iniciar conversas"}`|
| `PUT` | `/{id}` | Altera um comportamento passado. | `{"comportamento_paciente": "..."}` |
| `DELETE` | `/{id}` | Desvincula o aviso. | - |

---

## 💊 Medicamentos
Catálogo de prescrições ativas. Com suporte para dosagem.
**Base URL:** `/v1/medications`

| Método | Endpoint | Descrição | Exemplo de Payload / Query |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Lê todos os medicamentos disponíveis da base de dados global filtrada. | - |
| `GET` | `/patient/{id}`| Retorna dados com **Join** complexo (`paciente_medicamento` + detalhes) identificando a posologia individual do paciente. | - |
| `POST` | `/` | Adiciona um novo medicamento ao banco. | `{"nm_medicamento": "Ritalina", "dosagem": "10mg" }` *(forma_farmaceutica, principio, fabricante também suportados)* |
| `PUT` | `/{id}` | Edita parâmetros gerais do remédio da base. | - |
| `DELETE` | `/{id}` | Remove medicamento. | - |

---

## 🚻 Gêneros
**Base URL:** `/v1/genders`

| Método | Endpoint | Descrição | Exemplo de Payload / Query |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Traz categorias do gênero. Cacheado internamente em memória. | - |
| `POST` | `/` | Insere identificadores padrões à tabela. | `{"nm_genero": "Masculino"}` |
| `PUT` | `/{id}` | Corrige nomenclaturas e quebra o cache global do TTLCache. | - |
| `DELETE` | `/{id}` | Remove do sistema categorizado. | - |

---

## 🎯 Metas Terapêuticas
Gestão do catálogo de metas e de sua atribuição para pacientes. 
**Base URL:** `/v1/goals`

| Método | Endpoint | Descrição | Exemplo de Payload / Query |
| :--- | :--- | :--- | :--- |
| `GET` | `/patient/{id}` | Traz todas as metas e prazos atrelados ao paciente específico. | - |
| `POST` | `/` | Fluxo Atômico: Cria a diretriz base e simultaneamente agenda-a para o paciente informado. | `{"meta": "Melhorar Foco", "obs_meta": "...", "cd_paciente": 1, "dt_previsao": "2024-12-01"}` |
| `PATCH`| `/relation/{id}/complete`| Finaliza a relação paciente-meta (Altera o status `ativo` para C e grava data atual). | - |
| `PATCH`| `/{id}/toggle` | Suspende temporariamente uma diretriz clínica. | - |
| `DELETE`| `/{id}` | Apaga permanentemente do catálogo (Requer cautela). | - |

---

## 🏋️‍♂️ Atividades Práticas
Gestão de tarefas contínuas vinculadas às metas, monitorando ativamente progresso e evolução.
**Base URL:** `/v1/activities`

| Método | Endpoint | Descrição | Exemplo de Payload / Query |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Rota universal de listagem. Intercepta requisições flexíveis (para um Paciente, um User(Psicólogo) ou uma Meta específica). | `?cd_paciente=1` ou `?cd_usuario=5` ou `?cd_meta=12` |
| `POST` | `/` | Cadastra nova tarefa e sua pontuação primária. | `{"cd_meta": 12, "nm_atividade": "Leitura Guiada", "descricao_atividade": "...", "dt_atividade": "2024-01-01", "parecer_tecnico": "...", "resultado": "Pendente"}` |
| `PUT` | `/{id}` | Atualiza estado descritivo da atividade e sua `%` de conclusão. | `{"percent_conclusao": 50}` |
| `PATCH`| `/{id}/toggle` | Muda de Pendente(S) para Concluído(N) e vice-versa. | - |
| `DELETE`| `/{id}` | Remove a trilha. | - |
| `GET` | `/{id}/history`| Busca na Tabela de Históricos todas as alterações e aproximações `%` salvas numa Atividade Única. | - |
| `GET` | `/goal/{id}/history` | Busca o agrupamento evolutivo de todas as atividades encadeadas na mesma Meta. | - |

---

## 📝 Logs de Ação de Sistema (Antigo bdRoutes)
Gestão da auditoria e persistência de rastros de usuários blindados contra concorrência e *Racing condition* (suporte a Multi-Usuários).
**Base URL:** `/v1/log-actions`

| Método | Endpoint | Descrição | Exemplo de Payload / Query |
| :--- | :--- | :--- | :--- |
| `POST` | `/` | Gera o registro estrito via API HTTP, acoplado explicitamente ou preenchendo o autor pelos *Headers* automáticos (`x-usuario-id`). | `{"cd_usuario": 1, "tipo_log": "CMT", "mensagem_adicional": "Teste criacao"}` |
| `POST` | `/definir_usuario/{id}`| **[DEPRECADO]** Rota fictícia Mock de retrocompatibilidade para que Front-End antigos baseados no modelo anterior não entrem em Crash (`Axios Error`).| - |

