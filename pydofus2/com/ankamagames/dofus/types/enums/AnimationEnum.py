class AnimationEnum:

    ANIM_STATIQUE: str = "AnimStatique"

    ANIM_MARCHE: str = "AnimMarche"

    ANIM_COURSE: str = "AnimCourse"

    ANIM_ATTAQUE_BASE: str = "AnimAttaque"

    ANIM_ATTAQUE0: str = ANIM_ATTAQUE_BASE + "0"

    ANIM_ATTAQUE1: str = ANIM_ATTAQUE_BASE + "1"

    ANIM_ATTAQUE2: str = ANIM_ATTAQUE_BASE + "2"

    ANIM_HIT: str = "AnimHit"

    ANIM_MORT: str = "AnimMort"

    ANIM_TACLE: str = "AnimTacle"

    ANIM_PICKUP: str = "AnimPickup"

    ANIM_STATIQUE_CARRYING: str = "AnimStatiqueCarrying"

    ANIM_MARCHE_CARRYING: str = "AnimMarcheCarrying"

    ANIM_COURSE_CARRYING: str = "AnimCourseCarrying"

    ANIM_HIT_CARRYING: str = "AnimHitCarrying"

    ANIM_MORT_CARRYING: str = "AnimMortCarrying"

    ANIM_TACLE_CARRYING: str = "AnimTacleCarrying"

    ANIM_DROP: str = "AnimDrop"

    ANIM_THROW: str = "AnimThrow"

    ANIM_VANISH: str = "AnimVanish"

    ANIM_STATIQUE_RANDOM: str = "AnimStatiqueRandom"

    ANIM_MARCHE_UNDERWATER: str = "AnimNageMarche"

    ANIM_COURSE_UNDERWATER: str = "AnimNageCourse"

    def __init__(self):
        super().__init__()
