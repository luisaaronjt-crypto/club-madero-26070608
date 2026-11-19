import sqlite3, hashlib, os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "club_madero.db")

def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, user TEXT UNIQUE, pass TEXT, rol TEXT, activo INT DEFAULT 1)")
    c.execute("CREATE TABLE IF NOT EXISTS socios (id INTEGER PRIMARY KEY, folio TEXT UNIQUE, nombre TEXT, tel TEXT, correo TEXT, activo INT DEFAULT 1)")
    c.execute("CREATE TABLE IF NOT EXISTS planes (id INTEGER PRIMARY KEY, nombre TEXT UNIQUE, dias INT, precio REAL, activo INT DEFAULT 1)")
    c.execute("CREATE TABLE IF NOT EXISTS pagos (id INTEGER PRIMARY KEY, socio_id INT, plan_id INT, fecha TEXT, vigencia TEXT, monto REAL)")
    c.execute("SELECT COUNT(*) FROM usuarios")
    if c.fetchone()[0]==0:
        c.execute("INSERT INTO usuarios (user,pass,rol) VALUES (?,?,?)", ("admin", hash_pass("admin123"), "administrador"))
        c.execute("INSERT INTO usuarios (user,pass,rol) VALUES (?,?,?)", ("coach", hash_pass("coach123"), "operador"))
        for i in range(1,9):
            activo = 0 if i==7 else 1
            c.execute("INSERT INTO socios (folio,nombre,tel,correo,activo) VALUES (?,?,?,?,?)", (f"SOC-00{i}", f"Jugador {i} Madero", f"8331000{i}", f"j{i}@madero.com", activo))
        c.execute("INSERT INTO planes (nombre,dias,precio,activo) VALUES ('Mensual Americano',30,500,1)")
        c.execute("INSERT INTO planes (nombre,dias,precio,activo) VALUES ('Quincenal',15,300,1)")
        c.execute("INSERT INTO pagos (socio_id,plan_id,fecha,vigencia,monto) VALUES (1,1,'2026-11-01','2026-12-01',500)")
        c.execute("INSERT INTO pagos (socio_id,plan_id,fecha,vigencia,monto) VALUES (2,2,'2026-10-01','2026-10-16',300)")
    conn.commit()
    conn.close()

init_db()

root = tk.Tk()
root.geometry("1000x600")

login_frame = tk.Frame(root)
login_frame.pack(fill="both", expand=True)
main_frame = tk.Frame(root)

def mostrar_main(user, rol):
    login_frame.pack_forget()
    main_frame.pack(fill="both", expand=True)
    root.title(f"Club Madero - {rol} {user} - 26070608")
    nb = ttk.Notebook(main_frame)
    nb.pack(fill="both", expand=True)

    t1 = tk.Frame(nb); nb.add(t1, text="Socios")
    e_b = tk.Entry(t1); e_b.pack()
    tr1 = ttk.Treeview(t1, columns=("id","folio","nombre","tel","correo","activo"), show="headings")
    for col in ("id","folio","nombre","tel","correo","activo"): tr1.heading(col, text=col)
    tr1.pack(fill="both", expand=True)
    def c1():
        for i in tr1.get_children(): tr1.delete(i)
        conn = sqlite3.connect(DB); cur = conn.cursor()
        cur.execute("SELECT id,folio,nombre,tel,correo,activo FROM socios WHERE nombre LIKE ? OR folio LIKE ?", (f"%{e_b.get()}%", f"%{e_b.get()}%"))
        for r in cur.fetchall(): tr1.insert("", "end", values=r)
        conn.close()
    tk.Button(t1, text="Buscar / Recargar", command=c1).pack()
    c1()

    t2 = tk.Frame(nb); nb.add(t2, text="Planes")
    tr2 = ttk.Treeview(t2, columns=("id","nombre","dias","precio"), show="headings")
    for col in ("id","nombre","dias","precio"): tr2.heading(col, text=col)
    tr2.pack(fill="both", expand=True)
    conn = sqlite3.connect(DB); cur = conn.cursor(); cur.execute("SELECT id,nombre,dias,precio FROM planes")
    for r in cur.fetchall(): tr2.insert("", "end", values=r)
    conn.close()

    t3 = tk.Frame(nb); nb.add(t3, text="Pagos JOIN")
    tr3 = ttk.Treeview(t3, columns=("id","folio","socio","plan","fecha","vigencia","monto"), show="headings")
    for col in ("id","folio","socio","plan","fecha","vigencia","monto"): tr3.heading(col, text=col)
    tr3.pack(fill="both", expand=True)
    def c3():
        for i in tr3.get_children(): tr3.delete(i)
        conn = sqlite3.connect(DB); cur = conn.cursor()
        cur.execute("SELECT pg.id, s.folio, s.nombre, pl.nombre, pg.fecha, pg.vigencia, pg.monto FROM pagos pg JOIN socios s ON pg.socio_id=s.id JOIN planes pl ON pg.plan_id=pl.id")
        for r in cur.fetchall(): tr3.insert("", "end", values=r)
        conn.close()
    tk.Button(t3, text="Ver JOIN", command=c3).pack()
    c3()

    t4 = tk.Frame(nb); nb.add(t4, text="Reporte Vencidos")
    tr4 = ttk.Treeview(t4, columns=("folio","nombre","plan","venc"), show="headings")
    for col in ("folio","nombre","plan","venc"): tr4.heading(col, text=col)
    tr4.pack(fill="both", expand=True)
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("SELECT s.folio, s.nombre, pl.nombre, pg.vigencia FROM pagos pg JOIN socios s ON s.id=pg.socio_id JOIN planes pl ON pl.id=pg.plan_id WHERE date(pg.vigencia) < date('now')")
    for r in cur.fetchall(): tr4.insert("", "end", values=r)
    conn.close()

def login():
    u = e_user.get(); p = hash_pass(e_pass.get())
    conn = sqlite3.connect(DB); cur = conn.cursor()
    cur.execute("SELECT user, rol FROM usuarios WHERE user=? AND pass=? AND activo=1", (u,p))
    row = cur.fetchone(); conn.close()
    if row:
        mostrar_main(row[0], row[1])
    else:
        messagebox.showerror("Error", "Usuario o contraseña mal. Usa admin / admin123")

tk.Label(login_frame, text="CLUB MADERO\nFUTBOL AMERICANO\nOpcion 6", font=("Arial",14,"bold")).pack(pady=20)
tk.Label(login_frame, text="Usuario").pack()
e_user = tk.Entry(login_frame); e_user.pack(); e_user.insert(0,"admin")
tk.Label(login_frame, text="Contrasena").pack()
e_pass = tk.Entry(login_frame, show="*"); e_pass.pack(); e_pass.insert(0,"admin123")
tk.Button(login_frame, text="ENTRAR", width=20, bg="#0d2a54", fg="white", command=login).pack(pady=20)
tk.Label(login_frame, text="admin / admin123 | coach / coach123").pack()

root.mainloop()