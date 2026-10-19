# sign_alphabets.py
# Descripcion de cada sena y reglas de retroalimentacion POR LENGUA DE SENAS.
#
# Cada alfabeto (LSC, ASL, LIBRAS) tiene sus propias instrucciones, escritas en
# el idioma de su perfil, y sus propias reglas para la IA de Repaso. No se
# reutilizan las instrucciones de una letra entre alfabetos cuando la
# configuracion de la mano es distinta (p. ej. la A y la E de LSC llevan el
# pulgar abierto; la U de LSC usa indice y menique; la M, N y Q de LIBRAS
# apuntan hacia abajo).
#
# Las descripciones de LSC y LIBRAS se redactaron a partir de las imagenes de
# referencia del proyecto (src/gui_web/web/assets/letras/ y .../libras/).

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, Optional, Tuple

# (pulgar, indice, medio, anular, menique): True = extendido.
LetterPattern = Tuple[bool, bool, bool, bool, bool]

# Explicaciones de confusiones que los rasgos actuales permiten comprobar.
CHECK_UV_SEPARATION = "uv_separation"   # U = dedos juntos, V = separados
CHECK_BK_THUMB = "bk_thumb"             # B/K de ASL
CHECK_MN_THUMB_COVER = "mn_thumb_cover"  # M/N de ASL (pulgar bajo 3 o 2 dedos)
CHECK_TS_THUMB = "ts_thumb"             # T/S de ASL


@dataclass(frozen=True)
class SignAlphabet:
    sign_language: str
    descriptions: Dict[str, str]
    # Patron de dedos esperado. Solo para letras con un patron inequivoco; se
    # usa para explicar diferencias, nunca para clasificar.
    expected_fingers: Dict[str, LetterPattern]
    confusable_groups: Tuple[FrozenSet[str], ...]
    confusion_checks: FrozenSet[str]
    # Letras que se hacen con la mano de perfil.
    lateral_letters: FrozenSet[str]
    # Letras cuya orientacion no se evalua (apuntan hacia abajo, tienen
    # movimiento o se ven de lado en la referencia).
    orientation_free_letters: FrozenSet[str]

    def describe(self, letter: str) -> Optional[str]:
        return self.descriptions.get((letter or "").strip().upper())


_ASL = SignAlphabet(
    sign_language="ASL",
    descriptions={
        "A": "Make a fist and rest your thumb against the side of your index finger.",
        "B": "Hold your four fingers straight up and together, with your thumb folded across your palm.",
        "C": "Curve your fingers and thumb together to form the shape of a C.",
        "D": "Point your index finger up and touch the tips of your middle, ring and pinky fingers with your thumb.",
        "E": "Bend all four fingertips down toward your palm and tuck your thumb underneath them.",
        "F": "Touch the tips of your thumb and index finger to form a circle, keeping the other three fingers extended and spread.",
        "G": "Point your index finger and thumb sideways, parallel to each other, with the other fingers closed.",
        "H": "Extend your index and middle fingers together, pointing sideways, with your hand horizontal.",
        "I": "Raise only your pinky finger and keep the other fingers closed in a fist.",
        "J": "Start with the I handshape and trace a J in the air with your pinky.",
        "K": "Raise your index and middle fingers in a V and place your thumb between them, touching the middle finger.",
        "L": "Extend your thumb and index finger to form an L, with the other fingers closed.",
        "M": "Close your hand and tuck your thumb under your index, middle and ring fingers.",
        "N": "Close your hand and tuck your thumb under your index and middle fingers.",
        "O": "Curve all your fingers to meet your thumb, forming an O.",
        "P": "Make the K handshape and point it downward.",
        "Q": "Make the G handshape and point it downward.",
        "R": "Cross your middle finger over your index finger.",
        "S": "Make a fist with your thumb wrapped across the front of your fingers.",
        "T": "Make a fist and tuck your thumb between your index and middle fingers.",
        "U": "Raise your index and middle fingers together, touching each other.",
        "V": "Raise your index and middle fingers apart to form a V.",
        "W": "Raise your index, middle and ring fingers spread apart, holding your pinky down with your thumb.",
        "X": "Raise your index finger and bend it into a hook.",
        "Y": "Extend your thumb and pinky, keeping the other fingers closed.",
        "Z": "Point with your index finger and draw a Z in the air.",
    },
    expected_fingers={
        "A": (False, False, False, False, False),
        "B": (False, True, True, True, True),
        "D": (False, True, False, False, False),
        "F": (False, False, True, True, True),
        "G": (True, True, False, False, False),
        "I": (False, False, False, False, True),
        "K": (True, True, True, False, False),
        "L": (True, True, False, False, False),
        "M": (False, False, False, False, False),
        "N": (False, False, False, False, False),
        "O": (False, False, False, False, False),
        "S": (False, False, False, False, False),
        "T": (False, False, False, False, False),
        "U": (False, True, True, False, False),
        "V": (False, True, True, False, False),
        "W": (False, True, True, True, False),
        "Y": (True, False, False, False, True),
    },
    confusable_groups=(
        frozenset({"U", "V"}),
        frozenset({"B", "K"}),
        frozenset({"M", "N"}),
        frozenset({"A", "S", "E", "T"}),
        frozenset({"C", "D", "F", "G", "O"}),
    ),
    confusion_checks=frozenset({CHECK_UV_SEPARATION, CHECK_BK_THUMB, CHECK_MN_THUMB_COVER, CHECK_TS_THUMB}),
    lateral_letters=frozenset({"G", "H"}),
    orientation_free_letters=frozenset({"C", "P", "Q", "J", "Z"}),
)

_LSC = SignAlphabet(
    sign_language="LSC",
    descriptions={
        "A": "Cierra el puño y extiende el pulgar hacia el costado, separado de los dedos.",
        "B": "Estira los cuatro dedos juntos hacia arriba y dobla el pulgar sobre la palma.",
        "C": "Curva los dedos juntos y el pulgar enfrentado a ellos, formando una C.",
        "D": "Levanta el índice recto y une la punta del pulgar con la del dedo medio formando un aro; el anular y el meñique quedan doblados.",
        "E": "Dobla los cuatro dedos hacia la palma y deja el pulgar extendido hacia el costado.",
        "F": "Levanta el índice con el pulgar apoyado a su lado y dobla el medio, el anular y el meñique.",
        "G": "Dobla el índice y el pulgar en forma de gancho, apuntando hacia el costado, y gira la muñeca.",
        "H": "Estira el índice y el medio juntos en horizontal, apuntando hacia el costado.",
        "I": "Levanta solo el meñique y cierra los demás dedos con el pulgar por delante.",
        "J": "Desde la forma de la I, dibuja con el meñique una curva hacia abajo, como una J.",
        "K": "Levanta el índice en diagonal, estira el medio hacia el costado y apoya el pulgar sobre el medio.",
        "L": "Estira el pulgar y el índice formando una L, con los demás dedos doblados.",
        "M": "Con la palma hacia abajo, deja colgar el índice, el medio y el anular hacia abajo.",
        "N": "Con la palma hacia abajo, deja colgar el índice y el medio hacia abajo.",
        "Ñ": "Haz la N (índice y medio hacia abajo) y mueve la mano de lado a lado.",
        "O": "Une las puntas de todos los dedos con el pulgar formando un círculo.",
        "P": "Con la mano hacia abajo, estira el índice hacia abajo y une el pulgar con el dedo medio formando un aro.",
        "Q": "Junta los dedos estirados con el pulgar debajo, formando un pico que apunta hacia arriba.",
        "R": "Levanta el índice y el medio cruzados entre sí.",
        "S": "Cierra el puño con el pulgar cruzado por delante de los dedos.",
        "T": "Levanta el medio, el anular y el meñique separados y apoya el índice doblado en horizontal sobre el pulgar.",
        "U": "Levanta el índice y el meñique, y cierra el medio y el anular con el pulgar.",
        "V": "Levanta el índice y el medio separados, formando una V.",
        "W": "Levanta el índice, el medio y el anular separados; el pulgar sujeta el meñique.",
        "X": "Levanta el índice doblado en forma de gancho, con los demás dedos cerrados.",
        "Y": "Estira el pulgar y el meñique, con los demás dedos doblados.",
        "Z": "Con el índice extendido, dibuja una Z en el aire.",
    },
    expected_fingers={
        "A": (True, False, False, False, False),
        "B": (False, True, True, True, True),
        "D": (False, True, False, False, False),
        "E": (True, False, False, False, False),
        "I": (False, False, False, False, True),
        "L": (True, True, False, False, False),
        "S": (False, False, False, False, False),
        "U": (False, True, False, False, True),
        "V": (False, True, True, False, False),
        "W": (False, True, True, True, False),
        "Y": (True, False, False, False, True),
    },
    confusable_groups=(
        frozenset({"M", "N"}),
        frozenset({"A", "E", "S"}),
        frozenset({"C", "D", "O"}),
        frozenset({"I", "J"}),
        frozenset({"V", "W"}),
    ),
    confusion_checks=frozenset(),
    lateral_letters=frozenset({"G", "H"}),
    orientation_free_letters=frozenset({"C", "K", "M", "N", "Ñ", "P", "Q", "T", "J", "Z"}),
)

_LIBRAS = SignAlphabet(
    sign_language="LIBRAS",
    descriptions={
        "A": "Feche a mão e apoie o polegar na lateral do indicador.",
        "B": "Estique os quatro dedos juntos para cima e dobre o polegar sobre a palma.",
        "C": "Curve os dedos e o polegar formando a letra C.",
        "Ç": "Faça a configuração do C e balance a mão com um leve tremor.",
        "D": "Estique o indicador para cima e encoste o polegar nos outros dedos, formando um círculo.",
        "E": "Dobre os quatro dedos sobre o polegar, com a mão fechada.",
        "F": "Com a mão de lado, mantenha os dedos para cima e cruze o polegar à frente deles. Observe a imagem: F e T diferem na posição do polegar.",
        "G": "Estique só o indicador para cima e feche os outros dedos com o polegar por cima.",
        "H": "Estique o indicador e o médio afastados e gire a mão.",
        "I": "Levante só o dedo mínimo e feche os outros dedos.",
        "J": "Na configuração do I, desenhe um J no ar com o dedo mínimo.",
        "K": "Levante o indicador e o médio com o polegar entre eles e mova a mão para cima.",
        "L": "Estique o polegar e o indicador formando um L.",
        "M": "Com a palma para baixo, aponte o indicador, o médio e o anelar para baixo.",
        "N": "Com a palma para baixo, aponte o indicador e o médio para baixo.",
        "O": "Junte as pontas de todos os dedos ao polegar formando um círculo.",
        "P": "Com a mão na horizontal, aponte o indicador para a frente e dobre o médio abaixo dele.",
        "Q": "Aponte o indicador para baixo e feche os outros dedos.",
        "R": "Cruze o indicador e o médio, com os dedos para cima.",
        "S": "Feche a mão com o polegar cruzado à frente dos dedos.",
        "T": "Com a mão de lado, mantenha os dedos para cima e cruze o polegar à frente deles. Observe a imagem: T e F diferem na posição do polegar.",
        "U": "Levante o indicador e o médio juntos.",
        "V": "Levante o indicador e o médio afastados, formando um V.",
        "W": "Levante o indicador, o médio e o anelar afastados.",
        "X": "Com a mão na horizontal, dobre o indicador em gancho e mova a mão para o lado.",
        "Y": "Estique o polegar e o dedo mínimo, com os outros dedos fechados.",
        "Z": "Com o indicador estendido, desenhe um Z no ar.",
    },
    expected_fingers={
        "A": (False, False, False, False, False),
        "B": (False, True, True, True, True),
        "D": (False, True, False, False, False),
        "E": (False, False, False, False, False),
        "G": (False, True, False, False, False),
        "I": (False, False, False, False, True),
        "L": (True, True, False, False, False),
        "S": (False, False, False, False, False),
        "U": (False, True, True, False, False),
        "V": (False, True, True, False, False),
        "W": (False, True, True, True, False),
        "Y": (True, False, False, False, True),
    },
    confusable_groups=(
        frozenset({"U", "V"}),
        frozenset({"F", "T"}),
        frozenset({"M", "N"}),
        frozenset({"A", "E", "S"}),
        frozenset({"C", "Ç", "O"}),
        frozenset({"D", "G"}),
    ),
    confusion_checks=frozenset({CHECK_UV_SEPARATION}),
    lateral_letters=frozenset({"P", "X", "Z"}),
    orientation_free_letters=frozenset({"C", "Ç", "F", "T", "H", "K", "J", "M", "N", "Q"}),
)

SIGN_ALPHABET_RULES: Dict[str, SignAlphabet] = {"es": _LSC, "en": _ASL, "pt": _LIBRAS}


def get_sign_alphabet(language: str) -> SignAlphabet:
    from .profiles import normalize_language

    return SIGN_ALPHABET_RULES[normalize_language(language)]
