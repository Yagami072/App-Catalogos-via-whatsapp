# 📦 Servidor Multimedia Blancos Primavera
## Gestión de archivos para WhatsApp

🔗 **Tu Repositorio**: https://github.com/Yagami072/App-Catalogos-via-whatsapp

---

## ⚡ Quick Start (3 pasos)

### Paso 1️⃣: Prepara los archivos

Desde tu PC, abre terminal en:
```
c:\Users\Admin\Documents\App pedidos\sistema-pedidos\servidor-multimedia
```

Copia estos 3 archivos:
- `streamlit_app.py` ← **Principal**
- `requirements.txt`
- `.streamlit/config.toml`

### Paso 2️⃣: Sube a GitHub

```bash
git add streamlit_app.py requirements.txt .streamlit/
git commit -m "Agregar servidor multimedia Streamlit"
git push origin main
```

### Paso 3️⃣: Deploy en Streamlit Cloud

1. Ve a https://streamlit.io/cloud
2. Haz login con GitHub
3. Clic en "New app"
4. Selecciona tu repo: `Yagami072/App-Catalogos-via-whatsapp`
5. File path: `streamlit_app.py`
6. Clic en "Deploy"

**¡Listo! Tu URL pública será:**
```
https://app-catalogos-via-whatsapp-XXX.streamlit.app
```

---

## 🔌 Integración con la app React

En `Blancos Primavera Media`:

1. Abre en navegador: `http://localhost:5173`
2. Busca campo "Servidor multimedia"
3. Pega: `https://app-catalogos-via-whatsapp-XXX.streamlit.app`
4. Guarda

---

## ✅ Flujo Completo

```
┌─────────────────────┐
│  App React          │ ← http://localhost:5173
│ (Blancos Primavera) │
└──────────┬──────────┘
           │
           │ Usuario sube PDF
           ↓
┌─────────────────────────┐
│ Streamlit Cloud         │ ← https://...streamlit.app
│ (Servidor Multimedia)   │
└──────────┬──────────────┘
           │
           │ URL pública del PDF
           ↓
┌─────────────────────┐
│ WhatsApp API        │
│ (Meta Cloud)        │
└──────────┬──────────┘
           │
           │ Envía URL al cliente
           ↓
┌─────────────────────┐
│ WhatsApp Desktop    │ ✅ PDF descargado
│ (Cliente)           │
└─────────────────────┘
```

---

## 📋 Archivos Incluidos

| Archivo | Función |
|---------|---------|
| `streamlit_app.py` | Aplicación Streamlit principal |
| `requirements.txt` | Dependencias Python |
| `.streamlit/config.toml` | Tema y configuración |
| `app.py` | Servidor Flask alternativo (opcional) |
| `iniciar.bat` | Script para correr localmente (opcional) |
| `DEPLOYMENT-STREAMLIT.md` | Guía detallada de deployment |

---

## 🎨 Características

✅ Subida de múltiples archivos
✅ Tema rosa/negro (Blancos Primavera)
✅ Almacenamiento persistente en Streamlit
✅ URLs públicas para WhatsApp
✅ Gestión de archivos
✅ Estadísticas de almacenamiento

---

## 🔐 Seguridad & Límites

- Upload máximo: **200 MB por archivo**
- Almacenamiento: **Persistente** entre deployments
- Ancho de banda: **Ilimitado en Streamlit Cloud**
- Acceso: **Público** (URLs directas)

---

## 📞 Problemas Comunes

### "No logro conectar la app React"
```
Verifica que la URL sea exacta:
❌ https://app-catalogos-via-whatsapp-XXX.streamlit.app/
✅ https://app-catalogos-via-whatsapp-XXX.streamlit.app
```

### "El servidor local no funciona"
```bash
# Verifica que esté ejecutándose
curl http://127.0.0.1:5000/health
```

### "WhatsApp no descarga el archivo"
```
Usa SOLO URLs públicas (https://)
Las URLs locales (127.0.0.1) NO funcionan
```

---

## 📚 Documentación Adicional

- [Streamlit Docs](https://docs.streamlit.io)
- [Streamlit Cloud](https://streamlit.io/cloud)
- [GitHub Repo](https://github.com/Yagami072/App-Catalogos-via-whatsapp)

---

## 🚀 ¿Listo para empezar?

1. ✅ Tengo los archivos preparados
2. ✅ Voy a subirlos a GitHub
3. ✅ Haré el deploy en Streamlit Cloud
4. ✅ Configuro la URL en la app React
5. ✅ ¡Pruebo a enviar archivos por WhatsApp!

---

**Blancos Primavera Media** | Servidor Multimedia | 2026
