# 🚀 Guía de Deployment - Servidor Multimedia en Streamlit Cloud

## Paso 1: Clona tu repositorio localmente

```bash
git clone https://github.com/Yagami072/App-Catalogos-via-whatsapp.git
cd App-Catalogos-via-whatsapp
```

## Paso 2: Copia los archivos del servidor

Copia estos archivos a la raíz de tu repositorio:

```
App-Catalogos-via-whatsapp/
├── streamlit_app.py          (app Streamlit)
├── requirements.txt          (dependencias)
├── .streamlit/
│   └── config.toml          (configuración de tema)
└── README.md                (este archivo)
```

## Paso 3: Sube a GitHub

```bash
git add .
git commit -m "Agregar servidor multimedia con Streamlit"
git push origin main
```

## Paso 4: Deploy en Streamlit Cloud

1. **Accede a Streamlit Cloud**: https://streamlit.io/cloud

2. **Haz login** con tu cuenta de GitHub (crea una si no tienes)

3. **Haz clic en "New app"**

4. **Llena los datos**:
   - Repository: `Yagami072/App-Catalogos-via-whatsapp`
   - Branch: `main`
   - File path: `streamlit_app.py`

5. **Haz clic en "Deploy"**

6. **¡Listo!** Streamlit te dará una URL como:
   ```
   https://app-catalogos-via-whatsapp-yagami.streamlit.app
   ```

## Paso 5: Configura en la app React

En la app **Blancos Primavera Media** (React):

1. Abre el navegador en `http://localhost:5173`
2. Busca un campo de configuración para "Servidor multimedia"
3. Pega tu URL de Streamlit: `https://app-catalogos-via-whatsapp-yagami.streamlit.app`
4. Guarda

## Paso 6: ¡Prueba a enviar archivos!

1. Carga un PDF en la app React
2. Debería subirse a Streamlit Cloud
3. Streamlit devolverá una URL pública
4. La app la enviará a WhatsApp
5. ¡El cliente descargará el PDF! ✅

---

## 📊 Estructura del flujo

```
App React (localhost:5173)
    ↓
    [Usuario sube PDF]
    ↓
Streamlit Cloud (tu-url.streamlit.app)
    ↓
    [Archivo almacenado]
    ↓
    [URL pública generada]
    ↓
WhatsApp Cloud API
    ↓
    [PDF descargado por cliente]
    ✅ ÉXITO
```

---

## 🔧 Personalización

### Cambiar el tema de colores

Edita `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#ff5ecf"      # Rosa
backgroundColor = "#0b050b"   # Negro oscuro
secondaryBackgroundColor = "#170917"
textColor = "#ffe8fb"
font = "sans serif"
```

### Aumentar límite de upload

En `streamlit_app.py`, línea de configuración:

```python
[server]
maxUploadSize = 200  # en MB
```

---

## ⚠️ Notas importantes

- **Streamlit es gratuito** ✅
- **URLs permanentes** ✅
- **Almacenamiento persistente** ✅
- **Escalable automáticamente** ✅

---

## 🐛 Si algo no funciona

### "La app no aparece después de deploy"
- Espera 2-3 minutos, Streamlit está compilando
- Recarga la página

### "Los archivos no se suben"
- Verifica que la URL en React sea exacta (sin `/` al final)
- Comprueba la consola del navegador (F12)

### "Quiero cambiar la URL"
- Edita el nombre de tu app en Streamlit Cloud
- La URL se actualizará

---

## 📞 Soporte

Para más info sobre Streamlit Cloud: https://docs.streamlit.io/streamlit-cloud

---

**Listo para desplegar!** 🎉
