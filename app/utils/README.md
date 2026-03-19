# 🛠️ Utils & Helpers

Funções utilitárias genéricas que servem a todas as camadas da aplicação, mantendo o código **DRY (Don't Repeat Yourself)**.

## 📄 Principais Utilitários

### 💾 `database.py`
Gerencia o **Connection Pool** do MySQL.
- `get_connection()`: Retorna uma conexão ativa do pool.

### ⚡ `cache.py`
Implementação simples de Cache em memória com tempo de expiração (TTL).
- `TTLCache`: Classe para get/set/invalidate de dados.

### 📝 `text.py`
Processamento de strings e datas.
- `normalize_and_capitalize()`: Remove espaços e capitaliza nomes.
- `format_date_to_db()`: Converte `DD-MM-YYYY` para `YYYY-MM-DD`.

### 🚨 `exceptions.py`
Classes de exceção customizadas para controle de fluxo.
- `NotFoundError`, `ValidationError`, `UnauthorizedError`.

### 📨 `response.py`
Formatador padrão de respostas JSON da API.
- `ok(data)`: Retorna 200/201 com envelope `success: true`.
- `error(message)`: Retorna erro padronizado.

### 🔍 `validation.py`
Decorador para validação automática de Schemas nas rotas.
- `@validate_schema(Model)`: Valida o `request.json` antes de entrar na função da rota.
