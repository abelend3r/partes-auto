# partes-auto

Herramienta para automatizar el inicio de sesión en el portal de comunicación de hospedajes del Ministerio del Interior de España: [hospedajes.ses.mir.es](https://hospedajes.ses.mir.es/hospedajes-sede/#/comunicacion/inicio)

## Requisitos

- Python 3
- Google Chrome instalado
- `chromedriver.exe` compatible con tu versión de Chrome
- Librería Selenium para Python

## Instalación

1. Instala la dependencia de Python:

```bash
pip install selenium
```

2. Comprueba tu versión de Google Chrome en: **Menú de Chrome → Ayuda → Información de Google Chrome**

3. Descarga el `chromedriver.exe` compatible con tu versión desde:
   https://googlechromelabs.github.io/chrome-for-testing/

4. Extrae el `chromedriver.exe` y colócalo en el **mismo directorio** que el script `partes_auto_cli.py`.  
   Alternativamente, puedes añadirlo a la variable de entorno `PATH` de tu sistema.

## Uso

Abre una terminal (Command Prompt o PowerShell), navega al directorio del script y ejecuta:

```bash
python partes_auto_cli.py
```

El script te pedirá tu usuario y contraseña de forma interactiva (la contraseña no se muestra al escribirla) y realizará el inicio de sesión automáticamente.

## Errores comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `chromedriver.exe` no encontrado | No está en el directorio del script ni en el PATH | Coloca el archivo junto al script o añádelo al PATH |
| Versión de ChromeDriver incompatible | La versión de `chromedriver.exe` no coincide con Chrome | Descarga la versión correcta desde la URL indicada arriba |
| Chrome no encontrado | Chrome no está instalado en la ubicación predeterminada | Instala Chrome o configura `binary_location` en el script |
| Timeout de carga de página | Sin conexión o el portal no responde | Comprueba tu conexión a internet |
| Timeout esperando elementos | La página cambió su estructura | Los IDs de los campos del formulario pueden haber cambiado |
