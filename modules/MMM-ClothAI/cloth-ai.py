import json
import time, cv2, numpy
from transformers import pipeline
from colorthief import ColorThief
from PIL import Image
from globals import labels_to_labels, labels_to_write
from uuid import uuid4

def show_message(message):
    print(json.dumps(message))

session_id = str(uuid4())

matches = {
    'Pants': ['Upper-clothes'],
    'Upper-clothes': ['Pants'],
    'Dress': []
}

pipe = pipeline("image-segmentation", model="mattmdjaga/segformer_b2_clothes")
debug_img_path = 'cloth-ai/mirror-image.png'

data = {}

def predict_image():
    cam = cv2.VideoCapture(0, cv2.CAP_ANY)

    while True:
        ret, frame = cam.read()
        if ret == True:
            cv2.imshow('Webcam', frame)

            if cv2.waitKey(30) & 0xFF == ord('c'):
                break
        else:
            break

    cv2.waitKey()
    cv2.imwrite('cloth-ai/mirror-image.png', frame)

    time.sleep(3)

    image = Image.open(debug_img_path)
    res = pipe(image)
    seg_id = uuid4()

    for seg in res:
        # Detecção de roupas
        # if seg['label'] in labels_to_write:
        #     show_message(f"Detectado: {labels_to_labels[seg['label']]}")

        base_image = cv2.imread(debug_img_path)
        original_image = base_image.copy()
        seg_image_gray = seg['mask'].convert('L')

        seg_image_cv = numpy.array(seg['mask'])

        thresh = cv2.threshold(seg_image_cv, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

        cnts = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]

        pngs = []

        biggest_area = 0
        for c in cnts:
            x,y,w,h = cv2.boundingRect(c)
            cv2.rectangle(base_image, (x, y), (x+w, y+h), (0, 0, 0), 0)
            ROI = base_image[y:y+h, x:x+w]
            if seg['label'] in labels_to_write:
                pngs.append(f'modules/MMM-ClothAI/public/predicted_{seg["label"]}.png')

                roi_area = ROI.shape[0] * ROI.shape[1]
                
                if roi_area > biggest_area:
                    biggest_area = roi_area
                    cv2.imwrite(f'modules/MMM-ClothAI/public/predicted_{seg["label"]}.png', ROI)
                    cv2.imwrite(f'modules/MMM-ClothAI/public/predictionsLibrary/{seg_id}-{seg["label"]}.png', ROI)

                data[seg["label"]] = {
                    "w": 0,
                    "h": 0,
                    "name": "",
                    "image": "",
                    "dominant_color": ""
                }

                data[seg["label"]]["w"] = ROI.shape[0]
                data[seg["label"]]["h"] = ROI.shape[1]
                data[seg["label"]]["image"] = f"modules/MMM-ClothAI/public/predicted_{seg['label']}.png"

        # Detecção de cores de cada peça de roupa
        for png in pngs:
            color_thief = ColorThief(png)

            final_palette = []
            temp_palette = color_thief.get_palette(color_count=3)
            
            for palette in temp_palette:
                this_arr = []
                for color_n in palette:
                    this_arr.append(color_n)
                final_palette.append(this_arr)

            dom_color = color_thief.get_color()
            final_dom_color = []

            for color in dom_color:
                final_dom_color.append(color)

            data[seg["label"]]["name"] = labels_to_labels[seg["label"]]
            data[seg["label"]]["color_palette"] = final_palette
            data[seg["label"]]["dominant_color"] = final_palette[0]
        
        if seg["label"] in labels_to_write:
            color_t  = data[seg["label"]]["color_palette"][0]
            color = color_t[::-1]
            mask = seg["mask"]

            colored_mask = numpy.expand_dims(mask, 0).repeat(3, axis=0)
            colored_mask = numpy.moveaxis(colored_mask, 0, -1)
            masked = numpy.ma.MaskedArray(original_image, mask=colored_mask, fill_value=color)
            image_overlay = masked.filled()
            image_combined = cv2.addWeighted(original_image, 1-0.3, image_overlay, 0.3, 0)
            image_with_masks = image_overlay

            cv2.imwrite(f'modules/MMM-ClothAI/public/image-overlay-{seg["label"]}.png', image_with_masks)

    with open("modules/MMM-ClothAI/public/predictData.json", "w", encoding='utf8') as prediction_file:
        upclothes = data.get("Upper-clothes")
        dress = data.get("Dress")

        pants = data.get("Pants")
        skirt = data.get("Skirt")

        if upclothes != None and dress != None:
            uparea = upclothes["w"] * upclothes["h"]
            dressarea = dress["w"] * dress["h"]

            if uparea > dressarea:
                data.pop("Dress")
            else:
                data.pop("Upper-clothes")
        
        if pants != None and skirt != None:
            pantsarea = pants["w"] * pants["h"]
            skirtarea = skirt["w"] * skirt["h"]

            if pantsarea > skirtarea:
                data.pop("Skirt")
            else:
                data.pop("Pants")
        
        json.dump(data, prediction_file, indent=4)
        prediction_file.close()

    def save_on_library():
        with open(f"modules/MMM-ClothAI/public/predictionsLibrary/{seg_id}.json", "w+", encoding='utf8') as library_file:
            upclothes = data.get("Upper-clothes")
            dress = data.get("Dress")

            pants = data.get("Pants")
            skirt = data.get("Skirt")

            if upclothes != None and dress != None:
                uparea = upclothes["w"] * upclothes["h"]
                dressarea = dress["w"] * dress["h"]

                if uparea > dressarea:
                    data.pop("Dress")
                else:
                    data.pop("Upper-clothes")
            
            if pants != None and skirt != None:
                pantsarea = pants["w"] * pants["h"]
                skirtarea = skirt["w"] * skirt["h"]

                if pantsarea > skirtarea:
                    data.pop("Skirt")
                else:
                    data.pop("Pants")
            
            json.dump(data, library_file, indent=4)
            library_file.close()

    show_message(data)

# predict_image()