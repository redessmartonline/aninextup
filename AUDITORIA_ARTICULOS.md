# Auditoría editorial y SEO — AniNextUp

Última revisión: 2026-10-09. Rama: `main`. Objetivo solicitado: 59 artículos. Estado: **en curso; 0/59 con auditoría integral completada**.

## Criterio de cierre
Cada artículo solo se marca **completo** tras verificar: portada y URL de imagen; fechas/plataformas contra fuentes oficiales; tráiler oficial y `VideoObject` cuando exista video verificable; title/description/canonical/Open Graph/JSON-LD; enlaces internos; inclusión en sitemap; y, cuando estén accesibles, datos de Search Console y despliegue de GitHub Actions. No inventar información ni cambiar URLs, diseño o AniNextUp Auto Publisher.

## Revisiones parciales (NO cuentan como completas)
- `articles/sasaki-and-peeps-season-2-anime-shares-creditless-opening-and-end-a03f04c7.html` — revisado HTML en `main` (blob `3c9404646877a4ed1998ffb69bad613081ae1320`). Presenta canonical, descripción, Open Graph con imagen, NewsArticle, BreadcrumbList y enlaces internos; no tiene `VideoObject`. Falta validar disponibilidad real de portada, videos y afirmaciones con fuentes oficiales, GSC y despliegue.
- `articles/pok-mon-horizons-anime-unseals-treasures-of-ruin-in-latest-wonder-a6b9d2d5.html` — revisado HTML en `main` (blob `aca9a755862ac2ab05af4a0b5cc2eedc47489eee`). Canonical, descripción, NewsArticle y BreadcrumbList presentes; **no hay portada ni og:image**, y el índice usa `assets/favicon.svg` como imagen. La fuente oficial Pokémon confirma el inicio del arco Wonder Voyage el 2026-05-22; aún falta validar imagen oficial para corregir sin inventar, tráiler exacto y demás controles.
- `articles/live-action-firefly-wedding-tv-drama-announced-for-2027-a1ac1e86.html` — revisado HTML en `main` (blob `bf0c4d8911cf626668f8f2be0c2cea869cd975b9`). Canonical, descripción, og:image, NewsArticle, BreadcrumbList y enlaces internos presentes; la imagen está descrita explícitamente como arte de la serie y no póster del drama. Falta verificación externa integral.

## Verificaciones generales parciales
- `assets/data.js` (blob `ce9101a0a245ab46386ef624924e78b2a4961a6b`): índice de publicaciones y guías; mantener su formato y automatización.
- `sitemap.xml` (blob `39797b2c6b045571f57034d0505fae83b39d25f0`): incluye las tres URLs anteriores.
- `robots.txt` (blob `e18eb758d9b699d2eacf52aa8da8f28e784cae67`): declara `Sitemap: https://aninextup.com/sitemap.xml`.
- Search Console y GitHub Actions: todavía no verificados en esta ejecución.
- No se han aplicado correcciones editoriales sin evidencia suficiente.

## Pendientes
1. Reconciliar el inventario exacto de 59 artículos con `sitemap.xml`, `assets/data.js` y archivos HTML del repositorio; registrar cada ruta individual.
2. Completar la verificación integral de los tres artículos anteriores.
3. Auditar uno por uno los restantes artículos del inventario reconciliado (hasta completar 59/59).
4. Corregir solo fallos confirmados; antes de cada actualización leer SHA actual, después comprobar commit y releer archivo.
5. Comprobar Google Search Console si está disponible, resultados de GitHub Actions y despliegue público.

**No interpretar revisiones parciales como artículos completados.**
