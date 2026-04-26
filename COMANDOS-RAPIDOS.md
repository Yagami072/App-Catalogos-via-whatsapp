# ⚡ Comandos Rápidos - Deploy a Streamlit

## Opción 1: Desde PowerShell (Recomendado)

```powershell
# Paso 1: Navega a tu carpeta de proyectos
cd C:\ruta\donde\guardas\proyectos

# Paso 2: Clona el repo
git clone https://github.com/Yagami072/App-Catalogos-via-whatsapp.git
cd App-Catalogos-via-whatsapp

# Paso 3: Copia los archivos
Copy-Item "c:\Users\Admin\Documents\App pedidos\sistema-pedidos\servidor-multimedia\streamlit_app.py" -Destination "."
Copy-Item "c:\Users\Admin\Documents\App pedidos\sistema-pedidos\servidor-multimedia\requirements.txt" -Destination "."
Copy-Item "c:\Users\Admin\Documents\App pedidos\sistema-pedidos\servidor-multimedia\.streamlit" -Destination "." -Recurse

# Paso 4: Sube a GitHub
git add .
git commit -m "Agregar servidor multimedia Streamlit"
git push origin main

# ✅ Listo! Ve a https://streamlit.io/cloud
```

---

## Opción 2: Desde Git Bash o CMD

```bash
# Paso 1: Clona
git clone https://github.com/Yagami072/App-Catalogos-via-whatsapp.git
cd App-Catalogos-via-whatsapp

# Paso 2: Copia manualmente (desde explorador) estos archivos:
# - streamlit_app.py
# - requirements.txt
# - .streamlit/ (carpeta)

# Paso 3: Sube
git add .
git commit -m "Agregar servidor multimedia Streamlit"
git push origin main
```

---

## En Streamlit Cloud

```
1. Ve a: https://streamlit.io/cloud
2. Haz login
3. New app
4. Repository: Yagami072/App-Catalogos-via-whatsapp
5. Branch: main
6. File path: streamlit_app.py
7. Deploy
```

---

## En la App React (Después de deploy)

```
1. Abre: http://localhost:5173
2. Busca botón ⚙️ abajo a la derecha
3. Pega URL de Streamlit
4. Haz clic en Guardar
5. ¡Listo!
```

---

## URLs de Referencia

```
GitHub: https://github.com/Yagami072/App-Catalogos-via-whatsapp
Streamlit Cloud: https://streamlit.io/cloud
React App: http://localhost:5173
```
