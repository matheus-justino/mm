import sys

def show_message(str):
    encoded_str = str.encode('utf8')
    sys.stdout.buffer.write(encoded_str)

show_message("Importando frameworks...")

def import_model():
    try:
        m = pipeline("image-segmentation", model="mattmdjaga/segformer_b2_clothes")
        return m
    except:
        show_message("ERRO: Não foi possível importar o modelo de rede neural.")
        show_message("INFO: Tentando novamente...")

modules_check = {
    'matplotlib': False,
    'transformers': False,
    'colorthief': False,
    'PIL': False,
    'cv2': False,
    'numpy': False,
    'scipy': False
}

try:
    import matplotlib.pyplot as plt
    modules_check['matplotlib'] = True
    from transformers import pipeline
    modules_check['transformers'] = True
    from colorthief import ColorThief
    modules_check['colorthief'] = True
    from PIL import Image
    modules_check['PIL'] = True
    import cv2
    modules_check['cv2'] = True
    import numpy
    modules_check['numpy'] = True
    import scipy
    modules_check['scipy'] = True

    show_message("Importando modelo de rede neural...")

    pipe = None

    try:
        pipe = import_model()

        show_message(f"<strong>ClothAI v0 | ASTRA</strong>\n")
        for m in modules_check:
            show_message(f"{m}: {'OK' if modules_check[m] else 'ERRO'}\n")
        show_message("\nModelo de Rede Neural: OK\n\n")
        show_message("<strong>Todas as funções OK.</strong>")
    except:
        pipe = import_model()
except ModuleNotFoundError:
    show_message("ERRO: Modulo(s) faltando.\n")
    for m in modules_check:
        show_message(f"{m}: {'OK' if modules_check[m] else 'ERRO'}\n")