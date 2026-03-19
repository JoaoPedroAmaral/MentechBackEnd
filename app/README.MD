# 🧠 MenTech App - Documentação Técnica

Este diretório contém o núcleo da inteligência e lógica da MenTech API. A arquitetura segue o padrão **Clean Architecture**, dividida em camadas para garantir escalabilidade, testabilidade e facilidade de manutenção.

---

## 🏛️ Estrutura do Diretório `app/`

Clique nos links abaixo para acessar a documentação detalhada de cada camada:

### 🛣️ [Routes (Controllers)](./routes/README.md)
Mapeamento de todos os endpoints HTTP, exemplos de payloads de entrada e estruturas de resposta. É a porta de entrada da aplicação.

### ⚙️ [Services (Business Logic)](./services/README.md)
Onde residem as regras de negócio, orquestração de dados, cálculos e gerenciamento de cache.

### 🗄️ [Repositories (Data Access)](./repositories/README.md)
Toda a lógica de persistência e comunicação com o MySQL. Gerencia SQL puro e criptografia de dados.

### 📋 [Schemas (DTOs & Validation)](./schemas/README.md)
Definições dos contratos de dados (Pydantic models) para validação rigorosa de entrada de dados.

### 🛠️ [Utils (Helpers)](./utils/README.md)
Ferramentas transversais: Conexão com DB, Logística de Texto, Exceções Customizadas e Cache Global.

### 🏗️ [Models (Entities)](./models/README.md)
Definições estruturais das entidades do sistema.

---

## 🚀 Princípios de Design

1.  **Independência de Framework**: As regras de negócio (Services) não dependem das rotas (Flask).
2.  **Responsabilidade Única (SOLID)**: Cada arquivo e classe tem uma única razão para mudar.
3.  **Performance em Primeiro Lugar**: Uso agressivo de Cache e consultas agregadas para reduzir a carga no banco de dados.
4.  **Criptografia Nativa**: Dados sensíveis nunca tocam o banco de dados em texto puro.
