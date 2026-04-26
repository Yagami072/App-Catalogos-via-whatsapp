import streamlit as st
import re
import unicodedata
from pathlib import Path
from datetime import datetime

# Configuración
UPLOAD_FOLDER = Path(__file__).parent / "uploads_streamlit"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


def nombre_seguro(nombre_original: str) -> str:
    """Normaliza el nombre para evitar caracteres problemáticos en rutas."""
    stem = Path(nombre_original).stem
    stem_ascii = unicodedata.normalize("NFKD", stem).encode("ascii", "ignore").decode("ascii")
    stem_ascii = re.sub(r"[^a-zA-Z0-9_-]+", "_", stem_ascii).strip("_")
    return stem_ascii or "archivo"


def construir_nombre_archivo(nombre_original: str) -> str:
    ext = Path(nombre_original).suffix.lower().lstrip(".")
    marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    base = nombre_seguro(nombre_original)
    return f"blancos_{marca_tiempo}_{base}.{ext}" if ext else f"blancos_{marca_tiempo}_{base}"


def listar_archivos() -> list[Path]:
    return sorted(
        [filepath for filepath in UPLOAD_FOLDER.glob("*") if filepath.is_file()],
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    )

# Configurar página
st.set_page_config(
    page_title="Servidor Multimedia Blancos Primavera",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos CSS
st.markdown("""
<style>
    .header { 
        background: linear-gradient(135deg, #ff5ecf 0%, #ff98e8 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    .metric-box {
        background: rgba(255, 94, 207, 0.1);
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ff5ecf;
    }
    .file-item {
        background: rgba(23, 9, 23, 0.5);
        padding: 12px;
        border-radius: 6px;
        margin: 5px 0;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header">
    <h1>📦 Servidor Multimedia Blancos Primavera</h1>
    <p>Plataforma para almacenar y servir archivos públicamente en Streamlit Cloud</p>
</div>
""", unsafe_allow_html=True)

feedback = st.session_state.pop("upload_feedback", None)
if feedback:
    ok = feedback.get("ok", 0)
    failed = feedback.get("failed", 0)
    if ok and not failed:
        st.success(f"✅ Se cargaron correctamente {ok} archivo(s).")
    elif ok and failed:
        st.warning(f"⚠️ Se cargaron {ok} archivo(s) y {failed} fallaron.")
    else:
        st.error("❌ No se pudo guardar ningún archivo. Revisa el detalle en la tab de carga.")

files = listar_archivos()

# Tabs
tab1, tab2, tab3 = st.tabs(["📤 Subir Archivos", "📋 Gestión de Archivos", "ℹ️ Información"])

with tab1:
    st.subheader("Cargar nuevos archivos")
    
    uploaded_files = st.file_uploader(
        "Selecciona uno o varios archivos:",
        type=["pdf", "png", "jpg", "jpeg", "gif", "mp4", "mov", "avi", "webp"],
        accept_multiple_files=True,
    )
    
    if uploaded_files:
        if st.button("✅ Subir archivos", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            results = []
            
            for idx, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Subiendo {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}...")
                
                try:
                    # Generar nombre de archivo robusto y único
                    filename = construir_nombre_archivo(uploaded_file.name)
                    
                    # Guardar archivo
                    filepath = UPLOAD_FOLDER / filename
                    file_bytes = uploaded_file.getvalue()
                    if not file_bytes:
                        raise ValueError("El archivo está vacío o no se pudo leer")

                    with open(filepath, "wb") as f:
                        f.write(file_bytes)
                    
                    results.append({
                        "filename": filename,
                        "original_name": uploaded_file.name,
                        "size": uploaded_file.size,
                        "timestamp": datetime.now().isoformat(),
                        "success": True,
                    })
                    
                except Exception as e:
                    results.append({
                        "filename": uploaded_file.name,
                        "error": str(e),
                        "success": False,
                    })
                
                progress_bar.progress((idx + 1) / len(uploaded_files))

            ok_results = [result for result in results if result["success"]]
            failed_results = [result for result in results if not result["success"]]

            if ok_results and not failed_results:
                status_text.success(f"✅ {len(ok_results)} archivo(s) subido(s)")
            elif ok_results and failed_results:
                status_text.warning(
                    f"⚠️ {len(ok_results)} subido(s), {len(failed_results)} con error"
                )
            else:
                status_text.error("❌ Ningún archivo se pudo subir")
            
            # Mostrar resumen
            st.markdown("### Resumen de carga:")
            for result in results:
                if result["success"]:
                    st.success(f"✅ {result['original_name']} → `{result['filename']}`")
                else:
                    st.error(f"❌ {result['filename']}: {result.get('error', 'Error desconocido')}")

            st.session_state["upload_feedback"] = {
                "ok": len(ok_results),
                "failed": len(failed_results),
            }

            # Fuerza recarga para que la tab de gestión refleje archivos recién subidos.
            if ok_results:
                st.rerun()

with tab2:
    st.subheader("Gestión de archivos")

    if st.button("🔄 Refrescar listado", use_container_width=False):
        st.rerun()
    
    if not files:
        st.info("📭 No hay archivos almacenados aún")
    else:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write("**Archivo**")
        with col2:
            st.write("**Tamaño**")
        with col3:
            st.write("**Acciones**")
        
        st.divider()
        
        for filepath in files:
            stat = filepath.stat()
            size_mb = stat.st_size / (1024 * 1024)
            
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.code(filepath.name, language="text")
            
            with col2:
                if size_mb > 1:
                    st.write(f"{size_mb:.2f} MB")
                else:
                    st.write(f"{stat.st_size / 1024:.1f} KB")
            
            with col3:
                # Botón para descargar
                with open(filepath, "rb") as f:
                    st.download_button(
                        "⬇️ Descargar",
                        f,
                        file_name=filepath.name,
                        key=f"download_{filepath.name}",
                        use_container_width=True,
                    )
        
        st.divider()
        
        # Estadísticas
        total_size = sum(f.stat().st_size for f in files)
        st.markdown(f"""
        ### 📊 Estadísticas
        - **Total archivos**: {len(files)}
        - **Espacio usado**: {total_size / (1024 * 1024):.2f} MB
        """)

with tab3:
    st.subheader("ℹ️ Información del Servidor")
    
    st.markdown("""
    ### 📌 Características
    - ✅ Almacenamiento ilimitado en Streamlit Cloud
    - ✅ Archivos servidos públicamente
    - ✅ URL directas para descargar
    - ✅ Soporte para: PDF, imágenes, videos
    - ✅ Integración con WhatsApp
    
    ### 🔗 Cómo usar desde la app React
    
    1. **URL del servidor**: `https://TU-USUARIO-streamlit-multimedia.streamlit.app`
    2. **Detección automática**: la app React NO lee automáticamente lo subido aquí
    3. **API para integración automática**: usa `app.py` (Flask) con `/upload`, `/list`, `/files`, `/health`
    4. **Este Streamlit** funciona como panel manual de carga/descarga
    
    ### 📤 Proceso
    1. Sube archivos aquí en Streamlit (manual)
    2. Revisa el listado en "Gestión de Archivos"
    3. Para flujo automático con React + WhatsApp, usa servidor Flask (`app.py`)
    
    ### 🚀 Deployment en Streamlit Cloud
    
    1. Sube este código a GitHub
    2. Ve a https://streamlit.io/cloud
    3. Conecta tu repositorio
    4. Deploy automático ✅
    
    ### 📁 Carpeta de almacenamiento
    """)
    
    st.code(str(UPLOAD_FOLDER))
    
    # Mostrar archivos actualmente almacenados
    if files:
        st.markdown("### 📦 Archivos actuales")
        for filepath in files[:10]:  # Mostrar los 10 últimos
            st.code(filepath.name)

# Footer
st.divider()
st.markdown("""
---
**Servidor Multimedia Blancos Primavera** | Desarrollado con Streamlit | 2026
""")
