# Optimizador de Memoria Multitarea

Programa de escritorio desarrollado en Python para analizar el uso de memoria RAM en una computadora, identificar procesos con alto consumo y apoyar la optimización del sistema en un entorno multitarea.

## Descripción

Este proyecto permite observar cómo una computadora administra la memoria cuando se ejecutan varias aplicaciones al mismo tiempo. El programa muestra información en tiempo real sobre el uso de RAM, memoria virtual y procesos activos.

Además, permite medir el estado del sistema antes y después de cerrar procesos no esenciales, con el objetivo de comprobar si la optimización libera memoria y mejora el comportamiento del equipo.

## Objetivo del programa

El objetivo principal es ayudar al usuario a:

- Monitorear el uso actual de memoria RAM.
- Identificar procesos que consumen demasiada memoria.
- Clasificar procesos según su consumo.
- Evitar cerrar procesos protegidos del sistema.
- Finalizar procesos no esenciales seleccionados por el usuario.
- Comparar el estado del sistema antes y después de optimizar.

## Relación con Arquitectura de Computadoras

El programa se relaciona con varios conceptos de arquitectura de computadoras, principalmente:

- Memoria RAM.
- Memoria virtual.
- Archivo de paginación.
- Procesos.
- Sistema operativo.
- Administración de memoria.
- Multitarea.
- Rendimiento del sistema.

Cuando la RAM comienza a saturarse, el sistema operativo puede recurrir a la memoria virtual. Aunque esto permite que el sistema siga funcionando, también puede disminuir el rendimiento porque el almacenamiento secundario es más lento que la RAM.

## Funciones principales

### Monitor de memoria

La pestaña de monitor muestra:

- RAM total.
- RAM usada.
- RAM disponible.
- Estado general del sistema.
- Porcentaje de uso de RAM.
- Porcentaje de uso de memoria virtual.

### Procesos activos

La pestaña de procesos muestra una tabla con:

- PID del proceso.
- Nombre del proceso.
- Memoria utilizada en MB.
- Porcentaje aproximado de RAM.
- Clasificación del proceso.
- Recomendación de acción.

El programa clasifica los procesos como:

- Sistema protegido.
- Consumo muy alto.
- Consumo alto.
- Consumo medio.
- Consumo bajo.
- Aplicación de usuario.

### Optimización

La pestaña de optimización permite:

1. Medir el estado inicial del sistema.
2. Revisar procesos con alto consumo de memoria.
3. Finalizar procesos no esenciales.
4. Medir nuevamente el sistema.
5. Comparar si disminuyó el uso de RAM.

## Flujo de uso

1. Ejecutar el programa.
2. Presionar el botón **Medir antes**.
3. Entrar a la pestaña **Procesos**.
4. Seleccionar un proceso que el usuario reconozca.
5. Presionar **Finalizar proceso seleccionado**.
6. Entrar a la pestaña **Optimización**.
7. Presionar **Medir después**.
8. Revisar el resultado de la comparación.

## Advertencia

El programa permite finalizar procesos, por lo que se debe usar con cuidado.

No se recomienda cerrar procesos desconocidos o procesos del sistema operativo. El programa bloquea algunos procesos protegidos, pero el usuario debe asegurarse de cerrar únicamente aplicaciones que reconozca, como navegadores, editores de código, reproductores o programas abiertos manualmente.

Ejemplos de procesos que normalmente sí pueden cerrarse si no se están usando:

- chrome.exe
- brave.exe
- msedge.exe
- firefox.exe
- code.exe
- discord.exe
- spotify.exe
- steam.exe

Ejemplos de procesos que no se deben cerrar:

- system
- svchost.exe
- csrss.exe
- winlogon.exe
- services.exe
- lsass.exe
- dwm.exe
- explorer.exe

## Requisitos

- Windows 10 o Windows 11.
- Python 3.14 o superior.
- Librería `psutil`.

Tkinter no necesita instalarse por separado porque viene incluido con Python.

## Instalación

Primero se debe tener instalado Python.

Después, desde la terminal en la carpeta del proyecto, instalar las dependencias con:

```bash
pip install -r requirements.txt