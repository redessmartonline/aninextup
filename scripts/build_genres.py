#!/usr/bin/env python3
"""Build a curated, crawlable genre directory and install static navigation."""
import html
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
GENRES = [
 ('action','Action','Battles, high stakes and fast-moving stories.',['sakamoto-days-season-2','black-clover-season-2','one-punch-man-season-3-part-2-january-2027']),
 ('romance','Romance','Relationships, romantic comedy and emotional connections.',['blue-box-season-2','my-happy-marriage-special-episodes','the-moon-on-a-rainy-night-anime']),
 ('fantasy','Fantasy','Magic, imagined worlds and extraordinary journeys.',['frieren-season-3-release-date','delicious-in-dungeon-season-2-release-date','witch-on-the-holy-night-movie']),
 ('isekai','Isekai','Stories of reincarnation or travel to another world.',['ascendance-of-a-bookworm-part-4','reincarnated-as-a-sword-season-2-english-dub-release-date','sasaki-and-peeps-season-2']),
 ('comedy','Comedy','Comic misunderstandings, playful characters and absurd situations.',['bocchi-the-rock-starry-footprints-movie','ranma-season-3','mashle-season-3-release-date']),
 ('sci-fi','Sci-Fi','Future societies, technology, space and giant robots.',['cyberpunk-edgerunners-2','mobile-suit-gundam-seed-freedom-zero-release-date','cosmoship-yamato-root-2199']),
 ('adventure','Adventure','Journeys, discoveries and new horizons.',['where-to-watch-one-piece','pokemon-horizons-season-4-wonders-ahead','made-in-abyss-awakening-mystery-release-date']),
 ('mystery','Mystery','Secrets, investigations and stories built around unanswered questions.',['apothecary-diaries-season-3','detective-is-already-dead-season-2','red-riding-hood-detective-story']),
 ('horror','Horror','Unsettling mysteries, supernatural danger and darker themes.',['horror-collector-release-date','le-college-noir-season-2-trailer-october-2026','in-a-world-full-of-zombies-january-2027']),
 ('slice-of-life','Slice of Life','Everyday experiences, friendships and quieter character stories.',['hirayasumi-anime-release-date','bocchi-the-rock-starry-footprints-movie','chitose-ramune-bottle-cour-2'])
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


def build():
    home = (ROOT/'index.html').read_text()
    cards=[]
    sections=[]
    for key,label,description,slugs in GENRES:
        links=[]
        for slug in slugs:
            source=(ROOT/'articles'/f'{slug}.html').read_text()
            match=re.search(r'<h1[^>]*>(.*?)</h1>',source,re.S)
            title=html.unescape(re.sub('<[^>]+>','',match[1])).strip()
            desc=re.search(r'<meta\s+name="description"\s+content="([^"]+)"',source)
            summary=html.unescape(desc[1]) if desc else 'Read our release and viewing guide.'
            links.append(guide_card(f'/articles/{slug}', title, summary, 'READ GUIDE →', article_cover(source, slug)))
        sections.append(f'<section class="genre-section"{' hidden' if key != 'action' else ''} id="{key}" aria-labelledby="genre-{key}"><div class="section-head"><div><h2 id="genre-{key}">{label} Anime</h2><p>{description}</p></div><a href="#genre-index">ALL GENRES ↑</a></div><div class="genre-guides">'+''.join(links)+'</div></section>')
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
    anchors=''.join(f'<a href="#{key}">{label}</a>' for key,label,_,_ in GENRES)
    beginner='<section class="genre-section" id="beginners" hidden><span class="kicker">NEW TO ANIME?</span><h2>Choose Your First Anime Guide</h2><p>Start with the kind of story you already enjoy. Romance can focus on relationships; adventure follows a journey; slice of life explores everyday experiences. Genres overlap, so a title may appear in more than one section.</p><p>These links lead to release news and viewing guides, rather than a list of standalone first seasons. For a sequel or film, check the earlier entries before watching. A confirmed Japanese release date does not automatically mean streaming is available in your country.</p><div class="genre-guides">'+beginner_cards()+'</div></section>'
    schema={'@context':'https://schema.org','@type':'CollectionPage','name':'Anime Genres','url':'https://aninextup.com/genres','description':desc}
    page=head+'<body>'+header+'<main class="genres-page"><section class="genre-header"><span class="kicker">ANIME DISCOVERY</span><h1>Browse Anime by Genre</h1><p>Choose a genre. Explore release news and viewing guides.</p><nav class="genre-index" id="genre-index" aria-label="Browse anime genres">'+anchors+'</nav><div class="genre-starter-link"><span>New to anime? Find your starting point.</span><a href="#beginners">ANIME FOR BEGINNERS →</a></div></section>'+''.join(sections)+beginner+'</main>'+footer+scripts+'<script defer src="/assets/genres-ui.js?v=20261105a"></script><noscript><style>.genres-page .genre-section[hidden]{display:block!important}</style></noscript><script type="application/ld+json">'+json.dumps(schema)+'</script></body></html>'
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
            text=text.replace('</head>','<link rel="stylesheet" href="/assets/genres.css?v=20261105e"></head>',1)
        text=re.sub(r'(/assets/genres\.css)(?:\?[^" ]*)?',r'\1?v=20261105e',text)
        if text!=path.read_text():path.write_text(text)
    print('Built Genres directory, homepage discovery and static site navigation.')

if __name__=='__main__':build()
