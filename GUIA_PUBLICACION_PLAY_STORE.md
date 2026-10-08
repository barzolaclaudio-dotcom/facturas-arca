# 🚀 Guía Paso a Paso: Publicar tu App en Google Play Store

Esta guía contiene los **4 pasos exactos** para publicar tu primera aplicación en la tienda oficial **Google Play Store**.

---

## 📦 PASO 1: Generar el paquete Android (.aab) con PWABuilder (Gratis)

1. Abre el sitio web oficial: [pwabuilder.com](https://www.pwabuilder.com)
2. En la casilla central, pega la URL en vivo de tu App (ejemplo: `https://facturas-arca...streamlit.app`).
3. Haz clic en **Start** (Iniciar).
4. PWABuilder analizará tu aplicación y te mostrará un puntaje verde de compatibilidad.
5. Haz clic en el botón **Package for Stores** (Empaquetar para Tiendas).
6. Selecciona la tarjeta **Android** y haz clic en **Generate** (Generar).
7. Se descargará un archivo `.zip` en tu computadora. Descomprímelo: allí encontrarás el archivo **`app-release.aab`** (el archivo oficial requerido por Google).

---

## 💳 PASO 2: Crear tu cuenta de Desarrollador en Google Play Console

1. Ingresa a la página oficial: [play.google.com/console/signup](https://play.google.com/console/signup)
2. Inicia sesión con tu cuenta de Google (Gmail).
3. Selecciona tipo de cuenta: **Personal** o **Empresa**.
4. Realiza el pago único de **$25 USD** a Google con tarjeta de crédito o débito. *(Nota: Es un pago único de por vida que te permite publicar ilimitadas aplicaciones).*
5. Completa los datos de verificación de identidad de Google.

---

## 🎨 PASO 3: Crear la Ficha de la App en Google Play Console

Una vez dentro de tu panel de Google Play Console:

1. Haz clic en el botón **Crear aplicación** (Create app).
2. Completa los datos iniciales:
   - **Nombre de la app**: `Estampador de Logos ARCA`
   - **Idioma predeterminado**: `Español (América Latina)`
   - **Aplicación o juego**: `Aplicación`
   - **Gratis o de pago**: `Gratis`
3. En la sección **Ficha de la tienda principal** (Store listing):
   - **Descripción corta**: *"Estampa y personaliza logos en facturas PDF de ARCA/AFIP sin perder calidad ni código QR."*
   - **Descripción completa**: Explicación detallada de la galería de logos, procesamiento individual y en lote ZIP, y nitidez vectorial.
   - **Ícono de la app**: Sube el archivo `icon-512.png` de tu carpeta `static/`.
   - **Capturas de pantalla**: Sube 2 a 4 capturas de pantalla de la app en uso.
   - **Política de Privacidad**: Enlace simple a la política de privacidad.

---

## 🚀 PASO 4: Subir el archivo .aab y Lanzar la Aplicación

1. En el menú izquierdo de Google Play Console, ve a **Producción** (Production).
2. Haz clic en **Crear nueva versión** (Create new release).
3. Arrastra y sube el archivo **`app-release.aab`** que descargaste en el Paso 1.
4. Escribe un texto breve de notas de la versión (ej. *"Primera versión oficial de la aplicación"*).
5. Haz clic en **Guardar** ➔ **Revisar versión** ➔ **Iniciar lanzamiento a producción**.

---

### ⏳ ¿Qué ocurre después?
Google revisará tu aplicación (suele tardar entre 24 y 48 horas). Una vez aprobada, recibirás un correo de felicitación y **tu aplicación estará oficialmente disponible en el buscador de Google Play Store para que cualquier persona en el mundo la descargue**.
