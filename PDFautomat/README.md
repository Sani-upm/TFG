# 📩 Descarga Adjuntos Gmail - Automatización

Este script automatiza la descarga de archivos adjuntos (por ejemplo, tickets en PDF) desde correos electrónicos no leídos que cumplan un criterio específico (por defecto: enviados por “Sani Mitkov”) usando la API de Gmail.

---

## 🛠️ Requisitos

1. **Python 3.8 o superior**
2. **Instalación de dependencias (Conda recomendado):**

```bash
conda install -c conda-forge google-api-python-client google-auth google-auth-oauthlib
```

O alternativamente con pip:

```bash
pip install --upgrade google-api-python-client google-auth google-auth-oauthlib
```

3. **Credenciales de Gmail API:**
   - Crear un proyecto en [Google Cloud Console](https://console.cloud.google.com/)
   - Habilitar la API de Gmail
   - Descargar `credentials.json`
   - El primer uso generará `token.json` tras autenticarte

---

## ▶️ Uso

Ejecutar el script:

```bash
python pruebas-gmail.py
```

Este buscará correos no leídos del remitente `Sani Mitkov`, descargará los adjuntos y los marcará como leídos.

---

## 📁 Estructura de Logs

Todos los logs se guardan en:

```
./LOGGER_de_extraccion_de_correos/
```

### Se generan dos tipos de logs:
- `gmail_download_YYYY-MM-DD_HH-MM.log`: Log individual de cada ejecución
- `master_logger.log`: Log acumulativo con todo el historial

---

## 🧪 Ejemplo de salida

```
2025-05-18 16:42:10 - INFO - Script iniciado a las 2025-05-18 16:42:10
2025-05-18 16:42:12 - INFO - Archivo descargado: ticket1.pdf
2025-05-18 16:42:13 - INFO - Archivo descargado: ticket2.pdf
2025-05-18 16:42:14 - INFO - Total de archivos descargados: 2
2025-05-18 16:42:14 - INFO - Script finalizado a las 2025-05-18 16:42:14 (Duración total: 0:00:04)
```

---

## 📌 Notas

- El script crea automáticamente la carpeta de logs si no existe.
- El archivo `token.json` se regenera si es inválido.
- Los logs se almacenan de forma redundante en consola, archivo por ejecución y archivo maestro.

---
