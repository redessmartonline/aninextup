# AniNextUp: revisión de indexación — 27 de octubre de 2026

## Resultado comprobado

- Se recuperaron las 41 URL exactas del informe privado de Search Console; corresponden a 31 artículos distintos.
- La inspección actual de Google confirma 23 artículos indexados y 8 aún sin indexar.
- Las 127 URL canónicas del sitemap responden HTTP 200 sin redirecciones, con canónica propia y sin noindex.
- Las 41 URL del informe responden HTTP 200 al seguir redirecciones.
- Los 113 artículos tienen rutas de enlaces HTML desde el inicio: 37 a un clic y 76 a dos clics.

## Error de redirección de PSYREN

La URL histórica es `https://aninextup.com/articles/psyren-release-date.html`. Actualmente devuelve una sola redirección 301 a la URL limpia, que responde HTTP 200. La prueba de Google en tiempo real confirma obtención correcta, rastreo e indexación permitidos. La URL canónica limpia ya está indexada. La prueba no convierte la URL antigua en una canónica nueva.

## Artículos aún pendientes

| Artículo | HTTP | Páginas HTML que enlazan al artículo | Estado de Google |
|---|---:|---:|---|
| [detective-is-already-dead-season-2](https://aninextup.com/articles/detective-is-already-dead-season-2) | 200 | 9 | Rastreada, actualmente sin indexar |
| [tank-chair-release-date](https://aninextup.com/articles/tank-chair-release-date) | 200 | 5 | Rastreada, actualmente sin indexar |
| [sss-class-revival-hunter-anime-january-2027](https://aninextup.com/articles/sss-class-revival-hunter-anime-january-2027) | 200 | 4 | Rastreada, actualmente sin indexar |
| [black-clover-season-2](https://aninextup.com/articles/black-clover-season-2) | 200 | 10 | Rastreada, actualmente sin indexar |
| [haru-to-gen-anime-january-4-2027](https://aninextup.com/articles/haru-to-gen-anime-january-4-2027) | 200 | 10 | Rastreada, actualmente sin indexar |
| [reincarnated-as-a-sword-season-2-english-dub-release-date](https://aninextup.com/articles/reincarnated-as-a-sword-season-2-english-dub-release-date) | 200 | 5 | Rastreada, actualmente sin indexar |
| [demons-crest-release-date](https://aninextup.com/articles/demons-crest-release-date) | 200 | 16 | Rastreada, actualmente sin indexar |
| [reborn-space-mercenary](https://aninextup.com/articles/reborn-space-mercenary) | 200 | 6 | Rastreada, actualmente sin indexar |

Las ocho páginas tienen canónica propia, presencia en sitemap y enlaces internos. No se encontró un bloqueo técnico de indexación en estas comprobaciones. Esto no establece por qué Google aún no las selecciona. El contenido se había actualizado recientemente en varios casos; se conserva el contenido y se evita solicitar repetidamente indexación sin nuevos cambios.

## Cambios concretos

Se añaden las cuatro reglas 301 explícitas que faltaban para las variantes `.html` de True Saint, Haru to Gen, Dengeki Daisy y Prisma Illya. Ya existían destinos limpios válidos; se uniforma el tipo de redirección permanente. No se atribuye a estas reglas el motivo de exclusión de las ocho páginas.

Los enlaces internos a páginas propias ya utilizan las URL canónicas; las referencias externas terminadas en `.html` se conservan.

## Evidencia y límites

El informe resumido indica actualización del 22 de octubre, pero algunos ejemplos e inspecciones tienen rastreos posteriores. Se diferencia esa fotografía histórica del resultado de inspección actual. Las 41 entradas incluyen 25 HTTPS limpias, 8 HTTPS con `.html` y 8 HTTP. Las variantes no son necesariamente artículos duplicados.

El detalle por URL, fecha mostrada y resultado se conserva en `indexation-review-2026-10-27.json`. La auditoría no promete indexación ni aprobación de AdSense.
