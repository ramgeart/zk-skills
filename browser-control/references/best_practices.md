# Mejores Prácticas - Browser Control

## Flujo de Trabajo Recomendado

### 1. Planificar
- Identificar los pasos necesarios
- Preparar selectores robustos
- Considerar tiempos de carga

### 2. Implementar
```python
# Patrón: navegar -> esperar -> interactuar -> verificar

# Paso 1: Navegación
navigate(url)
wait_for_load()

# Paso 2: Verificar carga
screenshot()  # o get_elements()

# Paso 3: Interacción
click(selector)
wait_for_selector(result_selector)

# Paso 4: Extracción
get_text(result_selector)
screenshot()
```

### 3. Manejar Errores
- Siempre verificar existencia antes de interactuar
- Usar timeouts apropiados
- Capturar screenshots en fallos

## Patrones Comunes

### Login Automático
```bash
navigate "https://site.com/login"
wait_for_selector "input[name='username']"
fill -s "input[name='username']" -t "user@example.com"
fill -s "input[name='password']" -t "secretpass"
click -s "button[type='submit']"
wait_for_selector ".dashboard" --timeout 10000
screenshot
```

### Scrolling Infinito
```bash
navigate "https://site.com/infinite-scroll"
for i in {1..5}; do
    evaluate "window.scrollTo(0, document.body.scrollHeight)"
    wait_for_load
    sleep 2
done
screenshot --full-page
```

### Extraer Múltiples Items
```bash
navigate "https://site.com/products"
get_elements -s ".product-card"
# Procesar cada elemento
```

### Subir Archivo
```bash
navigate "https://site.com/upload"
fill -s "input[type='file']" -t "/ruta/al/archivo.pdf"
click -s "button#upload"
wait_for_selector ".success-message"
```

## Manejo de Esperas

### Esperas Implícitas vs Explícitas
```bash
# Implícita (automática con acciones)
click -s "button"  # espera hasta timeout por defecto

# Explícita (recomendada)
wait_for_selector -s "button" --timeout 10000
click -s "button"
```

### Estados de Carga
- `load` - DOM cargado
- `domcontentloaded` - DOM parseado
- `networkidle` - Sin requests de red (recomendado)

## Selectores Robustos

### Jerarquía de Preferencia
1. `data-testid` (mejor)
2. `id` único
3. Atributos ARIA
4. Texto visible estable
5. Clases semánticas
6. Estructura DOM (último recurso)

### Ejemplos
```css
/* ✅ Bien */
[data-testid="submit-button"]
[aria-label="Search"]
#user-profile-menu

/* ⚠️ Aceptable */
.btn-primary
.form-group input

/* ❌ Frágil */
div > div:nth-child(3) > button
.container > div > span
```

## Anti-patrones

### 1. Esperas Fijas
❌ Usar `sleep` arbitrario
✅ Usar `wait_for_selector` o `wait_for_load`

### 2. Selectores Posicionales
❌ `.list > div:nth-child(5)`
✅ `[data-testid="item-5"]`

### 3. Sin Manejo de Errores
❌ Ejecutar acciones sin verificar
✅ Verificar existencia antes de interactuar

### 4. Timeouts Cortos
❌ `--timeout 1000` para carga inicial
✅ `--timeout 10000` para carga inicial

## Optimización

### Headless vs Headed
```bash
# Desarrollo/debugging
--headless false

# Producción/automatización
--headless true
```

### Viewport
```bash
# Desktop
--width 1920 --height 1080

# Mobile
--width 375 --height 667

# Tablet
--width 768 --height 1024
```

### Reutilización de Sesión
```bash
# Guardar estado (cookies, localStorage)
# Reutilizar en sesiones posteriores
```

## Debugging

### Capturas de Pantalla
```bash
# Antes y después de cada acción crítica
screenshot
click -s "button"
screenshot
```

### Información de Página
```bash
# Verificar estado
evaluate "document.title"
evaluate "window.location.href"
get_html
```

### Logs del Navegador
```python
# En script personalizado
page.on("console", lambda msg: print(msg.text))
```

## Casos Especiales

### Frames/Iframes
```python
# Cambiar a frame
frame = page.frame_locator("iframe#content")
frame.locator("button").click()
```

### Shadow DOM
```python
# Acceder a shadow root
evaluate """() => {
    const host = document.querySelector('custom-element');
    const shadow = host.shadowRoot;
    return shadow.querySelector('button').click();
}"""
```

### Nuevas Ventanas/Popups
```python
# Manejar popup
with context.expect_page() as new_page_info:
    page.click("a[target='_blank']")
new_page = new_page_info.value
```

### Autenticación Básica
```python
# En navegación
page.goto("https://user:pass@site.com/protected")
```

## Seguridad

### Credenciales
- Nunca hardcodear contraseñas
- Usar variables de entorno
- Sanitizar inputs

### Headers Personalizados
```python
context.set_extra_http_headers({
    "X-Custom-Header": "value"
})
```

## Performance

### Paralelización
```python
# Múltiples navegadores en paralelo
# Usar asyncio para operaciones concurrentes
```

### Memoria
```bash
# Cerrar pestañas no usadas
close_tab

# Reiniciar navegador periódicamente
stop
start
```
