import psycopg2
import tkinter as tk
from tkinter import messagebox, ttk
import os
from dotenv import load_dotenv

# === Configurações ===
load_dotenv()
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')

def conectar():
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT
    )

def criar_tabelas():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            aluno_id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            turma TEXT NOT NULL,
            disciplina TEXT,
            nota NUMERIC(5,2)
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS professores (
            professor_id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            disciplina TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

criar_tabelas()

janela = tk.Tk()
janela.title("Sistema de Notas de Alunos")
janela.configure(bg="#f0f4f8")
mostrar_todos = tk.BooleanVar(value=True)

def atualizar_lista():
    carregar_alunos()

def carregar_alunos():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.aluno_id, a.nome, a.turma, a.disciplina, a.nota,
               COALESCE(p.nome, 'Não definido') AS professor
        FROM alunos a
        LEFT JOIN professores p ON a.disciplina = p.disciplina
        ORDER BY a.aluno_id
    """)
    registros = cur.fetchall()
    conn.close()
    tree_alunos.delete(*tree_alunos.get_children())
    for aluno in registros:
        tree_alunos.insert("", tk.END, values=aluno)

def buscar_por_nome():
    nome = entry_busca_nome.get().strip()
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.aluno_id, a.nome, a.turma, a.disciplina, a.nota,
               COALESCE(p.nome, 'Não definido') AS professor
        FROM alunos a
        LEFT JOIN professores p ON a.disciplina = p.disciplina
        WHERE a.nome ILIKE %s
        ORDER BY a.aluno_id
    """, (f"%{nome}%",))
    registros = cur.fetchall()
    conn.close()
    tree_alunos.delete(*tree_alunos.get_children())
    for aluno in registros:
        tree_alunos.insert("", tk.END, values=aluno)

def obter_disciplinas():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT disciplina FROM professores ORDER BY disciplina")
    disciplinas = [row[0] for row in cur.fetchall()]
    conn.close()
    return disciplinas

def buscar_professor_por_disciplina(disciplina):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT nome FROM professores WHERE disciplina = %s LIMIT 1", (disciplina,))
    resultado = cur.fetchone()
    conn.close()
    return resultado[0] if resultado else "Professor não encontrado"

def criar_filtro_alunos(frame):
    filtro_frame = tk.Frame(frame, bg="#f0f4f8")
    filtro_frame.pack(pady=5)
    tk.Label(filtro_frame, text="Buscar por nome:", bg="#f0f4f8").pack(side=tk.LEFT, padx=(10, 2))
    global entry_busca_nome
    entry_busca_nome = tk.Entry(filtro_frame)
    entry_busca_nome.pack(side=tk.LEFT)
    tk.Button(filtro_frame, text="Buscar", command=buscar_por_nome).pack(side=tk.LEFT, padx=5)

def criar_tabela_alunos(frame):
    global tree_alunos
    colunas = ("ID", "Nome", "Turma", "Disciplina", "Nota", "Professor")
    tree_alunos = ttk.Treeview(frame, columns=colunas, show="headings")
    for col in colunas:
        tree_alunos.heading(col, text=col)
        tree_alunos.column(col, anchor=tk.CENTER)
    tree_alunos.pack(fill="both", expand=True, pady=10)
    carregar_alunos()

    btn_excluir = tk.Button(frame, text="Excluir Aluno", command=excluir_aluno,bg="#ff4d4d", fg="white")
    btn_excluir.pack(pady=5)

def excluir_aluno():
    item = tree_alunos.focus()
    if not item:
        messagebox.showwarning("Aviso", "Selecione um aluno para excluir.")
        return

    aluno_id = tree_alunos.item(item, "values")[0]
    aluno_nome = tree_alunos.item(item, "values")[1]

    confirmar = messagebox.askyesno("Confirmar Exclusão", f"Deseja realmente excluir o aluno: {aluno_nome}?")
    if not confirmar:
        return

    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM alunos WHERE aluno_id = %s", (aluno_id,))
    conn.commit()
    conn.close()

    messagebox.showinfo("Sucesso", f"Aluno excluído com sucesso.")
    atualizar_lista()

def criar_tabela_professores(frame):
    global tree_professores
    colunas = ("ID", "Nome", "Disciplina")
    tree_professores = ttk.Treeview(frame, columns=colunas, show="headings")
    for col in colunas:
        tree_professores.heading(col, text=col)
        tree_professores.column(col, anchor=tk.CENTER)
    tree_professores.pack(fill="both", expand=True, pady=10)
    carregar_professores()

def carregar_professores():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT professor_id, nome, disciplina FROM professores ORDER BY professor_id")
    registros = cur.fetchall()
    conn.close()
    tree_professores.delete(*tree_professores.get_children())
    for professor in registros:
        tree_professores.insert("", tk.END, values=professor)

def criar_formulario_cadastro(frame):
    frame_aluno = tk.LabelFrame(frame, text="Cadastro de Alunos", bg="#f0f4f8", padx=10, pady=10)
    frame_aluno.pack(padx=10, pady=10, fill="x")

    tk.Label(frame_aluno, text="Nome do Aluno:", bg="#f0f4f8").pack(anchor="w")
    entry_nome_aluno = tk.Entry(frame_aluno)
    entry_nome_aluno.pack(fill="x", pady=5)

    tk.Label(frame_aluno, text="Turma:", bg="#f0f4f8").pack(anchor="w")
    entry_turma = tk.Entry(frame_aluno)
    entry_turma.pack(fill="x", pady=5)

    def cadastrar_aluno():
        nome = entry_nome_aluno.get().strip()
        turma = entry_turma.get().strip()
        if not nome or not turma:
            messagebox.showwarning("Aviso", "Preencha todos os campos do aluno.")
            return
        conn = conectar()
        cur = conn.cursor()
        cur.execute("INSERT INTO alunos (nome, turma) VALUES (%s, %s)", (nome, turma))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Aluno cadastrado com sucesso!")
        entry_nome_aluno.delete(0, tk.END)
        entry_turma.delete(0, tk.END)
        atualizar_lista()

    tk.Button(frame_aluno, text="Cadastrar Aluno", command=cadastrar_aluno).pack(pady=5)

    frame_nota = tk.LabelFrame(frame, text="Cadastro de Notas", bg="#f0f4f8", padx=10, pady=10)
    frame_nota.pack(padx=10, pady=10, fill="x")

    tk.Label(frame_nota, text="Disciplina:", bg="#f0f4f8").pack(anchor="w")
    
    # Removido o entry_disciplina e mantido apenas o combobox
    combo_disciplina = ttk.Combobox(frame_nota, values=obter_disciplinas(), state="readonly")
    combo_disciplina.pack(fill="x", pady=5)

    label_professor = tk.Label(frame_nota, text="", bg="#f0f4f8", font=("Arial", 12), fg="blue")
    label_professor.pack(anchor="w", pady=(0, 5))

    def atualizar_professor(event):
        disciplina = combo_disciplina.get()
        nome_professor = buscar_professor_por_disciplina(disciplina)
        label_professor.config(text=f"Professor: {nome_professor}")

    combo_disciplina.bind("<<ComboboxSelected>>", atualizar_professor)

    tk.Label(frame_nota, text="Nota:", bg="#f0f4f8").pack(anchor="w")
    entry_nota = tk.Entry(frame_nota)
    entry_nota.pack(fill="x", pady=5)

    def adicionar_nota():
        item = tree_alunos.focus()
        if not item:
            messagebox.showwarning("Aviso", "Selecione um aluno na aba Consulta.")
            return
        
        # Agora usamos apenas o valor do combobox para a disciplina
        disciplina = combo_disciplina.get()
        nota = entry_nota.get().strip()
        
        if not disciplina or not nota:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return
        try:
            nota = float(nota)
        except ValueError:
            messagebox.showerror("Erro", "Nota inválida. Insira um número.")
            return
        conn = conectar()
        cur = conn.cursor()
        aluno_id = tree_alunos.item(item, "values")[0]
        cur.execute("UPDATE alunos SET nota = %s, disciplina = %s WHERE aluno_id = %s", (nota, disciplina, aluno_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Nota adicionada com sucesso!")
        entry_nota.delete(0, tk.END)
        atualizar_lista()

    tk.Button(frame_nota, text="Salvar Nota", command=adicionar_nota).pack(pady=10)

def criar_formulario_professor(frame):
    frame_prof = tk.LabelFrame(frame, text="Cadastro de Professores", bg="#f0f4f8", padx=10, pady=10)
    frame_prof.pack(padx=10, pady=10, fill="x")

    tk.Label(frame_prof, text="Nome do Professor:", bg="#f0f4f8").pack(anchor="w")
    entry_nome_prof = tk.Entry(frame_prof)
    entry_nome_prof.pack(fill="x", pady=5)

    tk.Label(frame_prof, text="Disciplina:", bg="#f0f4f8").pack(anchor="w")
    entry_disciplina = tk.Entry(frame_prof)
    entry_disciplina.pack(fill="x", pady=5)

    def cadastrar():
        nome = entry_nome_prof.get().strip()
        disciplina = entry_disciplina.get().strip()
        if not nome or not disciplina:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return
        conn = conectar()
        cur = conn.cursor()
        cur.execute("INSERT INTO professores (nome, disciplina) VALUES (%s, %s)", (nome, disciplina))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Professor cadastrado com sucesso!")
        entry_nome_prof.delete(0, tk.END)
        entry_disciplina.delete(0, tk.END)
        carregar_professores()

    tk.Button(frame_prof, text="Cadastrar Professor", command=cadastrar).pack(pady=10)

notebook = ttk.Notebook(janela)
notebook.pack(padx=10, pady=10, fill="both", expand=True)


aba1 = tk.Frame(notebook, bg="#f0f4f8")
notebook.add(aba1, text="Consulta e Cadastro")
criar_filtro_alunos(aba1)
criar_formulario_cadastro(aba1)
criar_tabela_alunos(aba1)

aba2 = tk.Frame(notebook, bg="#f0f4f8")
notebook.add(aba2, text="Professores")
criar_formulario_professor(aba2)
criar_tabela_professores(aba2)

try:
    janela.mainloop()
except Exception as e:
    print("Erro ao iniciar a aplicação:", e)
