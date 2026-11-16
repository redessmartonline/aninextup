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
    if setting == "space":
        draw.ellipse((984, 58, 1156, 230), fill=ground, outline=far, width=3)
        draw.arc((954, 89, 1184, 211), 5, 175, fill=rim, width=2)
        for _ in range(62):
            x, y = rng.randrange(690, 1200), rng.randrange(18, 630)
            if (x-1070)**2 + (y-144)**2 > 86**2:
                draw.point((x,y), fill=rim)
        return
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


# Subjects selected from the premises, rather than from a palette or an article tag.
COVER_SUBJECTS = {
    "mercedes-and-the-waning-moon-anime": "vampire-dungeon",
    "yumeneko-connect-anime-announcement": "cat",
    "paw-palaces-creditless-ending-october-2026": "palace-cats",
    "sasaki-and-peeps-season-2": "bird",
    "sasaki-and-peeps-season-2-anime-shares-creditless-opening-and-end-a03f04c7": "bird",
    "takopis-original-sin-movie": "alien",
    "reincarnated-goblin": "goblin",
    "reincarnated-as-a-sword-season-2-english-dub-release-date": "sword",
    "cosmoship-yamato-root-2199": "space-battleship",
    "reborn-space-mercenary": "starfighter",
    "mobile-suit-gundam-seed-freedom-zero-release-date": "mecha",
    "votoms-gray-witch-part-1": "armored-trooper",
    "dandivine-release-date": "mecha",
    "dark-machine-the-animation": "armored-trooper",
    "eleceed-anime-april-2027-release-date": "electric-cat",
}


def paint_story_subject(draw, subject, dark, mid, light):
    ink = blend(dark, (12, 13, 24), .55)
    shadow = blend(dark, mid, .73)
    shine = blend(mid, light, .67)

    def shape(points, fill, width=4):
        draw.polygon(points, fill=fill, outline=ink, width=width)

    def ellipse(box, fill):
        draw.ellipse(box, fill=fill, outline=ink, width=4)

    if subject in {"cat", "palace-cats", "electric-cat"}:
        if subject == "palace-cats":
            for y in (191, 258):
                shape([(760,y+18),(799,y+12),(843,y-24),(1085,y-24),
                       (1129,y+12),(1184,y+16),(1147,y+33),(786,y+33)], shadow)
                for x in (838, 920, 1010, 1090):
                    draw.rectangle((x,y+28,x+9,y+85),fill=shine)
        elif subject == "electric-cat":
            for dx in (0, 96):
                draw.line([(835+dx,132),(811+dx,216),(861+dx,205),(827+dx,275)],
                          fill=light,width=8,joint="curve")
        fur = (242, 189, 143) if subject != "cat" else (189, 177, 215)
        # Tail, seated body and forepaws are drawn behind the broad cheek silhouette.
        draw.arc((982,320,1162,520),325,160,fill=ink,width=35)
        draw.arc((985,323,1159,517),325,160,fill=fur,width=27)
        ellipse((866,326,1059,548),fur)
        ellipse((884,493,955,551),fur)
        ellipse((967,493,1037,551),fur)
        shape([(851,279),(846,164),(914,209),(1004,205),(1052,158),(1060,280),
               (1040,328),(993,359),(911,358),(866,329)],fur)
        shape([(860,192),(866,246),(899,218)],(224,135,151),2)
        shape([(1038,184),(1017,216),(1045,240)],(224,135,151),2)
        for x in (910, 1003):
            ellipse((x-18,259,x+18,285),light)
            draw.ellipse((x-5,260,x+6,282),fill=ink)
        shape([(946,296),(966,296),(956,306)],ink,1)
        draw.arc((925,297,957,319),5,150,fill=ink,width=3)
        draw.arc((955,297,987,319),30,175,fill=ink,width=3)
        for dx in (-1,1):
            for i in range(3):
                draw.line((956+dx*47,303+i*7,956+dx*99,294+i*13),fill=ink,width=2)
        if subject == "palace-cats":
            shape([(761,473),(758,405),(788,427),(822,428),(849,405),(848,474),
                   (831,500),(777,501)],(214,169,130))
            for x in (784,821):
                draw.ellipse((x-4,461,x+4,469),fill=ink)
        return

    if subject == "vampire-dungeon":
        # Moonlight beyond a stone arch frames an original cloaked explorer.
        draw.rounded_rectangle((789, 66, 1181, 660), radius=181, fill=shadow, outline=ink, width=6)
        draw.rounded_rectangle((819, 99, 1151, 660), radius=154, fill=dark, outline=shine, width=4)
        for y in (264, 340, 416, 492, 568):
            draw.line((792, y, 816, y), fill=shine, width=3)
            draw.line((1155, y, 1178, y), fill=shine, width=3)
        draw.ellipse((956, 126, 1086, 256), fill=light)
        draw.ellipse((990, 113, 1097, 232), fill=dark)
        cloak = (123, 50, 92)
        cloak_light = (185, 83, 122)
        shape([(959, 304), (1020, 314), (1083, 389), (1149, 631), (804, 631),
               (873, 454), (909, 363)], cloak, 6)
        shape([(971, 361), (884, 632), (1017, 632), (1032, 488), (1011, 392)], ink)
        shape([(904, 376), (934, 337), (964, 357), (981, 390), (915, 415)], cloak_light)
        shape([(970, 381), (1006, 341), (1058, 376), (1043, 420), (1004, 413)], cloak_light)
        shape([(904, 330), (900, 259), (934, 214), (979, 203), (1022, 222),
               (1040, 273), (1027, 331), (995, 362), (941, 355)], ink)
        shape([(935, 259), (987, 244), (1014, 279), (1010, 315), (984, 345),
               (957, 335), (938, 310)], (230, 196, 201))
        shape([(904, 278), (929, 227), (974, 211), (1018, 230), (1028, 271),
               (990, 256), (960, 284), (956, 263), (929, 304)], (70, 58, 93))
        draw.line((944, 266, 973, 237, 1005, 246), fill=shine, width=3, joint="curve")
        draw.line((971, 290, 986, 286, 998, 290), fill=ink, width=4, joint="curve")
        draw.ellipse((982, 289, 989, 298), fill=cloak)
        draw.line((980, 319, 995, 316), fill=ink, width=2)
        ellipse((968, 395, 994, 421), shine)
        draw.line((1071, 505, 1123, 476), fill=light, width=4)
        draw.rounded_rectangle((1101, 476, 1144, 530), radius=7, fill=shine, outline=ink, width=4)
        draw.rectangle((1112, 487, 1133, 519), fill=(250, 204, 136))
        return

    if subject == "bird":
        draw.line([(774,508),(932,469),(1148,484)],fill=ink,width=20,joint="curve")
        draw.line([(774,505),(932,466),(1148,481)],fill=shine,width=8,joint="curve")
        ellipse((888,268,1082,476),(173,182,200))
        shape([(1000,361),(1061,373),(1089,501),(1021,481)],(100,117,156))
        ellipse((855,196,1010,351),(224,223,226))
        ellipse((869,226,951,319),(239,237,222))
        shape([(859,264),(816,283),(862,298)],(234,137,152))
        ellipse((886,239,910,266),ink)
        draw.ellipse((893,242,900,250),fill=(254,251,239))
        for x in (927,996):
            draw.line((x,445,x-5,477,x-23,485),fill=(245,159,159),width=7,joint="curve")
        return

    if subject == "alien":
        body = (238, 154, 191)
        for i in range(5):
            x=850+i*48
            ellipse((x,343+(i%2)*28,x+82,490+(i%2)*26),body)
        ellipse((828,155,1103,421),body)
        draw.arc((847,177,1074,397),195,277,fill=(255,222,233),width=12)
        for x in (911,1013):
            ellipse((x-13,253,x+13,292),ink)
            draw.ellipse((x-4,254,x+4,264),fill=(255,245,248))
        draw.arc((933,281,990,329),0,180,fill=ink,width=5)
        return

    if subject == "sword":
        shape([(844,478),(870,432),(1067,143),(1129,93),(1111,178),(910,460)],(225,234,246),5)
        shape([(870,432),(1067,143),(1129,93),(900,443)],(139,191,218),3)
        shape([(820,429),(845,415),(949,471),(929,491)],shine,5)
        shape([(860,449),(891,466),(828,557),(797,540)],shadow,5)
        ellipse((785,531,829,574),shine)
        return

    if subject in {"space-battleship", "starfighter"}:
        if subject == "space-battleship":
            shape([(757,410),(843,323),(989,296),(1045,304),(1167,366),(1131,402),(919,449)],shine)
            shape([(759,410),(927,420),(1167,366),(1115,429),(916,480),(788,449)],shadow)
            shape([(900,323),(924,273),(981,256),(1005,301)],shine)
            shape([(943,284),(954,217),(986,212),(998,270)],shadow)
            for x,y in ((862,331),(1014,319)):
                draw.line((x,y,x+19,y-29,x+70,y-36),fill=ink,width=9,joint="curve")
        else:
            shape([(744,453),(844,312),(926,342),(1011,207),(1163,290),(1050,427),(930,456)],shine)
            shape([(792,445),(920,365),(1011,207),(993,388),(1087,378),(1038,461),(921,493)],shadow)
            shape([(974,278),(1014,243),(1080,274),(1037,304)],light)
        for y in (424,445):
            draw.line((775,y,693,y+23),fill=light,width=7)
        return

    if subject in {"mecha","armored-trooper"}:
        armored = subject == "armored-trooper"
        plating = blend(shadow,light,.29 if armored else .67)
        shape([(766,531),(771,397),(807,338),(898,318),(1021,315),(1100,357),
               (1168,453),(1200,562),(1106,601),(931,546)],plating)
        shape([(771,397),(829,375),(929,419),(944,548),(769,531)],shadow)
        shape([(1031,365),(1104,358),(1177,472),(1158,547),(1050,498)],shadow)
        shape([(855,190),(894,153),(1015,150),(1067,196),(1072,283),(1026,342),
               (918,361),(861,319)],plating)
        shape([(872,222),(1035,195),(1060,239),(1048,299),(938,317),(879,288)],ink)
        if armored:
            for x,y,r in ((937,258,35),(1008,238,23),(1012,284,17)):
                ellipse((x-r,y-r,x+r,y+r),shine)
                ellipse((x-r//2,y-r//2,x+r//2,y+r//2),ink)
        else:
            shape([(889,244),(974,246),(1039,222),(1020,257),(971,274),(903,270)],light)
            shape([(942,163),(910,99),(956,139),(975,121),(1015,85),(990,156)],shine)
        for x in (886,942,996):
            draw.line((x,402,x+39,426),fill=light,width=5)
        return

    # A non-human adventurer with pointed ears and a leather travel outfit.
    green = (119, 179, 120)
    shape([(823,532),(833,391),(906,322),(1016,328),(1091,405),(1125,530)],shadow)
    shape([(896,221),(804,178),(821,253),(873,289),(897,277)],green)
    shape([(1006,218),(1115,173),(1093,251),(1047,289),(1018,274)],green)
    shape([(860,234),(886,166),(948,139),(1017,156),(1066,212),(1052,293),
           (1010,345),(943,356),(891,320)],green)
    for x in (918,998):
        shape([(x-24,220),(x+23,228),(x+15,250),(x-12,251)],(246,218,132))
        ellipse((x-4,228,x+7,247),ink)
    draw.line((925,296,961,306,1003,290),fill=ink,width=4,joint="curve")
    shape([(923,303),(940,304),(929,280)],(245,227,198),2)
    shape([(990,298),(1004,293),(994,273)],(245,227,198),2)
    draw.line((876,364,1028,513),fill=shine,width=19)


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

    subject = COVER_SUBJECTS.get(slug)
    if subject in {"space-battleship", "starfighter", "mecha", "armored-trooper"}:
        setting = "space"
    elif subject == "palace-cats":
        setting = "fantasy"

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

    if subject:
        paint_story_subject(draw, subject, dark, mid, light)
        return image

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
