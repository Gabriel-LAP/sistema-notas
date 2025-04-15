# Sistema de Registro de Notas

Este é um sistema desktop simples para registrar notas de alunos, desenvolvido com **Python**, **Tkinter** (interface gráfica) e **PostgreSQL** (banco de dados).

## 📋 Funcionalidades

- Cadastro de alunos (nome, turma)
- Registro de notas por disciplina
- Edição e exclusão de notas
- Remoção de alunos
- Busca de alunos por nome
- Interface gráfica intuitiva com `Tkinter`

## 💻 Tecnologias usadas

- **Python 3.x**
- **Tkinter** – Interface gráfica
- **PostgreSQL** – Banco de dados
- **psycopg2** – Conector PostgreSQL para Python
- **python-dotenv** – Gerenciamento seguro de variáveis de ambiente


## 🧱 Estrutura do banco de dados

O sistema cria automaticamente as tabelas abaixo ao iniciar:

- **alunos**:  
  - `aluno_id`: identificador único  
  - `nome`: nome do aluno  
  - `turma`: turma do aluno

- **notas**:  
  - `nota_id`: identificador único da nota  
  - `aluno_id`: referência ao aluno  
  - `disciplina`: nome da disciplina  
  - `nota`: valor da nota (formato decimal)


## ⚙️ Instalação e Execução

### 1. Clone o repositório
```bash
git clone https://github.com/Gabriel-LAP/sistema-notas.git
cd sistema-notas
```

### 2. Instale as dependências
```bash
pip install psycopg2

pip install python-dotenv
```
### 3. Configure as variáveis de ambiente
Crie um arquivo .env na raiz do projeto com suas credenciais do PostgreSQL:

```bash
DB_NAME=seu_banco
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432
```

### 4. Execute o sistema
```bash
python app.py
```

