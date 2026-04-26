# 📱 Pasos Visuales - Deploy Streamlit (Para principiantes)

## PASO 1️⃣: Descarga Git

1. Ve a: https://git-scm.com/download/win
2. Descarga e instala (botón azul)
3. Siguiente, siguiente, siguiente... ✅

---

## PASO 2️⃣: Abre PowerShell

1. Presiona: `Windows Key + X`
2. Selecciona: "Windows PowerShell" (azul)
3. Espera a que aparezca la terminal

```
PS C:\Users\[TuUsuario]>
```

---

## PASO 3️⃣: Clona el Repositorio

Escribe esto en PowerShell:

```powershell
git clone https://github.com/Yagami072/App-Catalogos-via-whatsapp.git
```

Presiona ENTER y espera. Verás algo como:

```
Cloning into 'App-Catalogos-via-whatsapp'...
remote: Enumerating objects: ...
```

---

## PASO 4️⃣: Entra a la Carpeta

Escribe:

```powershell
cd App-Catalogos-via-whatsapp
```

Verás:

```
PS C:\Users\Admin\App-Catalogos-via-whatsapp>
```

---

## PASO 5️⃣: Copia los Archivos

Opción Fácil (desde explorador):

1. Abre explorador
2. Ve a: `c:\Users\Admin\Documents\App pedidos\sistema-pedidos\servidor-multimedia`
3. Selecciona estos 3 elementos:
   - 📄 `streamlit_app.py`
   - 📄 `requirements.txt`
   - 📁 `.streamlit/`
4. Copia (Ctrl+C)
5. Ve a tu carpeta clonada (App-Catalogos-via-whatsapp)
6. Pega aquí (Ctrl+V)

---

## PASO 6️⃣: Sube a GitHub

En PowerShell, escribe (uno por uno):

```powershell
git add .
```

Presiona ENTER. Verás que regresa el cursor.

Luego escribe:

```powershell
git commit -m "Agregar servidor multimedia Streamlit"
```

Presiona ENTER.

Finalmente:

```powershell
git push origin main
```

Presiona ENTER.

**Nota:** Si pide contraseña, necesitarás un token de GitHub:
1. Ve a: https://github.com/settings/tokens
2. Haz clic en "Generate new token"
3. Elige "Personal access token (classic)"
4. Dale permisos: `repo`, `workflow`
5. Genera y copia el token
6. Úsalo como contraseña

---

## PASO 7️⃣: Deploy en Streamlit Cloud

1. **Abre tu navegador**
2. **Ve a**: https://streamlit.io/cloud
3. **Haz login** (con GitHub si puedes)
4. **Busca botón**: "New app" (color azul/verde)

### Formulario:

```
Repository:        Yagami072/App-Catalogos-via-whatsapp
Branch:            main
Main file path:    streamlit_app.py
```

5. **Haz clic**: "Deploy"
6. **¡Espera!** (2-3 minutos mientras compila)

Cuando termine, verás una URL como:

```
https://app-catalogos-yagami.streamlit.app
```

---

## PASO 8️⃣: Configura en React

1. **Abre navegador**: `http://localhost:5173`

2. **Mira la esquina inferior derecha** → Debería haber un botón ⚙️ gris/rosa

3. **Haz clic en ⚙️**

4. **Se abrirá panel de configuración**

5. **En el campo**, pega tu URL de Streamlit:

```
https://app-catalogos-yagami.streamlit.app
```

6. **Haz clic en "🔍 Verificar"** → Debería decir ✅

7. **Haz clic en "✅ Guardar"**

8. **Listo!** El panel se cerrará

---

## PASO 9️⃣: Prueba

### En la app (tab Gestión):

1. Sube un PDF pequeño
2. Debería subirse automáticamente a Streamlit
3. Se guardará localmente

### En la app (tab Envíos):

1. Selecciona el archivo que subiste
2. Ingresa tu número de WhatsApp
3. Haz clic en "Enviar por WhatsApp"
4. En 2 segundos debería llegar el PDF a tu WhatsApp

---

## ✅ Checklist de Éxito

- [ ] Git instalado
- [ ] Repositorio clonado
- [ ] Archivos copiados
- [ ] GitHub actualizado (`git push` completó)
- [ ] Streamlit desplegó (tu URL funciona)
- [ ] Panel ⚙️ configurado en React
- [ ] ✅ Servidor conectado (verificación pasó)
- [ ] PDF recibido en WhatsApp

---

## ❌ Si algo sale mal

### PowerShell dice "comando no reconocido"
```
→ Git no está instalado
→ Descarga e instala desde: https://git-scm.com/download/win
→ Reinicia PowerShell
```

### Git dice "authentication failed"
```
→ Necesitas Personal Access Token
→ Ve a: https://github.com/settings/tokens
→ Genera un token con permisos "repo"
→ Úsalo en lugar de tu contraseña
```

### Streamlit dice "Error: file not found"
```
→ Verificar que archivos estén en la raíz del repo
→ NO en una subcarpeta
→ Archivos deben estar en:
   ✅ App-Catalogos-via-whatsapp/streamlit_app.py
   ❌ App-Catalogos-via-whatsapp/server/streamlit_app.py
```

### React no ve el servidor
```
→ Recarga página: F5
→ Verifica que URL en panel sea exacta (sin "/" al final)
→ Abre https://[tu-url].streamlit.app en navegador
   → Debería ver la app Streamlit
→ Si no, espera 2 minutos a que termine de compilar
```

---

## 🎉 ¡Hecho!

Cuando completes estos 9 pasos tendrás un sistema completo:

🎨 **Interfaz bonita** en React
📱 **Servidor en la nube** en Streamlit
💬 **Envío de archivos** por WhatsApp
✅ **Todo funcionando juntos**

---

**Blancos Primavera Media** - Deploy Simplificado 🚀
