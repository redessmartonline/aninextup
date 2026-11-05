#!/usr/bin/env python3
"""Build a curated, crawlable genre directory and install static navigation."""
import html
import json
import re
from pathlib import Path

from build_latest_news import extract, publication_timestamp
from editorial_dates import article_metadata
ROOT = Path(__file__).resolve().parents[1]
GENRES = [
 ('action','Action','Battles, high stakes and fast-moving stories.'),
 ('romance','Romance','Relationships, romantic comedy and emotional connections.'),
 ('fantasy','Fantasy','Magic, imagined worlds and extraordinary journeys.'),
 ('isekai','Isekai','Stories of reincarnation or travel to another world.'),
 ('comedy','Comedy','Comic misunderstandings, playful characters and absurd situations.'),
 ('sci-fi','Sci-Fi','Future societies, technology, space and giant robots.'),
 ('adventure','Adventure','Journeys, discoveries and new horizons.'),
 ('mystery','Mystery','Secrets, investigations and stories built around unanswered questions.'),
 ('horror','Horror','Unsettling mysteries, supernatural danger and darker themes.'),
 ('slice-of-life','Slice of Life','Everyday experiences, friendships and quieter character stories.')
]

def article_cover(source, slug):
    match = re.search(r'<meta\s+property="og:image"\s+content="([^"]+)"', source)
    if not match:
        raise ValueError(f'{slug}: missing article cover')
    image = html.unescape(match[1]).removeprefix('https://aninextup.com')
    if not image.startswith('/assets/') or not (ROOT / image.lstrip('/')).is_file():
        raise ValueError(f'{slug}: cover must be an existing local image')
    return f'<img src="{html.escape(image, quote=True)}" alt="" width="640" height="360" loading="lazy" decoding="async">'


def guide_card(url, title, summary, action, media):
    return (
        f'<a class="genre-guide genre-visual-card" href="{html.escape(url, quote=True)}">{media}'
        f'<div class="genre-card-copy"><h3>{html.escape(title)}</h3>'
        f'<p>{html.escape(summary)}</p><span>{html.escape(action)}</span></div></a>'
    )


def beginner_cards():
    one_piece = (ROOT / 'articles/where-to-watch-one-piece.html').read_text()
    watch_icon = '<div class="genre-card-art" aria-hidden="true"><svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3" stroke-linejoin="round"><rect x="7" y="13" width="50" height="38" rx="6"/><path d="M27 24l14 8-14 8z"/></svg></div>'
    calendar_icon = '<div class="genre-card-art" aria-hidden="true"><svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><rect x="10" y="14" width="44" height="41" rx="6"/><path d="M21 9v11m22-11v11M10 28h44M21 37h4m14 0h4m-22 9h4m14 0h4"/></svg></div>'
    return ''.join((
        guide_card('/articles/where-to-watch-one-piece', 'Understand the viewing options',
                   'See which platforms carry One Piece and what to check before starting a long-running series.',
                   'READ VIEWING GUIDE →', article_cover(one_piece, 'where-to-watch-one-piece')),
        guide_card('/where-to-watch', 'Check your streaming service',
                   'Browse streaming platforms and check which anime are available in your region.',
                   'WHERE TO WATCH →', watch_icon),
        guide_card('/calendar', 'Check the release calendar',
                   'See which anime are airing and when upcoming titles are scheduled to premiere.',
                   'OPEN CALENDAR →', calendar_icon),
    ))


def articles_by_genre():
    """Combine the editorial tags for older articles with explicit article metadata."""
    tags = json.loads((ROOT / 'editorial/genre-tags.json').read_text())
    grouped = {key: [] for key, _, _ in GENRES}
    aliases = {'science fiction': 'sci-fi', 'scifi': 'sci-fi'}
    for path in sorted((ROOT / 'articles').glob('*.html')):
        source = path.read_text(encoding='utf-8')
        labels = list(tags.get(path.stem, []))
        labels.extend(html.unescape(tag) for tag in re.findall(
            r'<meta\s+property="article:tag"\s+content="([^"]+)"', source, re.I
        ))
        for entry in article_metadata(source):
            genres = entry.get('genre', [])
            labels.extend(genres if isinstance(genres, list) else [genres])
        keys = set()
        for label in labels:
            if isinstance(label, str):
                label = label.strip().lower()
                keys.add(aliases.get(label, label.replace(' ', '-')))
        keys.intersection_update(grouped)
        if not keys:
            continue
        article = extract(path)
        if not article:
            continue
        article['original_timestamp'] = publication_timestamp(path)
        image = article['image'].removeprefix('https://aninextup.com')
        if not image.startswith('/assets/') or not (ROOT / image.lstrip('/')).is_file():
            image = '/assets/images/anime-image-fallback.svg'
        article['image'] = image
        for key in keys:
            grouped[key].append(article)
    for articles in grouped.values():
        articles.sort(key=lambda item: (item['published'], item['original_timestamp'], item['article']),
                      reverse=True)
    return grouped


def article_card(article):
    image = html.escape(article['image'], quote=True)
    media = f'<img src="{image}" alt="" width="640" height="360" loading="lazy" decoding="async">'
    return guide_card('/' + article['article'], article['title'], article['description'],
                      'READ GUIDE →', media)


def build():
    home = (ROOT/'index.html').read_text()
    cards=[]
    sections=[]
    grouped = articles_by_genre()
    for key, label, description in GENRES:
        links = [article_card(article) for article in grouped[key]]
        more = ('<button type="button" class="genre-load-more" hidden>Load more</button>'
                if len(links) > 9 else '')
        visibility = '' if key == 'action' else ' hidden'
        sections.append(
            f'<section class="genre-section"{visibility} id="{key}" aria-labelledby="genre-{key}">'
            f'<div class="section-head"><div><h2 id="genre-{key}">{label} Anime</h2>'
            f'<p>{description}</p></div><a href="#genre-index">ALL GENRES ↑</a></div>'
            '<div class="genre-guides">' + ''.join(links) + '</div>' + more + '</section>'
        )
        if len(cards)<6:
            cards.append(f'<a class="genre-tile" href="/genres#{key}"><h3>{label}</h3><p>{description}</p><span>EXPLORE →</span></a>')
    block='<section class="home-genres" aria-labelledby="home-genres-title"><div class="section-head"><div><span class="kicker">START HERE</span><h2 id="home-genres-title">Find Your Next Anime</h2><p>Explore anime by genre, then open a release or viewing guide.</p></div><a href="/genres">EXPLORE ALL GENRES →</a></div><div class="genre-tiles">'+''.join(cards)+'</div><a class="genre-beginner" href="/genres#beginners"><div><h3>New to anime?</h3><p>Find a starting point by story, mood and viewing order.</p></div><span>BEGINNER’S GUIDE →</span></a></section>'
    if '<section class="home-genres"' in home:
        home=re.sub(r'<section class="home-genres".*?</section>',lambda _:block,home,count=1,flags=re.S)
    else:
        home=home.replace('<section class="home-more-news"',block+'\n<section class="home-more-news"',1)
    (ROOT/'index.html').write_text(home)
    template=(ROOT/'where-to-watch.html').read_text()
    head=template.split('</head>')[0]+'</head>'
    title='Anime Genres: Action, Romance, Fantasy & More | AniNextUp'
    desc='Explore anime genres with AniNextUp: action, romance, isekai, fantasy, sci-fi and more. Find existing release guides, viewing information and a beginner starting point.'
    head=re.sub(r'<title>.*?</title>',f'<title>{html.escape(title)}</title>',head,flags=re.S)
    head=re.sub(r'<script[^>]*type="application/ld\+json"[^>]*>.*?</script>','',head,flags=re.S)
    head=re.sub(r'(<meta[^>]*(?:name|property)="(?:description|og:description|twitter:description)"[^>]*content=")[^"]*',lambda m:m[1]+html.escape(desc,quote=True),head)
    head=re.sub(r'(<meta[^>]*(?:property|name)="(?:og:title|twitter:title)"[^>]*content=")[^"]*',lambda m:m[1]+html.escape(title,quote=True),head)
    head=head.replace('https://aninextup.com/where-to-watch','https://aninextup.com/genres')
    header=re.search(r'<header class="site-header">.*?</header>',template,re.S)[0]
    header=re.sub(r' class="active"','',header)
    footer=re.search(r'<footer>.*?</footer>',template,re.S)[0]
    scripts=''.join(re.findall(r'<script[^>]+src="/assets/(?:mobile-menu|article-search)[^"]*"[^>]*></script>',template))
    anchors=''.join(f'<a href="#{key}">{label}</a>' for key,label,_ in GENRES)
    beginner='<section class="genre-section" id="beginners" hidden><span class="kicker">NEW TO ANIME?</span><h2>Choose Your First Anime Guide</h2><p>Start with the kind of story you already enjoy. Romance can focus on relationships; adventure follows a journey; slice of life explores everyday experiences. Genres overlap, so a title may appear in more than one section.</p><p>These links lead to release news and viewing guides, rather than a list of standalone first seasons. For a sequel or film, check the earlier entries before watching. A confirmed Japanese release date does not automatically mean streaming is available in your country.</p><div class="genre-guides">'+beginner_cards()+'</div></section>'
    schema={'@context':'https://schema.org','@type':'CollectionPage','name':'Anime Genres','url':'https://aninextup.com/genres','description':desc}
    page=head+'<body>'+header+'<main class="genres-page"><section class="genre-header"><span class="kicker">ANIME DISCOVERY</span><h1>Browse Anime by Genre</h1><p>Choose a genre. Explore release news and viewing guides.</p><nav class="genre-index" id="genre-index" aria-label="Browse anime genres">'+anchors+'</nav><div class="genre-starter-link"><span>New to anime? Find your starting point.</span><a href="#beginners">ANIME FOR BEGINNERS →</a></div></section>'+''.join(sections)+beginner+'</main>'+footer+scripts+'<script defer src="/assets/genres-ui.js?v=20261105b"></script><noscript><style>.genres-page .genre-section[hidden]{display:block!important}</style></noscript><script type="application/ld+json">'+json.dumps(schema)+'</script></body></html>'
    (ROOT/'genres.html').write_text(page)
    # Render navigation at build time, including articles created by the publishing pipeline.
    for path in [*ROOT.glob('*.html'),*(ROOT/'articles').glob('*.html')]:
        text=path.read_text()
        def nav(m):
            section=m[0]
            section=re.sub(r'<a[^>]*href="/genres"[^>]*>GENRES</a>','',section)
            active=' class="active" aria-current="page"' if path.name=='genres.html' else ''
            return re.sub(r'(<a\b[^>]*href="[^\"]*where-to-watch(?:\.html)?"[^>]*>.*?</a>)',lambda x:x[1]+f'<a{active} href="/genres">GENRES</a>',section,count=1,flags=re.S)
        text=re.sub(r'<header class="site-header">.*?</header>',nav,text,flags=re.S)
        if '<header class="site-header">' in text and '/assets/genres.css' not in text:
            text=text.replace('</head>','<link rel="stylesheet" href="/assets/genres.css?v=20261105f"></head>',1)
        text=re.sub(r'(/assets/genres\.css)(?:\?[^" ]*)?',r'\1?v=20261105f',text)
        if text!=path.read_text():path.write_text(text)
    print('Built Genres directory, homepage discovery and static site navigation.')

if __name__=='__main__':build()
