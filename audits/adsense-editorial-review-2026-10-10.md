# AniNextUp — revisión editorial para AdSense (2026-10-10)

## Comprobación automática
- 76 páginas HTML revisadas; **0 errores técnicos** en el auditor de rutas, imágenes locales, metadatos y sitemap.
- 47 artículos marcados por **ausencia de enlaces externos de fuentes**. Esto es un indicador de revisión, **no una infracción de AdSense confirmada**.
- La validación de publicación GitHub Actions terminó correctamente: https://github.com/redessmartonline/aninextup/actions/runs/38093273264
- Auditoría: https://github.com/redessmartonline/aninextup/actions/runs/38093224916

## Inspección editorial manual de muestra
- `articles/blue-box-season-2.html`: afirmaciones sobre Netflix y calendario semanal, con tráiler integrado, pero sin enlace directo a un anuncio oficial. **Pendiente: verificar fechas/plataformas y citar fuente primaria**.
- `articles/ranma-season-3.html`: afirma destino Netflix y disponibilidad; vídeo integrado, pero sin referencia enlazada al anuncio de programación. **Pendiente: fuente oficial y comprobación regional**.
- `articles/apothecary-diaries-movie.html`: fecha japonesa, reparto y equipo de producción descritos sin enlaces a documentos oficiales. **Pendiente: fuentes primarias para cada dato relevante**.
- `articles/psyren-release-date.html`: dice que comprobó anuncios oficiales y contiene vídeo, pero no enlaza a esos anuncios. **Pendiente: enlaces y cotejo de fechas**.
- `articles/anime-releasing-november-2026.html`: calendario recopilatorio con enlaces a guías internas, sin referencias externas. **Pendiente: añadir fuentes verificadas para estrenos principales**.

## Acciones editoriales pendientes
1. Priorizar las 47 páginas señaladas por el auditor, empezando por las cinco anteriores y las páginas más visitadas.
2. Confirmar cada dato de estreno, región, distribuidor, reparto y estudio contra una fuente primaria; **no añadir enlaces de relleno ni fabricar corroboración**.
3. Añadir enlaces oficiales a los artículos cuando se haya comprobado su correspondencia. Corregir o retirar afirmaciones no verificadas.
4. Evaluar originalidad, derechos de imágenes y vídeos, utilidad para lectores y posibles duplicaciones; el auditor de HTML no puede demostrar estas cualidades.
5. Verificar `https://aninextup.com/ads.txt` y `https://aninextup.com/sitemap.xml` mediante peticiones HTTP públicas y comprobar que el ID de editor corresponda a la cuenta aprobable.
6. Revisar el estado de cuenta en Google AdSense. El rechazo de la cuenta no se puede resolver solo con cambios del repositorio.

**Estado:** no recomendar aún reenviar la solicitud. Esta revisión no equivale a aprobación de AdSense.
