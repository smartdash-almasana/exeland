from pathlib import Path
import yaml

from exceland_factory.skills.skill_registry import get_skill
from exceland_factory.validators import load_spec
from exceland_factory.workbook_builder import build_workbook


def build_from_skill(skill_name: str, output_path: Path):
    skill_fn = get_skill(skill_name)

    spec_dict = skill_fn()

    tmp_path = output_path.parent / f"{skill_name}_tmp.yaml"

    with tmp_path.open("w", encoding="utf-8") as f:
        yaml.dump(spec_dict, f, allow_unicode=True)

    spec = load_spec(tmp_path)

    return build_workbook(spec, output_path)