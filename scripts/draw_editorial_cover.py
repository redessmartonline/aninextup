"""Draw original editorial artwork from shapes, without external image assets."""

from hashlib import sha256
from math import cos, pi, sin
import random

from PIL import Image, ImageDraw


PALETTES = {
    "sun": ("#27122a", "#e26f57", "#f8c67d"),
    "moon": ("#111531", "#665add", "#a5d5ff"),
    "reef": ("#082832", "#14a69b", "#a6edd6"),
    "rose": ("#2a1530", "#cf4d87", "#ffb7cc"),
    "gold": ("#2a2026", "#ca832c", "#ffde9b"),
    "storm": ("#151e35", "#346cad", "#88daf3"),
    "ember": ("#30162b", "#cc4552", "#ffa77a"),
    "leaf": ("#132b31", "#478d67", "#d7ea97"),
}


def rgb(value):
    return tuple(bytes.fromhex(value[1:]))


def blend(a, b, ratio):
    return tuple(round(x + (y - x) * ratio) for x, y in zip(a, b))


def badge(draw, kind, x, y, size, ink, accent, dark):
    def pts(*points):
        return [(x + round(a * size), y + round(b * size)) for a, b in points]

    def box(a, b, c, d):
        return (*pts((a, b), (c, d))[0], *pts((a, b), (c, d))[1])

    def line(*points, color=ink, width=0.06):
        draw.line(pts(*points), fill=color, width=max(2, round(size * width)), joint="curve")

    def poly(*points, color=ink):
        draw.polygon(pts(*points), fill=color)

    def oval(a, b, c, d, color=ink):
        draw.ellipse(box(a, b, c, d), fill=color)

    if kind == "blade":
        poly((-.74,.65),(-.28,.18),(.5,-.75),(.74,-.76),(.68,-.48),(-.09,.34),(-.58,.8))
        poly((-.11,.22),(.5,-.75),(.74,-.76),(.04,.39),color=accent)
        line((-.45,-.02),(.25,.6),color=dark,width=.12)
        line((-.69,.71),(-.22,.25),color=accent,width=.11)
    elif kind == "book":
        poly((-.78,-.52),(-.18,-.43),(0,-.3),(.18,-.43),(.78,-.52),(.78,.48),(.16,.6),(0,.7),(-.16,.6),(-.78,.48))
        line((0,-.26),(0,.62),color=dark)
        for a in (-.18,.03,.24):
            line((-.62,a),(-.18,a+.08),color=accent)
            line((.18,a+.08),(.62,a),color=accent)
    elif kind == "planet":
        oval(-.55,-.55,.55,.55)
        oval(-.38,-.5,.49,.35,accent)
        draw.arc(box(-.9,-.28,.9,.37), 8, 350, fill=ink, width=max(2,int(size*.07)))
        oval(.63,-.63,.79,-.47,accent)
    elif kind == "ship":
        poly((0,-.85),(.38,-.26),(.78,.35),(.31,.21),(.22,.57),(-.22,.57),(-.31,.21),(-.78,.35),(-.38,-.26))
        poly((0,-.65),(.22,-.05),(0,.32),(-.22,-.05),color=accent)
        poly((-.14,.6),(.14,.6),(0,.93),color=accent)
    elif kind == "tower":
        poly((-.76,.66),(-.76,.09),(-.58,-.12),(-.43,.09),(-.43,-.16),(-.19,-.37),(-.19,-.56),(0,-.83),(.19,-.56),(.19,-.37),(.43,-.16),(.43,.09),(.58,-.12),(.76,.09),(.76,.66))
        for a,b in ((0,-.15),(-.52,.29),(.52,.29),(0,.37)):
            oval(a-.07,b-.1,a+.07,b+.1,dark)
    elif kind == "bottle":
        draw.rounded_rectangle(box(-.5,-.07,.5,.66),radius=int(size*.2),fill=ink)
        draw.rounded_rectangle(box(-.22,-.58,.22,.12),radius=int(size*.06),fill=ink)
        draw.rectangle(box(-.26,-.7,.26,-.5),fill=accent)
        oval(-.36,.18,.36,.53,accent)
        line((-.23,.17),(-.23,.39),color=dark)
    elif kind == "mask":
        poly((-.8,-.45),(-.36,-.66),(0,-.5),(.36,-.66),(.8,-.45),(.56,.26),(0,.68),(-.56,.26))
        poly((0,-.5),(.36,-.66),(.8,-.45),(.56,.26),(0,.68),color=accent)
        poly((-.55,-.19),(-.14,-.06),(-.33,.15),color=dark)
        poly((.55,-.19),(.14,-.06),(.33,.15),color=dark)
    elif kind == "music":
        line((-.23,.4),(-.23,-.59),(.54,-.73),(.54,.18),width=.1)
        line((-.23,-.37),(.54,-.51),color=accent,width=.13)
        oval(-.58,.26,-.18,.58)
        oval(.2,.05,.6,.37)
    elif kind == "flower":
        for n in range(6):
            angle=n*pi/3
            a,b=cos(angle)*.42,sin(angle)*.42
            oval(a-.28,b-.28,a+.28,b+.28,ink if n%2 else accent)
        oval(-.17,-.17,.17,.17,dark)
    elif kind == "calendar":
        draw.rounded_rectangle(box(-.68,-.56,.68,.64),radius=int(size*.09),fill=ink)
        draw.rectangle(box(-.68,-.27,.68,-.1),fill=accent)
        for a in (-.37,.37):line((a,-.71),(a,-.43),color=accent,width=.12)
        for a in (-.35,0,.35):
            for b in (.12,.42):oval(a-.07,b-.07,a+.07,b+.07,dark)
    elif kind == "ball":
        oval(-.62,-.62,.62,.62)
        for a,b,c,d in ((-.8,-.53,.13,.53),(-.13,-.53,.8,.53)):
            draw.arc(box(a,b,c,d),-130,130,fill=accent,width=max(2,int(size*.07)))
    elif kind == "field":
        poly((0,-.72),(.84,0),(0,.72),(-.84,0),color=accent)
        poly((0,-.49),(.59,0),(0,.49),(-.59,0),color=dark)
        for a,b in ((0,-.55),(.65,0),(0,.55),(-.65,0)):
            poly((a,b-.1),(a+.11,b),(a,b+.1),(a-.11,b))
    elif kind == "film":
        draw.rounded_rectangle(box(-.72,-.46,.72,.62),radius=int(size*.1),fill=ink)
        poly((-.74,-.55),(.65,-.81),(.73,-.56),(-.69,-.29),color=accent)
        poly((-.17,-.08),(.34,.13),(-.17,.39),color=dark)
    elif kind == "moon":
        oval(-.66,-.66,.66,.66)
        oval(-.19,-.75,.76,.27,dark)
        poly((.58,-.65),(.66,-.48),(.84,-.43),(.66,-.36),(.6,-.2),(.53,-.36),(.36,-.43),(.52,-.49),color=accent)
    elif kind == "lightning":
        poly((.17,-.85),(-.68,.12),(-.1,.12),(-.29,.85),(.69,-.22),(.12,-.22))
        poly((.17,-.85),(.12,-.22),(.69,-.22),(.53,-.06),(-.07,-.06),color=accent)
    elif kind == "mountain":
        poly((-.86,.62),(-.28,-.57),(.02,-.03),(.36,-.7),(.88,.62))
        poly((-.44,-.25),(-.28,-.57),(-.11,-.29),(-.23,-.33),(-.32,-.22),color=accent)
        poly((.18,-.37),(.36,-.7),(.55,-.22),(.39,-.31),(.29,-.23),color=accent)
    elif kind == "lantern":
        draw.rounded_rectangle(box(-.49,-.55,.49,.55),radius=int(size*.2),fill=ink)
        for a in (-.28,0,.28):line((a,-.42),(a,.42),color=accent)
        line((-.38,-.6),(.38,-.6),color=accent,width=.12)
        line((-.38,.61),(.38,.61),color=accent,width=.12)
        line((0,.62),(0,.82),color=accent)
    elif kind == "glove":
        draw.rounded_rectangle(box(-.56,-.52,.57,.29),radius=int(size*.26),fill=ink)
        draw.rounded_rectangle(box(-.56,-.02,-.18,.43),radius=int(size*.16),fill=accent)
        draw.rounded_rectangle(box(-.3,.2,.42,.68),radius=int(size*.07),fill=accent)
        line((-.23,.42),(.35,.42),color=dark)
    elif kind == "heart":
        oval(-.64,-.52,.08,.23)
        oval(-.08,-.52,.64,.23,accent)
        poly((-.62,-.02),(0,.68),(.62,-.02),(0,-.22))
        line((-.3,.02),(-.12,.17),(.14,-.14),color=accent)
    elif kind == "quill":
        poly((-.28,.53),(-.52,.16),(-.37,-.22),(-.06,-.49),(.65,-.74),(.57,-.19),(.22,.19))
        line((-.66,.77),(.47,-.53),color=accent)
        line((-.35,.39),(.05,.26),color=dark)
    elif kind == "crown":
        poly((-.75,-.36),(-.39,-.02),(0,-.69),(.39,-.02),(.75,-.36),(.56,.55),(-.56,.55))
        line((-.46,.31),(.46,.31),color=accent,width=.11)
        oval(-.1,-.09,.1,.12,accent)
    elif kind == "wave":
        for a,b in ((-.6,.15),(-.36,.07),(-.1,-.03)):
            draw.arc(box(a-.28,b-.64,a+1.1,b+.62),178,340,fill=ink,width=max(2,int(size*.12)))
        oval(.41,-.59,.65,-.35,accent)
    elif kind == "skull":
        oval(-.59,-.63,.59,.47)
        draw.rounded_rectangle(box(-.33,.09,.33,.66),radius=int(size*.08),fill=ink)
        oval(-.43,-.2,-.1,.12,dark)
        oval(.1,-.2,.43,.12,dark)
        for a in (-.16,0,.16):line((a,.4),(a,.63),color=accent)
    elif kind == "target":
        for i,r in enumerate((.69,.52,.35,.17)):
            oval(-r,-r,r,r,(ink,dark,accent,dark)[i])
        line((0,0),(.69,-.69),color=ink,width=.09)
        poly((.71,-.77),(.73,-.54),(.52,-.61))
    elif kind == "umbrella":
        draw.pieslice(box(-.73,-.65,.73,.72),180,360,fill=ink)
        line((0,-.02),(0,.58),(-.14,.69),(-.29,.57),color=accent,width=.09)
        line((-.65,.05),(.65,.05),color=accent)
    elif kind == "window":
        draw.rounded_rectangle(box(-.6,-.68,.6,.68),radius=int(size*.22),fill=ink)
        draw.rounded_rectangle(box(-.47,-.53,.47,.53),radius=int(size*.15),fill=dark)
        poly((-.43,.38),(-.15,-.08),(.06,.13),(.24,-.2),(.47,.38),color=accent)
        oval(.14,-.41,.33,-.22)
        line((0,-.52),(0,.52),color=ink)
    elif kind == "clapper":
        draw.rounded_rectangle(box(-.69,-.26,.69,.66),radius=int(size*.08),fill=ink)
        poly((-.73,-.51),(.63,-.76),(.69,-.51),(-.69,-.26),color=accent)
        for a in (-.45,-.08,.29):line((a,-.49),(a+.2,-.39),color=dark)
        line((-.47,.08),(.43,.08),color=accent)
        line((-.47,.28),(.24,.28),color=accent)
    elif kind == "key":
        oval(-.63,-.65,.15,.13)
        oval(-.46,-.48,-.02,-.04,dark)
        line((-.02,.03),(.59,.64),width=.17)
        line((.35,.43),(.58,.22),color=accent,width=.14)
        line((.52,.6),(.72,.42),color=accent,width=.14)
    elif kind == "flame":
        poly((-.55,.41),(-.6,.06),(-.35,-.25),(-.29,.02),(-.05,-.51),(.06,-.82),(.47,-.26),(.63,.08),(.5,.47),(.23,.69),(-.2,.69))
        poly((-.26,.44),(-.23,.17),(-.06,.28),(.08,-.22),(.37,.26),(.35,.52),(.12,.69),color=accent)
    elif kind == "house":
        poly((-.61,-.02),(0,-.63),(.61,-.02),(.61,.61),(-.61,.61))
        poly((-.8,-.02),(0,-.77),(.8,-.02),(.66,.09),(0,-.49),(-.66,.09),color=accent)
        draw.rectangle(box(-.13,.16,.14,.61),fill=dark)
        draw.rectangle(box(.27,.08,.46,.29),fill=accent)
    elif kind == "paw":
        oval(-.36,-.02,.36,.56)
        for a,b in ((-.55,-.19),(-.22,-.43),(.19,-.45),(.55,-.21)):
            oval(a-.15,b-.18,a+.15,b+.18,accent if a>0 else ink)
    elif kind == "hourglass":
        line((-.49,-.67),(.49,-.67),color=accent,width=.12)
        line((-.49,.67),(.49,.67),color=accent,width=.12)
        poly((-.4,-.59),(.4,-.59),(.14,-.15),(0,-.04),(.14,.14),(.4,.59),(-.4,.59),(-.14,.14),(0,-.04),(-.14,-.15))
        poly((0,.28),(.25,.58),(-.25,.58),color=accent)
    elif kind == "compass":
        oval(-.68,-.68,.68,.68,accent)
        oval(-.56,-.56,.56,.56,dark)
        poly((.37,-.46),(.11,.13),(-.38,.44),(-.1,-.11))
        poly((.37,-.46),(.11,.13),(-.1,-.11),color=accent)
    else:
        raise ValueError(f"Unknown cover motif: {kind}")


def draw_scene(slug, scene):
    family, main, detail = scene.split("/")
    dark, mid, light = map(rgb, PALETTES[family])
    rng = random.Random(sha256(slug.encode()).digest())
    image = Image.new("RGB", (1200, 630))
    # Paint the gradient at reduced resolution; all focal artwork stays sharp.
    lighting = Image.new("RGB", (300, 158))
    pixels = []
    for y in range(158):
        for x in range(300):
            distance = (((x - 243) / 150) ** 2 + ((y - 63) / 113) ** 2) ** .5
            glow = .69 * max(0, 1 - distance)
            pixels.append(blend(dark, mid, glow))
    lighting.putdata(pixels)
    image.paste(lighting.resize(image.size, Image.Resampling.BICUBIC))
    draw = ImageDraw.Draw(image)
    cx, cy = rng.randint(938, 976), rng.randint(286, 321)
    horizon = rng.randint(440, 510)
    for n in range(4):
        ridge = [(0, 630), (0, horizon + n * 42)]
        ridge += [(x, horizon + n * 42 + rng.randint(-40, 39)) for x in range(0, 1241, 65)]
        ridge += [(1240, 630)]
        draw.polygon(ridge, fill=blend(dark, mid, .22 - n * .045))
    for i in range(4):
        r = 160 + i * 15
        draw.ellipse((cx-r, cy-r, cx+r, cy+r), outline=blend(dark, light, .31-i*.05), width=2)
    draw.ellipse((cx-147, cy-147, cx+147, cy+147), fill=blend(dark, mid, .28), outline=mid, width=3)
    for i in range(80):
        x,y = rng.randint(700,1190),rng.randint(24,604)
        if (x-cx)**2+(y-cy)**2 < 155**2:
            continue
        d = rng.choice((1,1,2,2,3))
        draw.ellipse((x-d,y-d,x+d,y+d), fill=blend(dark, light, rng.uniform(.24,.72)))
    badge(draw, main, cx, cy, 125, light, mid, dark)
    dx, dy = cx + rng.randint(101,126), cy + rng.randint(123,150)
    draw.ellipse((dx-63,dy-63,dx+63,dy+63),fill=dark,outline=mid,width=3)
    badge(draw, detail, dx, dy, 49, light, mid, dark)
    return image
