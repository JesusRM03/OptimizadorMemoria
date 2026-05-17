# Optimizador de Memoria

Aplicación de escritorio para Windows hecha con Python y Tkinter. Permite monitorear el uso de RAM, revisar la memoria virtual, listar procesos activos y cerrar procesos no esenciales seleccionados por el usuario.

La aplicación está pensada como una herramienta práctica: ayuda a detectar aplicaciones con alto consumo de memoria y compara el estado del sistema antes y después de optimizar.

## Funciones principales

- Muestra RAM total, RAM usada, RAM disponible y estado general del sistema.
- Muestra el uso de memoria virtual / archivo de paginación.
- Lista procesos activos ordenados por memoria usada.
- Permite buscar procesos por nombre.
- Permite filtrar solo procesos de alto consumo.
- Clasifica procesos por consumo de memoria.
- Indica si un proceso parece seguro de cerrar o si está protegido.
- Bloquea procesos críticos de Windows y la propia aplicación.
- Pide confirmación antes de finalizar cualquier proceso.
- Actualiza la tabla y las mediciones después de cerrar un proceso.
- Compara estado inicial y final para mostrar RAM liberada, cambio porcentual y diferencia de procesos activos.
- Marca la optimización como positiva, neutral o negativa.

## Requisitos

- Windows 10 o Windows 11.
- Python 3.10 o superior.
- Dependencias incluidas en `requirements.txt`.

Tkinter viene incluido con la instalación normal de Python en Windows.

## Instalación

Desde la carpeta del proyecto, instala las dependencias:

```bash
pip install -r requirements.txt
```

## Ejecución

Ejecuta la aplicación con:

```bash
python main.py
```

## Uso recomendado

1. Abre la aplicación.
2. Pulsa **Guardar estado inicial**.
3. Entra en la pestaña **Procesos**.
4. Usa la búsqueda o el filtro de alto consumo para encontrar aplicaciones pesadas.
5. Selecciona solo procesos que reconozcas y que no estés usando.
6. Pulsa **Finalizar seleccionado** y confirma la acción.
7. Revisa la pestaña **Comparación** para ver el resultado.

## Advertencias

Finalizar procesos puede cerrar aplicaciones y causar pérdida de datos no guardados. Cierra únicamente procesos que reconozcas, como navegadores, editores, reproductores o aplicaciones abiertas manualmente.

La aplicación bloquea muchos procesos críticos de Windows, por ejemplo:

- `system`
- `smss.exe`
- `csrss.exe`
- `wininit.exe`
- `winlogon.exe`
- `services.exe`
- `lsass.exe`
- `svchost.exe`
- `dwm.exe`
- `explorer.exe`
- `msmpeng.exe`
- `trustedinstaller.exe`

Aunque exista esta protección, si no sabes qué hace un proceso, es mejor dejarlo activo.

## Notas del proyecto

El programa mantiene su propósito principal: observar el estado de memoria del sistema, identificar procesos con consumo elevado y permitir una optimización manual controlada. No genera archivos externos ni convierte el proyecto a `.exe`.
