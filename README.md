# Servidor Multimedia - Blancos Primavera

Servidor multimedia para almacenar y servir archivos que se envían por WhatsApp desde la app Blancos Primavera Media.

## 🚀 Opción 1: Streamlit Cloud (RECOMENDADO)

### Ventajas
- ✅ Alojamiento gratuito
- ✅ URLs públicas permanentes
- ✅ Sin configuración de ngrok
- ✅ Almacenamiento persistente
- ✅ Escala automática

### Pasos de Deployment

1. **Fork o copia este repositorio a GitHub**
   - Sube la carpeta `servidor-multimedia` a tu repo

2. **Crea una cuenta en Streamlit Cloud**
   - Ve a https://streamlit.io/cloud
   - Conecta tu cuenta de GitHub

3. **Deploy la app**
   - Haz clic en "New app"
   - Selecciona tu repositorio
   - Branch: `main`
   - File path: `servidor-multimedia/streamlit_app.py`
   - Haz clic en "Deploy"

4. **Obtén tu URL pública**
   - Streamlit te dará una URL como:
   - `https://tu-usuario-multimedia.streamlit.app`

5. **Configura en la app React**
   - Abre la app Blancos Primavera Media
   - Ve a Configuración
   - Pega tu URL de Streamlit en "Servidor multimedia"
   - Guarda

6. **¡Listo!** 🎉
   - Los archivos se subirán directamente a Streamlit Cloud
   - Las URLs serán públicas y WhatsApp podrá descargarlas

---

## 🖥️ Opción 2: Servidor Local (Python/Flask)

Si prefieres mantener el servidor local, usa `iniciar.bat`:

```bash
double-click iniciar.bat
```

O en terminal:
```bash
python app.py
```

Disponible en `http://localhost:5000`

---

## 📝 Archivo Streamlit App

**Ubicación**: `streamlit_app.py`

**Features**:
- 📤 Upload de múltiples archivos
- 📋 Gestión y descarga de archivos
- 📊 Estadísticas de almacenamiento
- 🎨 Tema personalizado (rosa/negro)

---

## 🔧 Configuración de la URL del servidor

En la app React (Blancos Primavera Media):

1. Abre la app en el navegador
2. Mira en la sección superior si hay un campo de configuración
3. Ingresa la URL de Streamlit o `http://127.0.0.1:5000` si usas local

---

## 📊 Límites

### Streamlit Cloud
- Upload máximo: 200 MB por archivo
- Almacenamiento: Persistente entre deployments
- Ancho de banda: Ilimitado

### Servidor Local
- Upload máximo: 100 MB por archivo
- Almacenamiento: Carpeta `uploads/`

---

## 🔗 API Endpoints

### Streamlit
- No expone API directa, solo interfaz web
- Los archivos se descargan desde URLs públicas

### Local (Flask)
```
POST /upload              - Subir archivo
GET /files/<filename>     - Descargar archivo
GET /list                 - Listar archivos
GET /health               - Estado del servidor
```

---

## 🐛 Troubleshooting

### "Archivo no se carga en Streamlit"
- Espera a que el archivo aparezca en la tab "Gestión de Archivos"
- Streamlit puede tardar unos segundos

### "WhatsApp no descarga el archivo"
- Verifica que la URL sea pública (comienza con `https://`)
- Los archivos locales (`127.0.0.1`) NO funcionan con WhatsApp
- Usa Streamlit Cloud o ngrok para URLs públicas

### "El servidor no responde"
- Verifica que Streamlit Cloud esté activo
- O que `app.py` esté ejecutándose localmente

---

## 📧 Integración con WhatsApp

1. Usuario sube PDF en Blancos Primavera Media
2. App sube a Streamlit
3. Streamlit devuelve URL pública
4. App envía URL a WhatsApp
5. WhatsApp descarga directamente de Streamlit ✅

---

## 📜 Licencia

Uso interno - Blancos Primavera 2026

