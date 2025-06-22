# self usage
import os, shutil

paths = {
    "Anime": "ImageDataLocal",
    "Sprite": "NumberLocal",
    "Unit": "UnitLocal",
    "Enemy": "ImageLocal",
}

anime = {
    "00": "walk",
    "01": "idle",
    "02": "attack",
    "03": "kb",
}


def parse(units: list):
    for unit in units:
        BCU_folder = os.path.join(os.getenv("BCU"), unit)
        os.makedirs(BCU_folder, exist_ok=True)
        id, form = unit.split("_")
        id = id.zfill(3)
        if form in ["f", "c", "s", "u"]:
            name = f"uni{id}_{form}00.png"
        else:
            name = f"enemy_icon_{id}.png"
        # icon
        try:
            shutil.copyfile(
                os.path.join(os.getenv("BC"), paths["Unit"], name),
                os.path.join(BCU_folder, "icon_deploy.png"),
            )
        except:
            shutil.copyfile(
                "../resources/icon_deploy.png",
                os.path.join(BCU_folder, "icon_deploy.png"),
            )
        # sprite
        shutil.copyfile(
            os.path.join(os.getenv("BC"), paths["Sprite"], f"{id}_{form}.png"),
            os.path.join(BCU_folder, "sprite.png"),
        )
        # imgcut
        try:
            shutil.copyfile(
                os.path.join(os.getenv("BC"), paths["Anime"], f"{id}_{form}.imgcut"),
                os.path.join(BCU_folder, "imgcut.txt"),
            )
        except:
            shutil.copyfile(
                "../resources/imgcut.txt", os.path.join(BCU_folder, "imgcut.txt")
            )
        # mamodel
        try:
            shutil.copyfile(
                os.path.join(os.getenv("BC"), paths["Anime"], f"{id}_{form}.mamodel"),
                os.path.join(BCU_folder, "mamodel.txt"),
            )
        except:
            shutil.copyfile(
                "../resources/mamodel.txt", os.path.join(BCU_folder, "mamodel.txt")
            )
        # maanim
        for _ in ["00", "01", "02", "03"]:
            try:
                shutil.copyfile(
                    os.path.join(
                        os.getenv("BC"), paths["Anime"], f"{id}_{form}{_}.maanim"
                    ),
                    os.path.join(BCU_folder, f"maanim_{anime[_]}.txt"),
                )
            except:
                shutil.copyfile(
                    f"../resources/maanim_{anime[_]}.txt",
                    os.path.join(BCU_folder, f"maanim_{anime[_]}.txt"),
                )
        shutil.copyfile(
            "../resources/maanim_burrow_up.txt",
            os.path.join(BCU_folder, "maanim_burrow_up.txt"),
        )
        shutil.copyfile(
            "../resources/maanim_burrow_down.txt",
            os.path.join(BCU_folder, "maanim_burrow_down.txt"),
        )
        shutil.copyfile(
            "../resources/maanim_burrow_move.txt",
            os.path.join(BCU_folder, "maanim_burrow_move.txt"),
        )
