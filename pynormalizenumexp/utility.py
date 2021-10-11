import json
import os
from importlib.resources import open_text
from dataclasses import dataclass
from typing import Dict, List

import pynormalizenumexp
from pynormalizenumexp.expression import NotationType

PLACE_HOLDER = "ǂ"
BASE_DICT_DIR = "resources/dict/"


@dataclass
class ChineseCharacter:
    character: str
    value: int
    notation_type: str


class DigitUtility(object):
    str_to_notation_type: Dict[str, int] = {}
    kansuji_09_to_value: Dict[str, int] = {}
    kansuji_kurai_to_power_val: Dict[str, int] = {}

    def load_dictionary(self, language: str, dict_path: str) -> List[ChineseCharacter]:
        with open_text(pynormalizenumexp.__package__, os.path.join(BASE_DICT_DIR, language, dict_path)) as fp:
            dict_obj = json.load(fp)
            load_target = [ChineseCharacter(character=char["character"], value=char["value"],
                                            notation_type=char["notation_type"]) for char in dict_obj["characters"]]

        return load_target

    def init_kansuji(self, language: str) -> None:
        chinese_characters = self.load_dictionary(language, "chinese_character.json")
        for c_char in chinese_characters:
            if c_char.notation_type == "09":
                notation_type = NotationType.KANSUJI_09

                self.kansuji_09_to_value[c_char.character] = c_char.value
            elif c_char.notation_type == "sen":
                notation_type = NotationType.KANSUJI_KURAI_SEN

                self.kansuji_kurai_to_power_val[c_char.character] = c_char.value
            elif c_char.notation_type == "man":
                notation_type = NotationType.KANSUJI_KURAI_MAN
            else:
                notation_type = NotationType.NOT_NUMBER

            self.str_to_notation_type[c_char.character] = notation_type

        self.kansuji_kurai_to_power_val["　"] = 0


class NormalizerUtility(object):
    pass
