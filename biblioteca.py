import sqlite3
from tkinter import *
from tkinter import messagebox
from datetime import datetime




# Funções para o banco de dados
def conectar_banco():
    conn = sqlite3.connect('biblioteca.db')
    return conn




def criar_tabelas():
    conn = conectar_banco()
    cursor = conn.cursor()
   
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            disponivel BOOLEAN DEFAULT TRUE
        )
    ''')
   
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    ''')
   
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Emprestimos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            livro_id INTEGER,
            usuario_id INTEGER,
            data_emprestimo TEXT NOT NULL,
            data_devolucao TEXT,
            FOREIGN KEY (livro_id) REFERENCES Livros(id),
            FOREIGN KEY (usuario_id) REFERENCES Usuarios(id)
        )
    ''')
   
    conn.commit()
    conn.close()




# Funções para cadastrar dados
def cadastrar_livro():
    titulo = entry_titulo.get()
    autor = entry_autor.get()
   
    if titulo and autor:
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO Livros (titulo, autor) VALUES (?, ?)', (titulo, autor))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Livro cadastrado com sucesso!")
        entry_titulo.delete(0, END)
        entry_autor.delete(0, END)
        listar_livros_disponiveis()
    else:
        messagebox.showwarning("Erro", "Preencha todos os campos!")



# Funções para empréstimos e devoluções
def registrar_emprestimo():
    livro_id = entry_livro_id.get()
    usuario_id = entry_usuario_id.get()
   
    if livro_id and usuario_id:
        conn = conectar_banco()
        cursor = conn.cursor()
       
        # Verifica se o livro está disponível
        cursor.execute('SELECT disponivel FROM Livros WHERE id = ?', (livro_id,))
        livro = cursor.fetchone()


        # Verifica se o livro está disponível
        cursor.execute('SELECT * FROM Usuarios WHERE id = ?', (usuario_id,))
        usuario = cursor.fetchone()        
       
        if livro and livro[0]:
            if usuario and usuario[0]:
                data_emprestimo = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute('INSERT INTO Emprestimos (livro_id, usuario_id, data_emprestimo) VALUES (?, ?, ?)',
                            (livro_id, usuario_id, data_emprestimo))
                cursor.execute('UPDATE Livros SET disponivel = FALSE WHERE id = ?', (livro_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Sucesso", "Empréstimo registrado com sucesso!")
                entry_livro_id.delete(0, END)
                entry_usuario_id.delete(0, END)
                listar_livros_disponiveis()
                listar_emprestimos_ativos()
            else:
                messagebox.showwarning("Erro", "Usuário não disponível ou ID inválido!")
        else:
            messagebox.showwarning("Erro", "Livro não disponível ou ID inválido!")
    else:
        messagebox.showwarning("Erro", "Preencha todos os campos!")




def registrar_devolucao():
    emprestimo_id = entry_emprestimo_id.get()
   
    if emprestimo_id:
        conn = conectar_banco()
        cursor = conn.cursor()
       
        # Verifica se o empréstimo existe
        cursor.execute('SELECT livro_id FROM Emprestimos WHERE id = ? AND data_devolucao IS NULL', (emprestimo_id,))
        emprestimo = cursor.fetchone()
       
        if emprestimo:
            data_devolucao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('UPDATE Emprestimos SET data_devolucao = ? WHERE id = ?', (data_devolucao, emprestimo_id))
            cursor.execute('UPDATE Livros SET disponivel = TRUE WHERE id = ?', (emprestimo[0],))
            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", "Devolução registrada com sucesso!")
            entry_emprestimo_id.delete(0, END)
            listar_livros_disponiveis()
            listar_emprestimos_ativos()
        else:
            messagebox.showwarning("Erro", "ID de empréstimo inválido ou já devolvido!")
    else:
        messagebox.showwarning("Erro", "Preencha o campo de ID de empréstimo!")




# Funções para listar dados
def listar_livros_disponiveis():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('SELECT id, titulo, autor FROM Livros WHERE disponivel = TRUE')
    livros = cursor.fetchall()
    conn.close()
   
    listbox_livros.delete(0, END)
    for livro in livros:
        listbox_livros.insert(END, f"ID: {livro[0]} | Título: {livro[1]} | Autor: {livro[2]}")




def listar_emprestimos_ativos():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM Emprestimos
    ''')
    cursor.execute('''
        SELECT Emprestimos.id, Livros.titulo, Usuarios.nome, Emprestimos.data_emprestimo
        FROM Emprestimos
        JOIN Livros ON Emprestimos.livro_id = Livros.id
        JOIN Usuarios ON Emprestimos.usuario_id = Usuarios.id
        WHERE Emprestimos.data_devolucao IS NULL
    ''')


    emprestimos = cursor.fetchall()
    conn.close()
   
    listbox_emprestimos.delete(0, END)
    for emprestimo in emprestimos:
        listbox_emprestimos.insert(END, f"ID: {emprestimo[0]} | Livro: {emprestimo[1]} | Usuário: {emprestimo[2]} | Data: {emprestimo[3]}")




criar_tabelas()


# Interface gráfica
root = Tk()
root.title("Sistema de Gestão de Biblioteca")
root.geometry("800x600")




# Cadastro de Livros
frame_livros = LabelFrame(root, text="Cadastro de Livros", padx=10, pady=10)
frame_livros.pack(fill="x", padx=10, pady=5)




Label(frame_livros, text="Título:").grid(row=0, column=0)
entry_titulo = Entry(frame_livros, width=30)
entry_titulo.grid(row=0, column=1)




Label(frame_livros, text="Autor:").grid(row=1, column=0)
entry_autor = Entry(frame_livros, width=30)
entry_autor.grid(row=1, column=1)




Button(frame_livros, text="Cadastrar Livro", command=cadastrar_livro).grid(row=2, column=0, columnspan=2)




# Cadastro de Usuários
frame_usuarios = LabelFrame(root, text="Cadastro de Usuários", padx=10, pady=10)
frame_usuarios.pack(fill="x", padx=10, pady=5)




Label(frame_usuarios, text="Nome:").grid(row=0, column=0)
entry_nome = Entry(frame_usuarios, width=30)
entry_nome.grid(row=0, column=1)




Label(frame_usuarios, text="Email:").grid(row=1, column=0)
entry_email = Entry(frame_usuarios, width=30)
entry_email.grid(row=1, column=1)




Button(frame_usuarios, text="Cadastrar Usuário", command=cadastrar_usuario).grid(row=2, column=0, columnspan=2)




# Empréstimos e Devoluções
frame_emprestimos = LabelFrame(root, text="Empréstimos e Devoluções", padx=10, pady=10)
frame_emprestimos.pack(fill="x", padx=10, pady=5)




Label(frame_emprestimos, text="ID do Livro:").grid(row=0, column=0)
entry_livro_id = Entry(frame_emprestimos, width=10)
entry_livro_id.grid(row=0, column=1)




Label(frame_emprestimos, text="ID do Usuário:").grid(row=0, column=2)
entry_usuario_id = Entry(frame_emprestimos, width=10)
entry_usuario_id.grid(row=0, column=3)




Button(frame_emprestimos, text="Registrar Empréstimo", command=registrar_emprestimo).grid(row=1, column=0, columnspan=2)




Label(frame_emprestimos, text="ID do Empréstimo:").grid(row=2, column=0)
entry_emprestimo_id = Entry(frame_emprestimos, width=10)
entry_emprestimo_id.grid(row=2, column=1)




Button(frame_emprestimos, text="Registrar Devolução", command=registrar_devolucao).grid(row=3, column=0, columnspan=2)




# Listagem de Livros Disponíveis
frame_listagem = LabelFrame(root, text="Livros Disponíveis", padx=10, pady=10)
frame_listagem.pack(fill="both", expand=True, padx=10, pady=5)




listbox_livros = Listbox(frame_listagem, width=100, height=5)
listbox_livros.pack(fill="both", expand=True)




Button(frame_listagem, text="Atualizar Lista", command=listar_livros_disponiveis,).pack()




# Listagem de Empréstimos Ativos
frame_emprestimos_ativos = LabelFrame(root, text="Empréstimos Ativos", padx=10, pady=10)
frame_emprestimos_ativos.pack(fill="both", expand=True, padx=10, pady=5)




listbox_emprestimos = Listbox(frame_emprestimos_ativos, width=100, height=5)
listbox_emprestimos.pack(fill="both", expand=True)




Button(frame_emprestimos_ativos, text="Atualizar Lista", command=listar_emprestimos_ativos).pack()


listar_livros_disponiveis()
listar_emprestimos_ativos()


root.mainloop()