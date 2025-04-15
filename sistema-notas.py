import psycopg2
import tkinter as tk
from tkinter import messagebox, ttk
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Define as variáveis de ambiente como variáveis Python
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')

# Conexão com o banco de dados PostgreSQL
def conectar():
    return psycopg2.connect(
        dbname= DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,  
        host=DB_HOST,
        port=DB_PORT
    )

# Criação das tabelas no banco de dados
def criar_tabelas():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            aluno_id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            turma TEXT NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            nota_id SERIAL PRIMARY KEY,
            aluno_id INTEGER REFERENCES alunos(aluno_id) ON DELETE CASCADE,
            disciplina TEXT NOT NULL,
            nota NUMERIC(5,2) NOT NULL
        );
    """)
    conn.commit()
    conn.close()

# Limpa todos os campos de entrada da interface
def limpar_campos():
    entry_nome.delete(0, tk.END)
    entry_turma.delete(0, tk.END)
    entry_id_aluno.delete(0, tk.END)
    entry_disciplina.delete(0, tk.END)
    entry_nota.delete(0, tk.END)
    entry_nota_id.delete(0, tk.END)
    entry_nova_nota.delete(0, tk.END)
    entry_busca_nome.delete(0, tk.END)

# Insere um novo aluno no banco
def inserir_aluno():
    nome = entry_nome.get()
    turma = entry_turma.get()
    if nome and turma:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("INSERT INTO alunos (nome, turma) VALUES (%s, %s)", (nome, turma))
        conn.commit()
        conn.close()
        limpar_campos()
        messagebox.showinfo("Sucesso", "Aluno cadastrado com sucesso!")
        atualizar_lista()
    else:
        messagebox.showwarning("Atenção", "Preencha todos os campos.")

# Registra uma nota para um aluno existente
def registrar_nota():
    aluno_id = entry_id_aluno.get().strip()
    disciplina = entry_disciplina.get().strip()
    nota = entry_nota.get().strip()

    if aluno_id and disciplina and nota:
        try:
            aluno_id = int(aluno_id)
            nota = float(nota)
        except ValueError:
            messagebox.showerror("Erro", "ID do aluno deve ser um número inteiro e nota deve ser numérica.")
            return

        conn = conectar()
        cur = conn.cursor()
        cur.execute("INSERT INTO notas (aluno_id, disciplina, nota) VALUES (%s, %s, %s)",
                    (aluno_id, disciplina, nota))
        conn.commit()
        conn.close()
        limpar_campos()
        messagebox.showinfo("Sucesso", "Nota registrada com sucesso!")
        atualizar_lista()
    else:
        messagebox.showwarning("Atenção", "Preencha todos os campos.")

# Atualiza a lista de alunos/notas na Treeview
def atualizar_lista():
    for row in tree.get_children():
        tree.delete(row)

    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT n.nota_id, a.aluno_id, a.nome, a.turma, n.disciplina, n.nota
        FROM alunos a
        LEFT JOIN notas n ON a.aluno_id = n.aluno_id
        ORDER BY a.aluno_id;
    """)
    resultados = cur.fetchall()
    conn.close()

    for linha in resultados:
        tree.insert("", tk.END, values=linha)

# Atualiza a nota de um aluno
def atualizar_nota():
    nota_id = entry_nota_id.get()
    nova_nota = entry_nova_nota.get()
    if nota_id and nova_nota and nota_id.lower() != 'none':
        try:
            nova_nota = float(nova_nota)
        except ValueError:
            messagebox.showerror("Erro", "A nota deve ser um número.")
            return

        conn = conectar()
        cur = conn.cursor()
        cur.execute("UPDATE notas SET nota = %s WHERE nota_id = %s", (nova_nota, nota_id))
        conn.commit()
        conn.close()
        limpar_campos()
        messagebox.showinfo("Sucesso", "Nota atualizada com sucesso!")
        atualizar_lista()
    else:
        messagebox.showwarning("Atenção", "Preencha todos os campos ou selecione uma nota válida.")

# Deleta uma nota e, se não houver mais notas, deleta também o aluno
def deletar_nota():
    nota_id = entry_nota_id.get().strip()
    aluno_id = entry_id_aluno.get().strip()

    if nota_id and nota_id.isdigit() and aluno_id:
        nota_id = int(nota_id)
        conn = conectar()
        cur = conn.cursor()
        cur.execute("DELETE FROM notas WHERE nota_id = %s", (nota_id,))
        conn.commit()

        cur.execute("SELECT COUNT(*) FROM notas WHERE aluno_id = %s", (aluno_id,))
        count = cur.fetchone()[0]
        if count == 0:
            cur.execute("DELETE FROM alunos WHERE aluno_id = %s", (aluno_id,))

        conn.commit()
        conn.close()

        limpar_campos()
        messagebox.showinfo("Sucesso", "Nota deletada com sucesso!")
        atualizar_lista()
    else:
        messagebox.showwarning("Atenção", "ID da nota ou aluno inválido ou não selecionado.")

# Deleta um aluno diretamente
def deletar_aluno():
    aluno_id = entry_id_aluno.get().strip()
    if aluno_id:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("DELETE FROM alunos WHERE aluno_id = %s", (aluno_id,))
        conn.commit()
        conn.close()
        limpar_campos()
        messagebox.showinfo("Sucesso", "Aluno deletado com sucesso!")
        atualizar_lista()
    else:
        messagebox.showwarning("Atenção", "Selecione um aluno para excluir.")

# Busca alunos pelo nome
def buscar_por_nome():
    nome = entry_busca_nome.get()
    for row in tree.get_children():
        tree.delete(row)

    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT n.nota_id, a.aluno_id, a.nome, a.turma, n.disciplina, n.nota
        FROM alunos a
        LEFT JOIN notas n ON a.aluno_id = n.aluno_id
        WHERE a.nome ILIKE %s
        ORDER BY a.aluno_id;
    """, (f"%{nome}%",))
    resultados = cur.fetchall()
    conn.close()

    for linha in resultados:
        tree.insert("", tk.END, values=linha)

# Preenche os campos ao clicar na linha da lista
def preencher_campos(event):
    item = tree.selection()
    if item:
        valores = tree.item(item, 'values')
        if valores:
            limpar_campos()
            if valores[0] and valores[0] != "None":
                entry_nota_id.insert(0, valores[0])
            entry_id_aluno.insert(0, valores[1])
            entry_nome.insert(0, valores[2])
            entry_turma.insert(0, valores[3])
            entry_disciplina.insert(0, valores[4])
            entry_nota.insert(0, valores[5])
            entry_nova_nota.insert(0, valores[5])

# --- INTERFACE GRÁFICA ---
criar_tabelas()
janela = tk.Tk()
janela.title("Sistema de Notas de Alunos")
janela.configure(bg="#f0f4f8")

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview",
                background="#ffffff",
                foreground="black",
                rowheight=25,
                fieldbackground="#f0f4f8")
style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="#dce3ea")
style.map("Treeview", background=[("selected", "#cdeafe")])

font_label = ("Arial", 10)
font_title = ("Arial", 12, "bold")

# --- CADASTRO DE ALUNO ---
tk.Label(janela, text="Cadastro de Aluno", font=font_title, bg="#f0f4f8").grid(row=0, column=0, sticky="w", pady=5)

# Campos de nome e turma
tk.Label(janela, text="Nome:", font=font_label, bg="#f0f4f8").grid(row=1, column=0)
entry_nome = tk.Entry(janela)
entry_nome.grid(row=1, column=1)

tk.Label(janela, text="Turma:", font=font_label, bg="#f0f4f8").grid(row=1, column=2)
entry_turma = tk.Entry(janela)
entry_turma.grid(row=1, column=3)

btn_cadastrar = tk.Button(janela, text="Cadastrar Aluno", bg="#4caf50", fg="white", command=inserir_aluno)
btn_cadastrar.grid(row=1, column=4, padx=10)

btn_deletar_aluno = tk.Button(janela, text="Excluir Aluno", bg="#f44336", fg="white", command=deletar_aluno)
btn_deletar_aluno.grid(row=1, column=5, padx=10)

# --- BUSCA ---
tk.Label(janela, text="Buscar Aluno", font=font_title, bg="#f0f4f8").grid(row=2, column=0, sticky="w", pady=5)

tk.Label(janela, text="Buscar por Nome:", font=font_label, bg="#f0f4f8").grid(row=3, column=0)
entry_busca_nome = tk.Entry(janela)
entry_busca_nome.grid(row=3, column=1)

btn_buscar = tk.Button(janela, text="Buscar", bg="#2196f3", fg="white", command=buscar_por_nome)
btn_buscar.grid(row=3, column=2)

# --- REGISTRO DE NOTA ---
tk.Label(janela, text="Registrar Nota", font=font_title, bg="#f0f4f8").grid(row=4, column=0, sticky="w", pady=5)

tk.Label(janela, text="ID Aluno:", font=font_label, bg="#f0f4f8").grid(row=5, column=0)
entry_id_aluno = tk.Entry(janela)
entry_id_aluno.grid(row=5, column=1)

tk.Label(janela, text="Disciplina:", font=font_label, bg="#f0f4f8").grid(row=5, column=2)
entry_disciplina = tk.Entry(janela)
entry_disciplina.grid(row=5, column=3)

tk.Label(janela, text="Nota:", font=font_label, bg="#f0f4f8").grid(row=5, column=4)
entry_nota = tk.Entry(janela)
entry_nota.grid(row=5, column=5)

btn_registrar = tk.Button(janela, text="Registrar Nota", bg="#4caf50", fg="white", command=registrar_nota)
btn_registrar.grid(row=5, column=6, padx=10)

# --- ATUALIZAR / EXCLUIR NOTA ---
tk.Label(janela, text="Atualizar / Deletar Nota", font=font_title, bg="#f0f4f8").grid(row=6, column=0, sticky="w", pady=5)

tk.Label(janela, text="ID Nota:", font=font_label, bg="#f0f4f8").grid(row=7, column=0)
entry_nota_id = tk.Entry(janela)
entry_nota_id.grid(row=7, column=1)

tk.Label(janela, text="Nova Nota:", font=font_label, bg="#f0f4f8").grid(row=7, column=2)
entry_nova_nota = tk.Entry(janela)
entry_nova_nota.grid(row=7, column=3)

btn_atualizar = tk.Button(janela, text="Atualizar Nota", bg="#ff9800", fg="white", command=atualizar_nota)
btn_atualizar.grid(row=7, column=4)

btn_deletar = tk.Button(janela, text="Deletar Nota", bg="#f44336", fg="white", command=deletar_nota)
btn_deletar.grid(row=7, column=5)

# --- LISTAGEM DE DADOS ---
tree = ttk.Treeview(janela, columns=("ID Nota", "ID", "Nome", "Turma", "Disciplina", "Nota"), show="headings")
tree.heading("ID Nota", text="")
tree.heading("ID", text="ID Aluno")
tree.heading("Nome", text="Nome")
tree.heading("Turma", text="Turma")
tree.heading("Disciplina", text="Disciplina")
tree.heading("Nota", text="Nota")
tree.grid(row=8, column=0, columnspan=7, pady=10)
tree.bind("<ButtonRelease-1>", preencher_campos)
tree.column("ID Nota", width=0, stretch=False)

# Inicia a aplicação
atualizar_lista()
janela.mainloop()
