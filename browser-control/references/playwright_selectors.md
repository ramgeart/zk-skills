# Guía de Selectores de Playwright

## Selectores Básicos

### Por ID
```css
#username
#submit-button
```

### Por Clase
```css
.button
.container.main
```

### Por Etiqueta
```css
div
input[type="text"]
button[type="submit"]
```

### Por Atributo
```css
[name="email"]
[data-testid="login-btn"]
[placeholder="Search..."]
[href="/about"]
```

## Selectores Combinados

### Descendientes
```css
div.content p          /* p dentro de div.content */
nav a                  /* cualquier a dentro de nav */
```

### Descendiente Directo
```css
div > span             /* span hijo directo de div */
ul > li                /* li hijo directo de ul */
```

### Múltiples Clases
```css
.button.primary        /* elemento con ambas clases */
.card.featured         /* elemento con ambas clases */
```

## Selectores Avanzados

### Por Posición
```css
li:first-child
li:last-child
li:nth-child(3)
tr:nth-child(even)
```

### Por Estado
```css
input:checked
button:disabled
input:enabled
a:visited
```

### Por Contenido (Playwright específico)
```css
text=Submit            /* elemento con texto exacto */
text=Submit button     /* texto parcial */
has-text="Welcome"     /* contiene texto */
```

### Por Rol (Accesibilidad)
```css
role=button
role=navigation
role=textbox[name="Search"]
```

## Estrategias de Selección

### 1. Atributos de Test (Recomendado)
```html
<button data-testid="submit-btn">Submit</button>
```
```css
[data-testid="submit-btn"]
```

### 2. Atributos ARIA
```html
<button aria-label="Close dialog">X</button>
```
```css
[aria-label="Close dialog"]
```

### 3. Texto Visible
```css
text=Login
text=/Log\s+in/i       /* regex, case insensitive */
```

### 4. Jerarquía Específica
```css
form.login input[name="username"]
header nav ul li:first-child a
```

## Ejemplos Prácticos

### Formularios
```css
#login-form input[name="email"]
form input[type="password"]
button[type="submit"]
select[name="country"] option[value="us"]
```

### Tablas
```css
table.data tr:nth-child(2) td:nth-child(3)
table tbody tr:last-child
```

### Listas
```css
ul.menu li.active
.product-list .item:first-child
```

### Dropdowns
```css
.select-options li:has-text("Option 1")
[role="listbox"] [role="option"]:nth-child(2)
```

## Debugging de Selectores

1. Usar DevTools del navegador
2. Probar en consola: `document.querySelector("selector")`
3. Usar `get_elements` para ver coincidencias
4. Verificar visibilidad con `screenshot`

## Anti-patrones a Evitar

❌ Selectores frágiles:
```css
div > div:nth-child(3) > span
.container > div > div > a
```

✅ Selectores robustos:
```css
[data-testid="user-menu"]
[aria-label="User profile"]
#header .nav-link
```
