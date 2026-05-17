import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

import psutil


APP_TITLE = "Optimizador de Memoria"
UPDATE_INTERVAL_MS = 5000
HIGH_MEMORY_MB = 500
VERY_HIGH_MEMORY_MB = 1000


class OptimizadorMemoriaApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1180x720")
        self.root.minsize(1060, 650)
        self.root.configure(bg="#eef2f6")
        self.root.report_callback_exception = self.mostrar_error_inesperado

        self.medicion_antes = None
        self.medicion_despues = None
        self.after_id = None
        self.procesos_cache = []
        self.sort_reverse = True
        self.current_pid = os.getpid()

        self.procesos_protegidos = self.obtener_procesos_protegidos()
        self.aplicaciones_comunes = {
            "chrome.exe", "brave.exe", "msedge.exe", "firefox.exe", "opera.exe",
            "code.exe", "devenv.exe", "pycharm64.exe", "notepad.exe", "notepad++.exe",
            "discord.exe", "teams.exe", "slack.exe", "zoom.exe", "spotify.exe",
            "steam.exe", "epicgameslauncher.exe", "word.exe", "excel.exe",
            "powerpnt.exe", "outlook.exe", "onedrive.exe",
        }

        self.configurar_estilos()
        self.crear_interfaz()
        self.actualizar_todo()

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")

        colors = {
            "bg": "#eef2f6",
            "surface": "#ffffff",
            "line": "#d8e0ea",
            "text": "#1f2937",
            "muted": "#64748b",
            "primary": "#2563eb",
            "primary_hover": "#1d4ed8",
            "success": "#16a34a",
            "warning": "#d97706",
            "danger": "#dc2626",
        }
        self.colors = colors

        style.configure("TFrame", background=colors["bg"])
        style.configure("Surface.TFrame", background=colors["surface"])
        style.configure("TLabel", background=colors["bg"], foreground=colors["text"], font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=colors["bg"], foreground=colors["muted"], font=("Segoe UI", 9))
        style.configure("Title.TLabel", background=colors["bg"], foreground=colors["text"], font=("Segoe UI", 20, "bold"))
        style.configure("Section.TLabel", background=colors["surface"], foreground=colors["text"], font=("Segoe UI", 11, "bold"))
        style.configure("CardTitle.TLabel", background=colors["surface"], foreground=colors["muted"], font=("Segoe UI", 9))
        style.configure("CardValue.TLabel", background=colors["surface"], foreground=colors["text"], font=("Segoe UI", 18, "bold"))
        style.configure("CardMeta.TLabel", background=colors["surface"], foreground=colors["muted"], font=("Segoe UI", 9))

        style.configure("TButton", font=("Segoe UI", 10), padding=(12, 8), borderwidth=0)
        style.map("TButton", background=[("active", "#e2e8f0")])
        style.configure("Primary.TButton", background=colors["primary"], foreground="#ffffff")
        style.map("Primary.TButton", background=[("active", colors["primary_hover"])], foreground=[("active", "#ffffff")])
        style.configure("Danger.TButton", background="#fee2e2", foreground=colors["danger"])
        style.map("Danger.TButton", background=[("active", "#fecaca")])

        style.configure("TNotebook", background=colors["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", font=("Segoe UI", 10), padding=(18, 9), background="#e2e8f0")
        style.map("TNotebook.Tab", background=[("selected", colors["surface"])], foreground=[("selected", colors["primary"])])

        style.configure("Treeview", background=colors["surface"], foreground=colors["text"], fieldbackground=colors["surface"],
                        rowheight=30, borderwidth=0, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background="#f8fafc", foreground=colors["text"], font=("Segoe UI", 9, "bold"))
        style.map("Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", colors["text"])])

        style.configure("Green.Horizontal.TProgressbar", troughcolor="#e5e7eb", background=colors["success"], thickness=14)
        style.configure("Amber.Horizontal.TProgressbar", troughcolor="#e5e7eb", background=colors["warning"], thickness=14)
        style.configure("Red.Horizontal.TProgressbar", troughcolor="#e5e7eb", background=colors["danger"], thickness=14)

    def crear_interfaz(self):
        contenedor = ttk.Frame(self.root, padding=18)
        contenedor.pack(fill="both", expand=True)

        encabezado = ttk.Frame(contenedor)
        encabezado.pack(fill="x", pady=(0, 14))
        ttk.Label(encabezado, text=APP_TITLE, style="Title.TLabel").pack(side="left", anchor="w")

        acciones = ttk.Frame(encabezado)
        acciones.pack(side="right")
        ttk.Button(acciones, text="Actualizar ahora", command=self.actualizar_manual).pack(side="left", padx=(0, 8))
        ttk.Button(acciones, text="Guardar estado inicial", command=self.tomar_medicion_antes).pack(side="left", padx=(0, 8))
        ttk.Button(acciones, text="Guardar estado final", command=self.tomar_medicion_despues).pack(side="left")

        self.notebook = ttk.Notebook(contenedor)
        self.notebook.pack(fill="both", expand=True)

        self.tab_monitor = ttk.Frame(self.notebook, padding=14)
        self.tab_procesos = ttk.Frame(self.notebook, padding=14)
        self.tab_optimizacion = ttk.Frame(self.notebook, padding=14)

        self.notebook.add(self.tab_monitor, text="Monitor")
        self.notebook.add(self.tab_procesos, text="Procesos")
        self.notebook.add(self.tab_optimizacion, text="Comparación")

        self.crear_tab_monitor()
        self.crear_tab_procesos()
        self.crear_tab_optimizacion()

    def crear_tab_monitor(self):
        panel_tarjetas = ttk.Frame(self.tab_monitor)
        panel_tarjetas.pack(fill="x", pady=(0, 14))

        self.card_total = self.crear_tarjeta(panel_tarjetas, "RAM total", "0 GB", "Instalada")
        self.card_usada = self.crear_tarjeta(panel_tarjetas, "RAM usada", "0 GB", "0%")
        self.card_disponible = self.crear_tarjeta(panel_tarjetas, "RAM disponible", "0 GB", "Lista para usar")
        self.card_estado = self.crear_tarjeta(panel_tarjetas, "Estado", "Analizando", "Memoria y paginación")

        panel_barras = self.crear_panel(self.tab_monitor, "Uso actual")
        panel_barras.pack(fill="x", pady=(0, 14))

        self.barra_ram, self.lbl_ram_porcentaje = self.crear_barra(panel_barras, "RAM")
        self.barra_swap, self.lbl_swap_porcentaje = self.crear_barra(panel_barras, "Memoria virtual / archivo de paginación")

        panel_diagnostico = self.crear_panel(self.tab_monitor, "Diagnóstico")
        panel_diagnostico.pack(fill="both", expand=True)
        self.txt_diagnostico = self.crear_texto(panel_diagnostico, height=8)

    def crear_tab_procesos(self):
        panel_filtros = self.crear_panel(self.tab_procesos, "Procesos activos")
        panel_filtros.pack(fill="x", pady=(0, 12))

        fila = ttk.Frame(panel_filtros, style="Surface.TFrame")
        fila.pack(fill="x", padx=14, pady=12)

        ttk.Label(fila, text="Buscar", style="Section.TLabel").pack(side="left", padx=(0, 8))
        self.busqueda = tk.StringVar()
        self.busqueda.trace_add("write", lambda *_: self.actualizar_procesos())
        entrada_busqueda = ttk.Entry(fila, textvariable=self.busqueda, width=30)
        entrada_busqueda.pack(side="left", padx=(0, 12))

        self.solo_alto_consumo = tk.BooleanVar(value=False)
        chk_alto = ttk.Checkbutton(
            fila,
            text=f"Solo alto consumo (+{HIGH_MEMORY_MB} MB)",
            variable=self.solo_alto_consumo,
            command=self.actualizar_procesos,
        )
        chk_alto.pack(side="left", padx=(0, 12))

        ttk.Button(fila, text="Limpiar filtros", command=self.limpiar_filtros).pack(side="left", padx=(0, 12))
        ttk.Button(fila, text="Finalizar seleccionado", style="Danger.TButton",
                   command=self.finalizar_proceso_seleccionado).pack(side="right")

        self.lbl_resumen_procesos = ttk.Label(panel_filtros, text="", style="Muted.TLabel")
        self.lbl_resumen_procesos.pack(anchor="w", padx=14, pady=(0, 12))

        panel_tabla = self.crear_panel(self.tab_procesos, "Ordenado por memoria usada")
        panel_tabla.pack(fill="both", expand=True)

        columnas = ("pid", "nombre", "memoria", "porcentaje", "tipo", "seguridad")
        self.tabla_procesos = ttk.Treeview(panel_tabla, columns=columnas, show="headings", selectmode="browse")
        headings = {
            "pid": "PID",
            "nombre": "Proceso",
            "memoria": "Memoria",
            "porcentaje": "% RAM",
            "tipo": "Clasificación",
            "seguridad": "Cierre",
        }
        for columna, texto in headings.items():
            if columna == "memoria":
                self.tabla_procesos.heading(columna, text=texto, command=self.cambiar_orden_memoria)
            else:
                self.tabla_procesos.heading(columna, text=texto)

        self.tabla_procesos.column("pid", width=80, anchor="center", stretch=False)
        self.tabla_procesos.column("nombre", width=250)
        self.tabla_procesos.column("memoria", width=120, anchor="e", stretch=False)
        self.tabla_procesos.column("porcentaje", width=90, anchor="center", stretch=False)
        self.tabla_procesos.column("tipo", width=165, anchor="center")
        self.tabla_procesos.column("seguridad", width=260)

        self.tabla_procesos.tag_configure("protegido", foreground="#b91c1c")
        self.tabla_procesos.tag_configure("alto", foreground="#92400e")
        self.tabla_procesos.tag_configure("usuario", foreground="#166534")
        self.tabla_procesos.tag_configure("normal", foreground="#334155")

        scrollbar = ttk.Scrollbar(panel_tabla, orient="vertical", command=self.tabla_procesos.yview)
        self.tabla_procesos.configure(yscrollcommand=scrollbar.set)
        self.tabla_procesos.pack(side="left", fill="both", expand=True, padx=(14, 0), pady=(0, 14))
        scrollbar.pack(side="right", fill="y", padx=(0, 14), pady=(0, 14))

    def crear_tab_optimizacion(self):
        panel_mediciones = ttk.Frame(self.tab_optimizacion)
        panel_mediciones.pack(fill="x", pady=(0, 14))

        self.lbl_antes = self.crear_caja_medicion(panel_mediciones, "Estado inicial")
        self.lbl_despues = self.crear_caja_medicion(panel_mediciones, "Estado final")
        self.lbl_resultado = self.crear_caja_medicion(panel_mediciones, "Resultado")

        panel_detalle = self.crear_panel(self.tab_optimizacion, "Comparación de optimización")
        panel_detalle.pack(fill="both", expand=True)
        self.txt_optimizacion = self.crear_texto(panel_detalle, height=9)
        self.actualizar_texto_optimizacion()

    def crear_panel(self, padre, titulo):
        panel = ttk.Frame(padre, style="Surface.TFrame", padding=(0, 12, 0, 0))
        ttk.Label(panel, text=titulo, style="Section.TLabel").pack(anchor="w", padx=14, pady=(0, 10))
        return panel

    def crear_tarjeta(self, padre, titulo, valor, detalle):
        tarjeta = tk.Frame(padre, bg=self.colors["surface"], highlightbackground=self.colors["line"],
                           highlightthickness=1, bd=0)
        tarjeta.pack(side="left", fill="x", expand=True, padx=(0, 10))

        lbl_titulo = ttk.Label(tarjeta, text=titulo, style="CardTitle.TLabel")
        lbl_valor = ttk.Label(tarjeta, text=valor, style="CardValue.TLabel")
        lbl_detalle = ttk.Label(tarjeta, text=detalle, style="CardMeta.TLabel")
        lbl_titulo.pack(anchor="w", padx=14, pady=(12, 3))
        lbl_valor.pack(anchor="w", padx=14)
        lbl_detalle.pack(anchor="w", padx=14, pady=(3, 12))
        return {"valor": lbl_valor, "detalle": lbl_detalle}

    def crear_barra(self, padre, titulo):
        fila = ttk.Frame(padre, style="Surface.TFrame")
        fila.pack(fill="x", padx=14, pady=(0, 12))
        ttk.Label(fila, text=titulo, style="CardTitle.TLabel").pack(anchor="w")
        barra = ttk.Progressbar(fila, maximum=100, style="Green.Horizontal.TProgressbar")
        barra.pack(fill="x", pady=(5, 3))
        etiqueta = ttk.Label(fila, text="0%", style="CardMeta.TLabel")
        etiqueta.pack(anchor="w")
        return barra, etiqueta

    def crear_texto(self, padre, height):
        texto = tk.Text(
            padre,
            height=height,
            wrap="word",
            bd=0,
            padx=12,
            pady=10,
            bg="#f8fafc",
            fg=self.colors["text"],
            font=("Segoe UI", 10),
            relief="flat",
        )
        texto.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        texto.config(state="disabled")
        return texto

    def crear_caja_medicion(self, padre, titulo):
        panel = self.crear_panel(padre, titulo)
        panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        etiqueta = ttk.Label(panel, text="Sin datos", justify="left", style="CardMeta.TLabel")
        etiqueta.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        return etiqueta

    def actualizar_manual(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.actualizar_todo()

    def actualizar_todo(self):
        try:
            memoria = psutil.virtual_memory()
            swap = psutil.swap_memory()
            self.actualizar_tarjetas(memoria, swap)
            self.actualizar_diagnostico(memoria, swap)
            self.actualizar_procesos()
        except (psutil.Error, OSError) as error:
            self.mostrar_mensaje_estado(f"No se pudo actualizar la información del sistema: {error}")
        except Exception as error:
            self.mostrar_mensaje_estado(f"Ocurrió un error inesperado al actualizar: {error}")
        finally:
            self.after_id = self.root.after(UPDATE_INTERVAL_MS, self.actualizar_todo)

    def actualizar_tarjetas(self, memoria, swap):
        estado = self.obtener_estado(memoria.percent, swap.percent)
        self.card_total["valor"].config(text=f"{self.bytes_a_gb(memoria.total)} GB")
        self.card_total["detalle"].config(text="Memoria física")
        self.card_usada["valor"].config(text=f"{self.bytes_a_gb(memoria.used)} GB")
        self.card_usada["detalle"].config(text=f"{memoria.percent:.1f}% en uso")
        self.card_disponible["valor"].config(text=f"{self.bytes_a_gb(memoria.available)} GB")
        self.card_disponible["detalle"].config(text="Disponible ahora")
        self.card_estado["valor"].config(text=estado)
        self.card_estado["detalle"].config(text=f"Paginación: {swap.percent:.1f}%")

        self.configurar_barra(self.barra_ram, memoria.percent)
        self.configurar_barra(self.barra_swap, swap.percent)
        self.lbl_ram_porcentaje.config(text=f"{memoria.percent:.1f}% de RAM utilizada")
        self.lbl_swap_porcentaje.config(text=f"{swap.percent:.1f}% de memoria virtual utilizada")

    def actualizar_procesos(self):
        if not hasattr(self, "tabla_procesos"):
            return

        filtro = self.busqueda.get().strip().lower() if hasattr(self, "busqueda") else ""
        solo_alto = self.solo_alto_consumo.get() if hasattr(self, "solo_alto_consumo") else False
        procesos = self.obtener_procesos(filtro=filtro, solo_alto=solo_alto)
        self.procesos_cache = procesos
        self.renderizar_procesos(procesos)

    def obtener_procesos(self, filtro="", solo_alto=False):
        memoria_total = max(psutil.virtual_memory().total, 1)
        procesos = []

        for proceso in psutil.process_iter(["pid", "name", "memory_info", "username"]):
            try:
                info = proceso.info
                nombre = info.get("name") or "Desconocido"
                nombre_lower = nombre.lower()
                if filtro and filtro not in nombre_lower:
                    continue

                memoria_bytes = info["memory_info"].rss if info.get("memory_info") else 0
                memoria_mb = self.bytes_a_mb(memoria_bytes)
                if solo_alto and memoria_mb < HIGH_MEMORY_MB:
                    continue

                tipo, seguridad, protegido = self.clasificar_proceso(proceso, nombre_lower, memoria_mb)
                procesos.append({
                    "pid": info["pid"],
                    "nombre": nombre,
                    "memoria_mb": memoria_mb,
                    "porcentaje": round((memoria_bytes / memoria_total) * 100, 2),
                    "tipo": tipo,
                    "seguridad": seguridad,
                    "protegido": protegido,
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except (OSError, ValueError):
                continue

        procesos.sort(key=lambda item: item["memoria_mb"], reverse=self.sort_reverse)
        return procesos

    def renderizar_procesos(self, procesos):
        self.tabla_procesos.delete(*self.tabla_procesos.get_children())

        for proceso in procesos:
            tag = self.obtener_tag_proceso(proceso)
            self.tabla_procesos.insert(
                "",
                "end",
                iid=str(proceso["pid"]),
                values=(
                    proceso["pid"],
                    proceso["nombre"],
                    f"{proceso['memoria_mb']:.1f} MB",
                    f"{proceso['porcentaje']:.2f}%",
                    proceso["tipo"],
                    proceso["seguridad"],
                ),
                tags=(tag,),
            )

        sentido = "mayor a menor" if self.sort_reverse else "menor a mayor"
        self.lbl_resumen_procesos.config(
            text=f"{len(procesos)} procesos mostrados. Orden de memoria: {sentido}."
        )

    def clasificar_proceso(self, proceso, nombre_lower, memoria_mb):
        pid = proceso.pid
        if pid == self.current_pid:
            return "Aplicación actual", "Protegido: este programa", True

        if self.es_proceso_critico(pid, nombre_lower):
            return "Sistema protegido", "No cerrar", True

        if memoria_mb >= VERY_HIGH_MEMORY_MB:
            return "Consumo muy alto", "Seguro solo si reconoces la app", False

        if memoria_mb >= HIGH_MEMORY_MB:
            return "Consumo alto", "Candidato si no está en uso", False

        if nombre_lower in self.aplicaciones_comunes:
            return "Aplicación de usuario", "Seguro si la reconoces", False

        if memoria_mb >= 200:
            return "Consumo medio", "Revisar antes de cerrar", False

        return "Consumo bajo", "Mantener", False

    def es_proceso_critico(self, pid, nombre_lower):
        if pid in (0, 4):
            return True
        return nombre_lower in self.procesos_protegidos

    def obtener_tag_proceso(self, proceso):
        if proceso["protegido"]:
            return "protegido"
        if proceso["memoria_mb"] >= HIGH_MEMORY_MB:
            return "alto"
        if proceso["tipo"] == "Aplicación de usuario":
            return "usuario"
        return "normal"

    def cambiar_orden_memoria(self):
        self.sort_reverse = not self.sort_reverse
        self.actualizar_procesos()

    def limpiar_filtros(self):
        self.busqueda.set("")
        self.solo_alto_consumo.set(False)
        self.actualizar_procesos()

    def finalizar_proceso_seleccionado(self):
        seleccion = self.tabla_procesos.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Selecciona un proceso de la tabla.")
            return

        pid = int(seleccion[0])
        proceso = self.buscar_proceso_cache(pid)
        if not proceso:
            messagebox.showinfo("Proceso no disponible", "El proceso ya no aparece en la lista.")
            self.actualizar_manual()
            return

        if proceso["protegido"] or self.es_proceso_critico(pid, proceso["nombre"].lower()):
            messagebox.showerror(
                "Proceso protegido",
                "Este proceso parece ser parte de Windows o de la propia aplicación. No se puede finalizar desde aquí.",
            )
            return

        if not self.confirmar_cierre(proceso):
            return

        self.terminar_proceso(pid, proceso["nombre"])

    def buscar_proceso_cache(self, pid):
        return next((proceso for proceso in self.procesos_cache if proceso["pid"] == pid), None)

    def confirmar_cierre(self, proceso):
        mensaje = (
            f"Proceso: {proceso['nombre']}\n"
            f"PID: {proceso['pid']}\n"
            f"Memoria: {proceso['memoria_mb']:.1f} MB\n\n"
            "Cierra el proceso solo si reconoces la aplicación y no estás usando datos sin guardar."
        )
        return messagebox.askyesno("Finalizar proceso", mensaje, icon="warning")

    def terminar_proceso(self, pid, nombre):
        try:
            proceso = psutil.Process(pid)
            nombre_actual = (proceso.name() or "").lower()
            if nombre_actual != nombre.lower() or self.es_proceso_critico(pid, nombre_actual):
                messagebox.showerror(
                    "Proceso cambiado",
                    "El proceso seleccionado cambió o ahora parece protegido. Actualiza la lista e inténtalo de nuevo.",
                )
                self.actualizar_manual()
                return

            proceso.terminate()
            try:
                proceso.wait(timeout=3)
            except psutil.TimeoutExpired:
                proceso.kill()
                proceso.wait(timeout=2)
        except psutil.NoSuchProcess:
            messagebox.showinfo("Proceso no encontrado", "El proceso ya terminó.")
        except psutil.AccessDenied:
            messagebox.showerror("Acceso denegado", "Windows no permitió finalizar este proceso.")
            return
        except psutil.TimeoutExpired:
            messagebox.showerror("Tiempo agotado", "El proceso no respondió al intento de cierre.")
            return
        except (psutil.Error, OSError) as error:
            messagebox.showerror("No se pudo finalizar", f"Windows devolvió este error:\n{error}")
            return
        except Exception as error:
            messagebox.showerror("Error inesperado", f"No se pudo finalizar el proceso:\n{error}")
            return

        messagebox.showinfo("Proceso finalizado", f"{nombre} fue finalizado correctamente.")
        self.medicion_despues = self.obtener_medicion_actual()
        self.lbl_despues.config(text=self.formatear_medicion(self.medicion_despues))
        self.actualizar_resultado_optimizacion()
        self.actualizar_texto_optimizacion()
        self.actualizar_manual()

    def tomar_medicion_antes(self):
        self.medicion_antes = self.obtener_medicion_actual()
        self.medicion_despues = None
        self.lbl_antes.config(text=self.formatear_medicion(self.medicion_antes))
        self.lbl_despues.config(text="Sin datos")
        self.actualizar_resultado_optimizacion()
        self.actualizar_texto_optimizacion()
        messagebox.showinfo("Estado inicial guardado", "Se guardó la medición actual del sistema.")

    def tomar_medicion_despues(self):
        self.medicion_despues = self.obtener_medicion_actual()
        self.lbl_despues.config(text=self.formatear_medicion(self.medicion_despues))
        self.actualizar_resultado_optimizacion()
        self.actualizar_texto_optimizacion()
        messagebox.showinfo("Estado final guardado", "Se guardó la medición posterior.")

    def obtener_medicion_actual(self):
        memoria = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "ram_usada_gb": self.bytes_a_gb(memoria.used),
            "ram_disponible_gb": self.bytes_a_gb(memoria.available),
            "ram_porcentaje": round(memoria.percent, 1),
            "swap_porcentaje": round(swap.percent, 1),
            "procesos": len(psutil.pids()),
        }

    def formatear_medicion(self, medicion):
        return (
            f"{medicion['fecha']}\n"
            f"RAM usada: {medicion['ram_usada_gb']:.2f} GB\n"
            f"RAM disponible: {medicion['ram_disponible_gb']:.2f} GB\n"
            f"Uso de RAM: {medicion['ram_porcentaje']:.1f}%\n"
            f"Memoria virtual: {medicion['swap_porcentaje']:.1f}%\n"
            f"Procesos activos: {medicion['procesos']}"
        )

    def actualizar_resultado_optimizacion(self):
        if not self.medicion_antes or not self.medicion_despues:
            self.lbl_resultado.config(text="Guarda un estado inicial y uno final para comparar.")
            return

        resultado = self.calcular_resultado()
        self.lbl_resultado.config(text=self.formatear_resultado(resultado))

    def calcular_resultado(self):
        antes = self.medicion_antes
        despues = self.medicion_despues
        ram_liberada_gb = round(antes["ram_usada_gb"] - despues["ram_usada_gb"], 2)
        porcentaje_liberado = round(antes["ram_porcentaje"] - despues["ram_porcentaje"], 2)
        disponible_extra_gb = round(despues["ram_disponible_gb"] - antes["ram_disponible_gb"], 2)
        diferencia_procesos = antes["procesos"] - despues["procesos"]

        if ram_liberada_gb > 0.05 or disponible_extra_gb > 0.05 or diferencia_procesos > 0:
            estado = "Positiva"
        elif ram_liberada_gb < -0.05 and disponible_extra_gb < -0.05:
            estado = "Negativa"
        else:
            estado = "Neutral"

        return {
            "estado": estado,
            "ram_liberada_gb": ram_liberada_gb,
            "porcentaje_liberado": porcentaje_liberado,
            "disponible_extra_gb": disponible_extra_gb,
            "diferencia_procesos": diferencia_procesos,
        }

    def formatear_resultado(self, resultado):
        return (
            f"Optimización: {resultado['estado']}\n"
            f"RAM liberada: {resultado['ram_liberada_gb']:.2f} GB\n"
            f"Cambio en uso de RAM: {resultado['porcentaje_liberado']:.2f}%\n"
            f"RAM disponible adicional: {resultado['disponible_extra_gb']:.2f} GB\n"
            f"Diferencia de procesos: {resultado['diferencia_procesos']}"
        )

    def actualizar_texto_optimizacion(self):
        if not hasattr(self, "txt_optimizacion"):
            return

        if self.medicion_antes and self.medicion_despues:
            resultado = self.calcular_resultado()
            texto = (
                f"Resultado {resultado['estado'].lower()}.\n\n"
                f"RAM liberada: {resultado['ram_liberada_gb']:.2f} GB "
                f"({resultado['porcentaje_liberado']:.2f}%).\n"
                f"RAM disponible adicional: {resultado['disponible_extra_gb']:.2f} GB.\n"
                f"Procesos activos reducidos: {resultado['diferencia_procesos']}.\n\n"
                "Una mejora real suele verse como menos RAM usada, más memoria disponible o menos procesos activos."
            )
        else:
            texto = (
                "Guarda un estado inicial, cierra solo procesos no esenciales y guarda un estado final. "
                "La comparación mostrará si el cambio fue positivo, neutral o negativo."
            )

        self.escribir_texto(self.txt_optimizacion, texto)

    def actualizar_diagnostico(self, memoria, swap):
        estado = self.obtener_estado(memoria.percent, swap.percent)
        lineas = [
            f"Estado actual: {estado}",
            f"RAM usada: {memoria.percent:.1f}%",
            f"Memoria virtual usada: {swap.percent:.1f}%",
            "",
        ]

        if memoria.percent < 60:
            lineas.append("La carga de memoria es baja. No hace falta cerrar procesos.")
        elif memoria.percent < 80:
            lineas.append("La carga de memoria es moderada. Revisa aplicaciones pesadas que no estés usando.")
        elif memoria.percent < 90:
            lineas.append("La RAM está alta. Conviene cerrar aplicaciones no esenciales.")
        else:
            lineas.append("La RAM está en un nivel crítico. Evita cerrar procesos desconocidos o del sistema.")

        if swap.percent >= 30:
            lineas.append("El archivo de paginación tiene uso notable; el equipo puede sentirse más lento.")
        else:
            lineas.append("La memoria virtual se mantiene en un rango normal.")

        self.escribir_texto(self.txt_diagnostico, "\n".join(lineas))

    def configurar_barra(self, barra, porcentaje):
        if porcentaje >= 90:
            barra.configure(style="Red.Horizontal.TProgressbar")
        elif porcentaje >= 75:
            barra.configure(style="Amber.Horizontal.TProgressbar")
        else:
            barra.configure(style="Green.Horizontal.TProgressbar")
        barra["value"] = porcentaje

    def obtener_estado(self, porcentaje_ram, porcentaje_swap):
        if porcentaje_ram < 60 and porcentaje_swap < 20:
            return "Óptimo"
        if porcentaje_ram < 80:
            return "Carga media"
        if porcentaje_ram < 90:
            return "Uso alto"
        return "Crítico"

    def mostrar_mensaje_estado(self, mensaje):
        if hasattr(self, "txt_diagnostico"):
            self.escribir_texto(self.txt_diagnostico, mensaje)

    def escribir_texto(self, widget, texto):
        widget.config(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert(tk.END, texto)
        widget.config(state="disabled")

    def mostrar_error_inesperado(self, tipo, valor, traceback):
        messagebox.showerror("Error inesperado", f"La aplicación encontró un problema:\n{valor}")

    def bytes_a_gb(self, valor):
        return round(valor / (1024 ** 3), 2)

    def bytes_a_mb(self, valor):
        return round(valor / (1024 ** 2), 2)

    def obtener_procesos_protegidos(self):
        return {
            "system", "system idle process", "registry", "secure system",
            "smss.exe", "csrss.exe", "wininit.exe", "winlogon.exe",
            "services.exe", "lsass.exe", "lsaiso.exe", "svchost.exe",
            "fontdrvhost.exe", "dwm.exe", "explorer.exe", "taskhostw.exe",
            "sihost.exe", "runtimebroker.exe", "searchindexer.exe",
            "searchhost.exe", "startmenuexperiencehost.exe", "shellhost.exe",
            "audiodg.exe", "spoolsv.exe", "wudfhost.exe", "wmiprvse.exe",
            "wmiapsrv.exe", "conhost.exe", "ctfmon.exe", "securityhealthservice.exe",
            "securityhealthsystray.exe", "msmpeng.exe", "nisserv.exe",
            "tiworker.exe", "trustedinstaller.exe", "dllhost.exe",
            "dasHost.exe".lower(), "memory compression",
        }


if __name__ == "__main__":
    root = tk.Tk()
    app = OptimizadorMemoriaApp(root)
    root.mainloop()
