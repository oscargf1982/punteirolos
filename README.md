# Punteirolos 8.0 — Fantasy Stats 🏆

Web automática de estadísticas para la liga fantasy privada Punteirolos 8.0.

## 🚀 Configuración inicial (solo una vez)

### 1. Crear cuenta en GitHub
Ve a [github.com](https://github.com) y crea una cuenta gratuita si no tienes.

### 2. Crear repositorio
- Haz clic en **"New repository"**
- Nombre: `punteirolos` (o el que quieras)
- Visibilidad: **Public** (necesario para GitHub Pages gratis)
- Haz clic en **"Create repository"**

### 3. Subir los archivos
Sube todos estos archivos al repositorio:
```
punteirolos/
├── template.html      ← Plantilla de la web
├── generate.py        ← Script que genera los datos
├── splash.png         ← Imagen de celebración (la del campeón)
├── README.md          ← Este archivo
└── .github/
    └── workflows/
        └── update.yml ← Automatización semanal
```

**Opción fácil:** En GitHub, arrastra y suelta los archivos directamente.

### 4. Activar GitHub Pages
- Ve a tu repo → **Settings** → **Pages**
- En "Source", selecciona **"gh-pages"** branch
- Guarda

### 5. Activar permisos de Actions
- Ve a **Settings** → **Actions** → **General**
- En "Workflow permissions" → selecciona **"Read and write permissions"**
- Guarda

### 6. Primera ejecución
- Ve a la pestaña **Actions** de tu repo
- Haz clic en **"Actualizar estadísticas Punteirolos"**
- Haz clic en **"Run workflow"** → **"Run workflow"**
- Espera 3-5 minutos

### 7. Tu URL
```
https://TU_USUARIO.github.io/punteirolos/
```

---

## 🔄 Cómo funciona la automatización

Cada **lunes a las 10:00** (después del fin de semana de fútbol), GitHub ejecuta automáticamente:

1. Llama a la API de FPL y descarga todos los resultados
2. Descarga los picks de cada jornada (capitanes incluidos)
3. Regenera el `index.html` con los datos actualizados
4. Lo publica en GitHub Pages

**También puedes ejecutarlo manualmente** en cualquier momento desde la pestaña Actions → Run workflow.

---

## 🛠 Cambiar el día/hora de actualización

En `.github/workflows/update.yml`, edita la línea:
```yaml
- cron: '0 10 * * 1'
```

Formato: `minuto hora día_mes mes día_semana`
- `0 10 * * 1` = Lunes a las 10:00 UTC (11:00 España invierno, 12:00 verano)
- `0 9 * * 2` = Martes a las 9:00 UTC

---

## 📁 Archivos importantes

| Archivo | Para qué sirve |
|---------|----------------|
| `template.html` | La web. No lo edites a mano |
| `generate.py` | El script. Puedes cambiarlo |
| `splash.png` | La imagen de celebración al abrir la web |
| `update.yml` | Cuándo se actualiza automáticamente |
| `index.html` | Generado automáticamente, no lo subas |

---

## ❓ Problemas frecuentes

**La acción falla con error 403:**
La API de FPL a veces tiene restricciones temporales. Vuelve a ejecutarlo más tarde.

**No veo la web en la URL:**
Espera 2-3 minutos después de la primera ejecución. Si sigue sin aparecer, comprueba que GitHub Pages está configurado en la rama `gh-pages`.

**Quiero cambiar la imagen de celebración:**
Sube una nueva imagen con el nombre `splash.png` al repositorio.
