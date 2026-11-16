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


def paint_backdrop(draw, rng, setting, dark, mid, light):
    ground = blend(dark, mid, .28)
    far = blend(dark, mid, .54)
    rim = blend(mid, light, .42)
    if setting == "school":
        draw.polygon([(625, 630), (805, 65), (1200, 5), (1200, 630)], fill=ground)
        for x in (798, 913, 1040, 1160):
            draw.polygon([(x, 105), (x+94, 88), (x+94, 349), (x-12, 381)], fill=far, outline=rim, width=3)
            draw.line((x+40, 94, x+34, 366), fill=rim, width=4)
            draw.line((x-6, 242, x+94, 224), fill=rim, width=4)
        draw.polygon([(600, 630), (804, 444), (1200, 390), (1200, 630)], fill=blend(dark, mid, .17))
        for x in range(630, 1250, 94):
            draw.line((x, 630, 866+(x-630)//3, 438), fill=ground, width=3)
        return
    if setting == "sports":
        draw.polygon([(590, 630), (760, 400), (1200, 362), (1200, 630)], fill=ground)
        for y in range(324, 402, 14):
            draw.line((704, y+24, 1200, y), fill=far, width=4)
        draw.line((606, 625, 1022, 431, 1200, 463), fill=rim, width=4)
        for x in (775, 1148):
            draw.line((x, 133, x, 365), fill=far, width=6)
            for k in range(3):
                draw.rounded_rectangle((x-24+k*16, 131, x-11+k*16, 151), 3, fill=rim)
        return
    if setting == "stage":
        draw.polygon([(676, 0), (970, 0), (1120, 552), (696, 552)], fill=far)
        draw.polygon([(1030, 0), (1160, 0), (1200, 480), (884, 480)], fill=blend(mid, light, .19))
        for x in range(730, 1210, 35):
            draw.line((x, 0, x-22, 310), fill=ground, width=4)
        for _ in range(54):
            x, y = rng.randrange(685, 1200), rng.randrange(410, 635)
            draw.ellipse((x, y, x+7, y+18), fill=rim if rng.random() < .35 else far)
        return
    if setting == "city":
        for x in range(650, 1200, 49):
            roof = rng.randrange(110, 404)
            draw.rectangle((x, roof, x+43, 584), fill=ground, outline=far, width=2)
            for y in range(roof+14, 470, 23):
                if rng.random() < .66:
                    draw.rectangle((x+9, y, x+28, y+4), fill=rim)
        draw.polygon([(620, 630), (857, 513), (1172, 513), (1200, 630)], fill=dark)
        for k in range(6):
            y = 540+k*17
            draw.line((830-k*21, y, 1124+k*13, y), fill=far, width=2)
        return
    draw.ellipse((918, 56, 1101, 239), fill=far, outline=rim, width=3)
    for layer in range(3):
        ridge = [(570, 630), (570, 424+layer*34)]
        ridge.extend((x, rng.randrange(365, 470)+layer*34) for x in range(600, 1250, 48))
        ridge.append((1250, 630))
        draw.polygon(ridge, fill=blend(dark, mid, .44-layer*.10))
    for x in (752, 1080, 1163):
        height = rng.randrange(68, 151)
        if setting == "coast":
            draw.line((x-36, 505, x+44, 498), fill=rim, width=3)
            draw.polygon([(x, 482-height), (x+24, 488), (x, 483)], fill=far)
            draw.line((x, 478-height, x, 511), fill=rim, width=2)
        else:
            draw.polygon([(x-21, 490), (x-17, 490-height), (x+4, 466-height),
                          (x+27, 490-height), (x+28, 490)], fill=ground, outline=far, width=2)


def paint_character(draw, x, y, scale, rng, outfit, palette, mirror=False):
    dark, mid, light = palette
    outline = (25, 21, 39)
    skin, shade = rng.choice([((244, 197, 164), (193, 126, 126)),
                              ((230, 177, 145), (178, 111, 100)),
                              ((187, 130, 108), (126, 77, 82))])
    hair = rng.choice([(49, 31, 48), (72, 48, 43), (39, 49, 73), (96, 49, 55),
                       blend(dark, mid, .57), blend(dark, light, .63)])
    hair_shine = blend(hair, light, .44)
    coat = blend(dark, mid, .54)
    coat_light = blend(coat, light, .26)
    side = -1 if mirror else 1

    def point(a, b):
        return round(x+a*scale*side), round(y+b*scale)

    def poly(points, color, edge=outline, width=2):
        draw.polygon([point(a,b) for a,b in points], fill=color, outline=edge,
                     width=max(1, round(width*scale)))

    def line(points, color=outline, width=2):
        draw.line([point(a,b) for a,b in points], fill=color, width=max(1, round(width*scale)), joint="curve")

    def oval(a, b, c, d, color):
        l,t = point(a,b)
        r,u = point(c,d)
        draw.ellipse((min(l,r),t,max(l,r),u),fill=color)

    long_hair = rng.random() < .56
    hair_end = rng.randrange(103, 165) if long_hair else rng.randrange(27, 53)
    poly([(-60, -59), (-52,-92), (-20,-114), (20,-111), (52,-93), (63,-62),
          (67,-16), (74,hair_end), (43,hair_end-19), (18,63), (-40,63),
          (-70,hair_end-13), (-58,4)], hair, width=3)
    poly([(-78,108), (-53,91), (-24,79), (16,76), (56,86), (79,103), (105,144),
          (128,260), (88,295), (-91,278), (-126,257), (-112,172)], coat, width=3)
    poly([(-78,111), (-61,131), (-82,221), (-111,248), (-103,168)], coat_light, None)
    poly([(58,95), (81,116), (103,166), (114,228), (94,219), (64,143)], coat_light, None)
    poly([(-21,40), (25,42), (22,78), (40,89), (6,124), (-36,89), (-20,76)], skin)
    poly([(-21,47), (25,50), (21,70), (-11,80), (-21,72)], shade, None)
    if outfit == "sports":
        poly([(-37,90), (4,115), (39,86), (50,102), (7,140), (-49,105)], light)
        line([(-67,130),(-87,203),(-92,249)], light, 7)
        line([(66,130),(86,207),(91,246)], light, 7)
    elif outfit == "fantasy":
        poly([(-47,84), (-18,102), (7,111), (32,99), (45,83), (67,104),
              (53,128), (6,147), (-56,118)], mid)
        poly([(4,130), (31,122), (47,222), (13,209)], mid)
        line([(-54,126),(5,151),(59,126)], light, 3)
    else:
        poly([(-24,82), (3,102), (26,81), (55,97), (29,159), (0,205), (-43,111)], (232,221,219))
        poly([(-25,83), (3,103), (-17,125), (-41,102)], (255,240,229))
        poly([(25,82), (5,103), (24,125), (46,101)], (255,240,229))
        poly([(-4,105), (12,105), (17,118), (13,151), (3,172), (-8,148), (0,120)], mid)
        line([(-54,100),(-39,146),(-10,190)], coat_light, 3)
    # Small foreground shoulder or bag strap distinguishes the poses.
    line([(-70,105),(-61,148),(-50,208),(-26,270)], outline, 9)
    line([(-68,108),(-58,149),(-46,208),(-24,268)], hair_shine, 4)
    oval(-61,-15,-38,18,shade)
    oval(38,-14,61,18,skin)
    poly([(-47,-55),(-38,-82),(-14,-94),(15,-92),(43,-77),(51,-45),(51,0),
          (45,23),(28,46),(7,56),(-10,52),(-32,37),(-44,15),(-49,-15)], skin, width=2)
    poly([(-47,-43),(-33,-22),(-32,12),(-19,42),(1,52),(-11,50),(-32,37),(-45,10)], shade, None)
    for eye_x in (-23, 24):
        poly([(eye_x-13,-12),(eye_x-8,-18),(eye_x+4,-19),(eye_x+13,-15),
              (eye_x+10,-6),(eye_x+4,-1),(eye_x-8,-3)], (255,239,227), None)
        oval(eye_x-5,-17,eye_x+7,-2,mid)
        oval(eye_x-2,-17,eye_x+5,-5,outline)
        oval(eye_x-2,-16,eye_x+2,-12,(255,248,237))
        line([(eye_x-14,-13),(eye_x-7,-18),(eye_x+4,-19),(eye_x+13,-15)], outline, 3)
        line([(eye_x-10,-28),(eye_x-1,-31),(eye_x+10,-28)], hair, 2)
    line([(7,-2),(10,10),(5,13)], shade)
    line([(-9,27),(1,29),(13,25)], outline)
    line([(-3,32),(4,33)], shade)
    # Layer angular locks over the forehead, leaving eyes and expression readable.
    part = rng.randrange(-16, 23)
    poly([(-58,-63),(-50,-85),(-30,-103),(0,-112),(30,-108),(56,-86),(64,-59),
          (53,-23),(43,-39),(38,-62),(19,-35),(part,-55),(part-21,-33),
          (-28,-46),(-44,-22),(-56,5),(-57,-18)], hair, width=2)
    line([(-50,-64),(-36,-84),(-16,-97),(4,-100)], hair_shine, 3)
    line([(14,-99),(38,-93),(53,-73),(56,-49)], hair_shine, 3)
    line([(part,-80),(part-13,-64),(part-21,-49)], hair_shine, 2)
    if long_hair:
        line([(-57,8),(-58,41),(-59,77)], hair_shine, 2)
        line([(56,2),(59,41),(60,79)], hair_shine, 2)


def draw_scene(slug, scene):
    family, main, detail = scene.split("/")
    dark, mid, light = map(rgb, PALETTES[family])
    rng = random.Random(sha256(slug.encode()).digest())
    motifs = {main, detail}
    if motifs & {"ball", "field", "glove"}:
        setting = "sports"
    elif motifs & {"music", "film", "clapper", "calendar"}:
        setting = "stage"
    elif motifs & {"ship", "wave"}:
        setting = "coast"
    elif motifs & {"blade", "skull", "mask", "tower", "flame", "hourglass", "planet", "bottle", "compass"}:
        setting = "fantasy"
    elif motifs & {"lightning", "target", "house"}:
        setting = "city"
    else:
        setting = "school"

    lighting = Image.new("RGB", (300, 158))
    pixels = []
    for y in range(158):
        for x in range(300):
            distance = (((x - 246) / 155)**2 + ((y - 59) / 117)**2)**.5
            glow = .82 * max(0, 1 - distance)
            pixels.append(blend(dark, mid, glow))
    lighting.putdata(pixels)
    image = lighting.resize((1200, 630), Image.Resampling.BICUBIC)
    draw = ImageDraw.Draw(image)
    paint_backdrop(draw, rng, setting, dark, mid, light)

    # Integrate the story motifs into the background and foreground of the scene.
    badge(draw, detail, 1124, 108, 38, blend(mid, light, .52), light, dark)
    outfit = "sports" if setting == "sports" else "fantasy" if setting in {"fantasy", "coast"} else "school"
    pair = bool(motifs & {"heart", "window", "music", "flower"}) and "blade" not in motifs
    if pair:
        paint_character(draw, 1055, 290, 1.04, rng, outfit, (dark, mid, light), mirror=True)
    cx = rng.randint(875, 932) if pair else rng.randint(959, 1012)
    cy = rng.randint(258, 304)
    paint_character(draw, cx, cy, rng.uniform(1.28, 1.48), rng, outfit, (dark, mid, light))
    if main != "window":
        ix, iy = (1115, 494) if main == "blade" else (1122, 505) if not pair else (1083, 519)
        badge(draw, main, ix, iy, 73, blend(mid, light, .86), light, dark)
    for _ in range(34):
        x, y = rng.randrange(738,1200), rng.randrange(25,622)
        if abs(x-cx) < 92 and abs(y-cy) < 105:
            continue
        size = rng.choice((1,2,2,3))
        draw.ellipse((x,y,x+size,y+size), fill=blend(mid, light, .52))
    return image
