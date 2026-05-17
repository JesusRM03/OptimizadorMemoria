import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import psutil


class OptimizadorMemoriaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Optimizador de Memoria Multitarea")
        self.root.geometry("1200x750")
        self.root.minsize(1100, 680)

        self.medicion_antes = None
        self.medicion_despues = None
        self.after_id = None

        self.procesos_protegidos = {
            "system",
            "registry",
            "smss.exe",
            "csrss.exe",
            "wininit.exe",
            "winlogon.exe",
            "services.exe",
            "lsass.exe",
            "svchost.exe",
            "fontdrvhost.exe",
            "dwm.exe",
            "explorer.exe"
        }

        self.aplicaciones_comunes = {
            "chrome.exe",
            "brave.exe",
            "msedge.exe",
            "firefox.exe",
            "code.exe",
            "discord.exe",
            "teams.exe",
            "steam.exe",
            "spotify.exe",
            "notepad.exe",
            "word.exe",
            "excel.exe",
            "powerpnt.exe"
        }

        self.configurar_estilos()
        self.crear_interfaz()
        self.actualizar_todo()

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TFrame", background="#f4f6f8")
        style.configure("TLabel", background="#f4f6f8", font=("Segoe UI", 10))
        style.configure("Titulo.TLabel", background="#f4f6f8", font=("Segoe UI", 20, "bold"))
        style.configure("Subtitulo.TLabel", background="#f4f6f8", font=("Segoe UI", 11, "bold"))
        style.configure("Dato.TLabel", background="white", font=("Segoe UI", 16, "bold"))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=(10, 7))
        style.configure("TLabelframe", background="#f4f6f8")
        style.configure("TLabelframe.Label", background="#f4f6f8", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=27)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def crear_interfaz(self):
        contenedor = ttk.Frame(self.root, padding=15)
        contenedor.pack(fill="both", expand=True)

        ttk.Label(
            contenedor,
            text="Optimizador de Memoria Multitarea",
            style="Titulo.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            contenedor,
            text="Analiza el uso de RAM, detecta procesos pesados y permite liberar memoria cerrando procesos no esenciales.",
            style="Subtitulo.TLabel"
        ).pack(anchor="w", pady=(0, 12))

        panel_botones = ttk.Frame(contenedor)
        panel_botones.pack(fill="x", pady=(0, 12))

        ttk.Button(
            panel_botones,
            text="Actualizar",
            command=self.actualizar_manual,
            width=18
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            panel_botones,
            text="Medir antes",
            command=self.tomar_medicion_antes,
            width=18
        ).pack(side="left", padx=8)

        ttk.Button(
            panel_botones,
            text="Medir después",
            command=self.tomar_medicion_despues,
            width=18
        ).pack(side="left", padx=8)

        ttk.Button(
            panel_botones,
            text="Finalizar proceso seleccionado",
            command=self.finalizar_proceso_seleccionado,
            width=30
        ).pack(side="left", padx=8)

        self.notebook = ttk.Notebook(contenedor)
        self.notebook.pack(fill="both", expand=True)

        self.tab_monitor = ttk.Frame(self.notebook, padding=10)
        self.tab_procesos = ttk.Frame(self.notebook, padding=10)
        self.tab_optimizacion = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.tab_monitor, text="Monitor")
        self.notebook.add(self.tab_procesos, text="Procesos")
        self.notebook.add(self.tab_optimizacion, text="Optimización")

        self.crear_tab_monitor()
        self.crear_tab_procesos()
        self.crear_tab_optimizacion()

    def crear_tab_monitor(self):
        panel_tarjetas = ttk.Frame(self.tab_monitor)
        panel_tarjetas.pack(fill="x", pady=(0, 10))

        self.lbl_ram_total = self.crear_tarjeta(panel_tarjetas, "RAM total", "0 GB")
        self.lbl_ram_usada = self.crear_tarjeta(panel_tarjetas, "RAM usada", "0 GB")
        self.lbl_ram_disponible = self.crear_tarjeta(panel_tarjetas, "RAM disponible", "0 GB")
        self.lbl_estado = self.crear_tarjeta(panel_tarjetas, "Estado", "Analizando")

        panel_barras = ttk.LabelFrame(self.tab_monitor, text="Uso actual de memoria")
        panel_barras.pack(fill="x", pady=10)

        ttk.Label(panel_barras, text="Uso de RAM").pack(anchor="w", padx=10, pady=(10, 3))
        self.barra_ram = ttk.Progressbar(panel_barras, maximum=100)
        self.barra_ram.pack(fill="x", padx=10, pady=4)
        self.lbl_ram_porcentaje = ttk.Label(panel_barras, text="0%")
        self.lbl_ram_porcentaje.pack(anchor="w", padx=10, pady=(0, 8))

        ttk.Label(panel_barras, text="Uso de memoria virtual / archivo de paginación").pack(anchor="w", padx=10, pady=(5, 3))
        self.barra_swap = ttk.Progressbar(panel_barras, maximum=100)
        self.barra_swap.pack(fill="x", padx=10, pady=4)
        self.lbl_swap_porcentaje = ttk.Label(panel_barras, text="0%")
        self.lbl_swap_porcentaje.pack(anchor="w", padx=10, pady=(0, 10))

        panel_texto = ttk.LabelFrame(self.tab_monitor, text="Diagnóstico automático")
        panel_texto.pack(fill="both", expand=True, pady=10)

        self.txt_diagnostico = tk.Text(
            panel_texto,
            wrap="word",
            font=("Segoe UI", 10)
        )
        self.txt_diagnostico.pack(fill="both", expand=True, padx=10, pady=10)
        self.txt_diagnostico.config(state="disabled")

    def crear_tab_procesos(self):
        panel_superior = ttk.Frame(self.tab_procesos)
        panel_superior.pack(fill="x", pady=(0, 10))

        ttk.Label(panel_superior, text="Buscar proceso:").pack(side="left", padx=(0, 8))

        self.busqueda = tk.StringVar()
        entrada_busqueda = ttk.Entry(panel_superior, textvariable=self.busqueda, width=35)
        entrada_busqueda.pack(side="left", padx=(0, 8))

        ttk.Button(
            panel_superior,
            text="Buscar",
            command=self.actualizar_procesos,
            width=14
        ).pack(side="left", padx=5)

        ttk.Button(
            panel_superior,
            text="Limpiar búsqueda",
            command=self.limpiar_busqueda,
            width=18
        ).pack(side="left", padx=5)

        panel_tabla = ttk.LabelFrame(self.tab_procesos, text="Procesos activos ordenados por consumo de memoria")
        panel_tabla.pack(fill="both", expand=True)

        columnas = ("pid", "nombre", "memoria", "porcentaje", "clasificacion", "accion")
        self.tabla_procesos = ttk.Treeview(panel_tabla, columns=columnas, show="headings")

        self.tabla_procesos.heading("pid", text="PID")
        self.tabla_procesos.heading("nombre", text="Proceso")
        self.tabla_procesos.heading("memoria", text="Memoria MB")
        self.tabla_procesos.heading("porcentaje", text="% RAM")
        self.tabla_procesos.heading("clasificacion", text="Clasificación")
        self.tabla_procesos.heading("accion", text="Recomendación")

        self.tabla_procesos.column("pid", width=80, anchor="center")
        self.tabla_procesos.column("nombre", width=230)
        self.tabla_procesos.column("memoria", width=120, anchor="center")
        self.tabla_procesos.column("porcentaje", width=100, anchor="center")
        self.tabla_procesos.column("clasificacion", width=170, anchor="center")
        self.tabla_procesos.column("accion", width=230)

        scrollbar = ttk.Scrollbar(panel_tabla, orient="vertical", command=self.tabla_procesos.yview)
        self.tabla_procesos.configure(yscrollcommand=scrollbar.set)

        self.tabla_procesos.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        nota = ttk.Label(
            self.tab_procesos,
            text="Nota: solo finaliza procesos que reconozcas, como navegadores, editores o aplicaciones abiertas por el usuario.",
            style="Subtitulo.TLabel"
        )
        nota.pack(anchor="w", pady=(8, 0))

    def crear_tab_optimizacion(self):
        panel = ttk.Frame(self.tab_optimizacion)
        panel.pack(fill="both", expand=True)

        panel_pasos = ttk.LabelFrame(panel, text="Flujo de optimización")
        panel_pasos.pack(fill="x", pady=(0, 10))

        texto_pasos = (
            "1. Presiona 'Medir antes' para guardar el estado inicial del sistema.\n"
            "2. Revisa la pestaña 'Procesos' e identifica aplicaciones con alto consumo de RAM.\n"
            "3. Finaliza únicamente procesos no esenciales que reconozcas.\n"
            "4. Presiona 'Medir después' para comparar si la RAM usada disminuyó."
        )

        ttk.Label(panel_pasos, text=texto_pasos, justify="left").pack(anchor="w", padx=10, pady=10)

        panel_mediciones = ttk.Frame(panel)
        panel_mediciones.pack(fill="x", pady=10)

        self.lbl_antes = self.crear_caja_medicion(panel_mediciones, "Medición antes")
        self.lbl_despues = self.crear_caja_medicion(panel_mediciones, "Medición después")
        self.lbl_resultado = self.crear_caja_medicion(panel_mediciones, "Resultado")

        panel_detalle = ttk.LabelFrame(panel, text="Interpretación de la optimización")
        panel_detalle.pack(fill="both", expand=True, pady=10)

        self.txt_optimizacion = tk.Text(
            panel_detalle,
            wrap="word",
            font=("Segoe UI", 10)
        )
        self.txt_optimizacion.pack(fill="both", expand=True, padx=10, pady=10)
        self.txt_optimizacion.config(state="disabled")

        self.actualizar_texto_optimizacion()

    def crear_tarjeta(self, padre, titulo, valor):
        marco = ttk.LabelFrame(padre, text=titulo)
        marco.pack(side="left", fill="x", expand=True, padx=5)

        etiqueta = ttk.Label(marco, text=valor, style="Dato.TLabel")
        etiqueta.pack(fill="x", padx=10, pady=18)

        return etiqueta

    def crear_caja_medicion(self, padre, titulo):
        marco = ttk.LabelFrame(padre, text=titulo)
        marco.pack(side="left", fill="both", expand=True, padx=5)

        etiqueta = ttk.Label(
            marco,
            text="Sin datos",
            justify="left",
            background="white",
            font=("Segoe UI", 10)
        )
        etiqueta.pack(fill="both", expand=True, padx=10, pady=10)

        return etiqueta

    def actualizar_manual(self):
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.actualizar_todo()

    def actualizar_todo(self):
        memoria = psutil.virtual_memory()
        swap = psutil.swap_memory()

        self.lbl_ram_total.config(text=f"{self.bytes_a_gb(memoria.total)} GB")
        self.lbl_ram_usada.config(text=f"{self.bytes_a_gb(memoria.used)} GB")
        self.lbl_ram_disponible.config(text=f"{self.bytes_a_gb(memoria.available)} GB")

        self.barra_ram["value"] = memoria.percent
        self.barra_swap["value"] = swap.percent

        self.lbl_ram_porcentaje.config(text=f"{memoria.percent}% de RAM utilizada")
        self.lbl_swap_porcentaje.config(text=f"{swap.percent}% de memoria virtual utilizada")

        estado = self.obtener_estado(memoria.percent, swap.percent)
        self.lbl_estado.config(text=estado)

        self.actualizar_diagnostico(memoria, swap, estado)
        self.actualizar_procesos()

        self.after_id = self.root.after(5000, self.actualizar_todo)

    def actualizar_procesos(self):
        if not hasattr(self, "tabla_procesos"):
            return

        for item in self.tabla_procesos.get_children():
            self.tabla_procesos.delete(item)

        memoria = psutil.virtual_memory()
        filtro = self.busqueda.get().strip().lower() if hasattr(self, "busqueda") else ""

        procesos = []

        for proceso in psutil.process_iter(["pid", "name", "memory_info"]):
            try:
                info = proceso.info
                nombre = info["name"] or "Desconocido"
                nombre_lower = nombre.lower()

                if filtro and filtro not in nombre_lower:
                    continue

                memoria_bytes = info["memory_info"].rss
                memoria_mb = self.bytes_a_mb(memoria_bytes)
                porcentaje = round((memoria_bytes / memoria.total) * 100, 2)

                clasificacion, accion = self.clasificar_proceso(nombre_lower, memoria_mb)

                procesos.append({
                    "pid": info["pid"],
                    "nombre": nombre,
                    "memoria": memoria_mb,
                    "porcentaje": porcentaje,
                    "clasificacion": clasificacion,
                    "accion": accion
                })

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        procesos.sort(key=lambda x: x["memoria"], reverse=True)

        for proceso in procesos[:60]:
            self.tabla_procesos.insert(
                "",
                "end",
                values=(
                    proceso["pid"],
                    proceso["nombre"],
                    proceso["memoria"],
                    f"{proceso['porcentaje']}%",
                    proceso["clasificacion"],
                    proceso["accion"]
                )
            )

    def clasificar_proceso(self, nombre_lower, memoria_mb):
        if nombre_lower in self.procesos_protegidos:
            return "Sistema protegido", "No finalizar"

        if memoria_mb >= 1000:
            return "Consumo muy alto", "Revisar y cerrar si no es necesario"

        if memoria_mb >= 500:
            return "Consumo alto", "Candidato a optimizar"

        if nombre_lower in self.aplicaciones_comunes:
            return "Aplicación de usuario", "Cerrar si no se está usando"

        if memoria_mb >= 200:
            return "Consumo medio", "Revisar"

        return "Consumo bajo", "Mantener"

    def limpiar_busqueda(self):
        self.busqueda.set("")
        self.actualizar_procesos()

    def finalizar_proceso_seleccionado(self):
        seleccion = self.tabla_procesos.selection()

        if not seleccion:
            messagebox.showwarning("Sin selección", "Selecciona un proceso de la tabla.")
            return

        valores = self.tabla_procesos.item(seleccion[0], "values")

        pid = int(valores[0])
        nombre = valores[1]
        clasificacion = valores[4]

        if clasificacion == "Sistema protegido":
            messagebox.showerror(
                "Proceso protegido",
                "Este proceso pertenece al sistema o es necesario para Windows. No se puede finalizar desde el programa."
            )
            return

        respuesta = messagebox.askyesno(
            "Confirmar finalización",
            f"¿Deseas finalizar este proceso?\n\n"
            f"Proceso: {nombre}\n"
            f"PID: {pid}\n\n"
            "Solo continúa si reconoces la aplicación."
        )

        if not respuesta:
            return

        try:
            proceso = psutil.Process(pid)
            proceso.terminate()

            try:
                proceso.wait(timeout=3)
            except psutil.TimeoutExpired:
                proceso.kill()

            messagebox.showinfo(
                "Proceso finalizado",
                f"El proceso {nombre} fue finalizado correctamente."
            )

            self.actualizar_manual()

        except psutil.NoSuchProcess:
            messagebox.showinfo("Proceso no encontrado", "El proceso ya no existe.")
            self.actualizar_manual()

        except psutil.AccessDenied:
            messagebox.showerror(
                "Acceso denegado",
                "No se tienen permisos para finalizar este proceso."
            )

        except Exception as error:
            messagebox.showerror(
                "Error",
                f"No se pudo finalizar el proceso.\n\nDetalle: {error}"
            )

    def tomar_medicion_antes(self):
        self.medicion_antes = self.obtener_medicion_actual()
        self.lbl_antes.config(text=self.formatear_medicion(self.medicion_antes))
        self.actualizar_texto_optimizacion()
        messagebox.showinfo("Medición guardada", "Se guardó la medición inicial del sistema.")

    def tomar_medicion_despues(self):
        self.medicion_despues = self.obtener_medicion_actual()
        self.lbl_despues.config(text=self.formatear_medicion(self.medicion_despues))
        self.actualizar_resultado_optimizacion()
        self.actualizar_texto_optimizacion()
        messagebox.showinfo("Medición guardada", "Se guardó la medición posterior a la optimización.")

    def obtener_medicion_actual(self):
        memoria = psutil.virtual_memory()
        swap = psutil.swap_memory()

        return {
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "ram_usada_gb": self.bytes_a_gb(memoria.used),
            "ram_disponible_gb": self.bytes_a_gb(memoria.available),
            "ram_porcentaje": memoria.percent,
            "swap_porcentaje": swap.percent,
            "procesos": len(psutil.pids())
        }

    def formatear_medicion(self, medicion):
        return (
            f"Fecha: {medicion['fecha']}\n"
            f"RAM usada: {medicion['ram_usada_gb']} GB\n"
            f"RAM disponible: {medicion['ram_disponible_gb']} GB\n"
            f"Uso de RAM: {medicion['ram_porcentaje']}%\n"
            f"Uso de memoria virtual: {medicion['swap_porcentaje']}%\n"
            f"Procesos activos: {medicion['procesos']}"
        )

    def actualizar_resultado_optimizacion(self):
        if not self.medicion_antes or not self.medicion_despues:
            self.lbl_resultado.config(text="Faltan mediciones")
            return

        diferencia_ram_gb = round(
            self.medicion_antes["ram_usada_gb"] - self.medicion_despues["ram_usada_gb"],
            2
        )

        diferencia_porcentaje = round(
            self.medicion_antes["ram_porcentaje"] - self.medicion_despues["ram_porcentaje"],
            2
        )

        diferencia_procesos = self.medicion_antes["procesos"] - self.medicion_despues["procesos"]

        if diferencia_ram_gb > 0:
            estado = "La optimización liberó memoria."
        elif diferencia_ram_gb == 0:
            estado = "No hubo cambio notable en la RAM."
        else:
            estado = "La RAM usada aumentó después de la medición."

        texto = (
            f"{estado}\n\n"
            f"RAM liberada: {diferencia_ram_gb} GB\n"
            f"Reducción de uso RAM: {diferencia_porcentaje}%\n"
            f"Diferencia de procesos: {diferencia_procesos}"
        )

        self.lbl_resultado.config(text=texto)

    def actualizar_texto_optimizacion(self):
        if not hasattr(self, "txt_optimizacion"):
            return

        texto = (
            "Este apartado mide el efecto real de la optimización.\n\n"
            "La idea no es generar un reporte académico, sino comprobar si al cerrar procesos no esenciales "
            "disminuye el uso de memoria RAM y se reduce la presión sobre la memoria virtual.\n\n"
            "Un sistema multitarea puede volverse lento cuando muchas aplicaciones permanecen abiertas al mismo tiempo. "
            "El programa ayuda a identificar esas aplicaciones y permite finalizar procesos seleccionados por el usuario.\n\n"
            "La optimización se considera positiva cuando después de cerrar procesos innecesarios baja el porcentaje de RAM usada, "
            "aumenta la RAM disponible o disminuye la cantidad de procesos activos."
        )

        self.txt_optimizacion.config(state="normal")
        self.txt_optimizacion.delete("1.0", tk.END)
        self.txt_optimizacion.insert(tk.END, texto)
        self.txt_optimizacion.config(state="disabled")

    def actualizar_diagnostico(self, memoria, swap, estado):
        texto = []

        texto.append("DIAGNÓSTICO DEL SISTEMA")
        texto.append("")
        texto.append(f"Estado actual: {estado}")
        texto.append(f"RAM usada: {memoria.percent}%")
        texto.append(f"Memoria virtual usada: {swap.percent}%")
        texto.append("")

        if memoria.percent < 60:
            texto.append("El sistema tiene suficiente memoria disponible para la carga actual.")
            texto.append("No se detecta presión alta sobre la RAM.")
        elif memoria.percent < 80:
            texto.append("El sistema tiene una carga media de memoria.")
            texto.append("Conviene revisar aplicaciones abiertas que no sean necesarias.")
        elif memoria.percent < 90:
            texto.append("El sistema tiene uso alto de RAM.")
            texto.append("Se recomienda cerrar aplicaciones pesadas que no estén en uso.")
        else:
            texto.append("El sistema está en estado crítico de memoria.")
            texto.append("Es probable que el sistema dependa más de memoria virtual y se vuelva lento.")

        texto.append("")

        if swap.percent > 30:
            texto.append("La memoria virtual tiene uso considerable.")
            texto.append("Esto puede afectar el rendimiento porque el almacenamiento es más lento que la RAM.")
        else:
            texto.append("La memoria virtual se mantiene baja.")
            texto.append("Esto indica que el sistema sigue trabajando principalmente con RAM.")

        texto.append("")
        texto.append("PROPÓSITO DEL PROGRAMA")
        texto.append("")
        texto.append(
            "El programa permite monitorear la memoria, identificar procesos con alto consumo "
            "y optimizar el sistema cerrando procesos no esenciales seleccionados por el usuario."
        )

        self.txt_diagnostico.config(state="normal")
        self.txt_diagnostico.delete("1.0", tk.END)
        self.txt_diagnostico.insert(tk.END, "\n".join(texto))
        self.txt_diagnostico.config(state="disabled")

    def obtener_estado(self, porcentaje_ram, porcentaje_swap):
        if porcentaje_ram < 60 and porcentaje_swap < 20:
            return "Óptimo"

        if porcentaje_ram < 80:
            return "Carga media"

        if porcentaje_ram < 90:
            return "Uso alto"

        return "Crítico"

    def bytes_a_gb(self, valor):
        return round(valor / (1024 ** 3), 2)

    def bytes_a_mb(self, valor):
        return round(valor / (1024 ** 2), 2)


if __name__ == "__main__":
    root = tk.Tk()
    app = OptimizadorMemoriaApp(root)
    root.mainloop()