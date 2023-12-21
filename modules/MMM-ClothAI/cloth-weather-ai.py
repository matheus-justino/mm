import requests, cv2, os, time, sys, threading, json, numpy, geocoder, datetime, codecs

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

from PIL import Image
from transformers import BlipProcessor, BlipForQuestionAnswering, pipeline
from skimage import metrics
from colorthief import ColorThief
from PIL import Image
from globals import labels_to_labels, labels_to_write
from uuid import uuid4

def show_message(message):
    print(json.dumps(message))

# Global data
weather_data = {}
cloth_data = {}
data = {}

# Etc
session_id = str(uuid4())

matches = {
    'Pants': ['Upper-clothes'],
    'Upper-clothes': ['Pants'],
    'Dress': []
}

pipe = pipeline("image-segmentation", model="mattmdjaga/segformer_b2_clothes")
debug_img_path = 'cloth-ai/mirror-image.png'

def predict_clothes():
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

    cloth_data = data

def is_cloth_for_weather(cloth_target:str):
    geolocation = geocoder.ip('me')
    my_lat = geolocation.lat
    my_lng = geolocation.lng

    weather_api_key = "5c74affbd4a748bda72162536231312"
    weather_api_base_url = "http://api.weatherapi.com/v1/"
    weather_api_general = "forecast.json"

    r = requests.get(f"{weather_api_base_url}{weather_api_general}?key={weather_api_key}&q={my_lat},{my_lng}&days=3&aqi=no&alerts=no")

    forecast_hours = {
        0: '06',
        1: '06',
        2: '06',
        3: '06',
        4: '08',
        5: '08',
        6: '10',
        7: '10',
        8: '12',
        9: '12',
        10: '12',
        11: '14',
        12: '16',
        13: '19',
        14: '20',
        15: '20',
        16: '20',
        17: '20',
        18: '21',
        19: '22',
        20: '23'
    }

    now = datetime.datetime.now()

    data = r.json()

    for hour in data['forecast']['forecastday'][0]['hour']:
        # Mesmo dia, mesma hora.
        if hour['time'][:10] == now.strftime("%Y-%m-%d") and now.hour <= 20 and forecast_hours[now.hour] == hour['time'][11:13]:
            future_temp = hour['temp_c']
            weather_data['temp'] = data['current']['temp_c']
            weather_data['wind_velocity'] = data['current']['wind_kph']

            chance_of_rain = hour['chance_of_rain']
            will_it_rain_hour = hour['will_it_rain']
            weather_data['will_rain'] = data['forecast']['forecastday'][0]['day']['daily_will_it_rain']

            weather_data['condition'] = hour['condition']

    def get_weather_by_temp(temp):
        if temp < 8:
            return 'very cold'
        elif temp > 10 and temp < 18:
            return 'cold'
        elif temp > 18 and temp < 25:
            return 'neutral'
        elif temp > 25 and temp < 30:
            return 'hot'
        else:
            return 'very hot'
        
    def get_coldness_by_wind(temp, wind_velocity):
        if temp < 18 and wind_velocity > 50:
            return 'cold wind'
        elif temp > 18 and wind_velocity > 50:
            return 'fresh wind'
        
        if temp > 30 and wind_velocity < 30:
            return 'hot wind'
        elif temp < 18 and wind_velocity < 30:
            return 'weak wind'
        
    def will_rain(will_rain):
        if will_rain == 1:
            return True
        else:
            return False

    processor = BlipProcessor.from_pretrained("Salesforce/blip-vqa-base")
    model = BlipForQuestionAnswering.from_pretrained("Salesforce/blip-vqa-base")

    raw_image = Image.open(cloth_target).convert('RGB')

    data = {
        "cloth_type": "",
        "weather": "",
        "wind": "",
        "will_rain": False,
        "for_this_weather": False,
        "recommendation": ""
    }

    cloth_weather_data = {
        'hot_weather': False,
        'cold_weather': False,
        'for_this_weather': False
    }

    data['weather'] = get_weather_by_temp(weather_data['temp'])
    data['wind'] = get_coldness_by_wind(weather_data['temp'], weather_data['wind_velocity'])
    data['will_rain'] = will_rain(weather_data['will_rain'])

    question = f"is the person wearing a cloth for {data['weather']} weather with {data['wind']}?"
    inputs = processor(raw_image, question, return_tensors="pt")
    out = model.generate(**inputs)
    response = processor.decode(out[0], skip_special_tokens=True)

    if "yes" in response.split(" ") or "yes." in response.split(" "):
        if data['weather'] == 'very cold' or data['weather'] == 'cold':
            cloth_weather_data['cold_weather'] = True
            cloth_weather_data['for_this_weather'] = True
        else:
            cloth_weather_data['hot_weather'] = True
            cloth_weather_data['for_this_weather'] = True
        return cloth_weather_data
    else:
        if data['weather'] == 'very cold' or data['weather'] == 'cold':
            cloth_weather_data['hot_weather'] = True
        else:
            cloth_weather_data['cold_weather'] = True
        return cloth_weather_data

def is_cloth_on_library(cloth_target:str):
    """
    Verifica se uma roupa já faz parte da biblioteca de roupas do usuário.

    `cloth_target` - o caminho para a imagem da roupa gerada pela IA (`/public/predictionsLibrary/{id}.png`)

    Retorna um objeto com as propriedades `action` e `message`.

    `action` - a ação a ser realizada (somente) pelo `node_helper` do módulo `ClothAI` (`add-to-library` ou `fly-by`)
    `message` - uma mensagem que informa o resultado da função

    {
        action: `socket-action: str`,
        message: `response-message: str`
    }
    """

    def similarity(img1:str, img2:str):
        """
        Verifica a similaridade entre duas roupas por meio do método de um script baseado no histograma de um par de imagens - `img1`, `img2`

        `img1` - caminho para a primeira imagem-alvo
        `img2` - caminho para a segunda imagem-alvo
        """

        img1 = cv2.imread(img1)
        img2 = cv2.imread(img2)
        hist_img1 = cv2.calcHist([img1], [0, 1, 2], None, [256, 256, 256], [0, 256, 0, 256, 0, 256])
        hist_img1[255, 255, 255] = 0
        cv2.normalize(hist_img1, hist_img1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        hist_img2 = cv2.calcHist([img2], [0, 1, 2], None, [256, 256, 256], [0, 256, 0, 256, 0, 256])
        hist_img2[255, 255, 255] = 0 
        cv2.normalize(hist_img2, hist_img2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        metric_val = cv2.compareHist(hist_img1, hist_img2, cv2.HISTCMP_CORREL)

        if round(metric_val, 2) > 0.46:
            return {'result': True, 'score': round(metric_val, 2)}
        else:
            return {'result': False, 'score': round(metric_val, 2)}
        
    def compare_cloth_to_library(cloth_target:str=cloth_target):
        """
        Compara a imagem de uma roupa com as roupas da biblioteca de predições/biblioteca de roupas do usuário.

        `cloth_target` - roupa a ser comparada com as roupas da biblioteca.
        """
        real_cloth_library = []
        for filename in os.listdir(os.getcwd()+'\\public\\predictionsLibrary'):
            img = f'public/predictionsLibrary/{filename}'
            if img[len(img)-3:] in ['png', 'jpg', 'jpeg']:
                real_cloth_library.append(img)    
        same = []
        for cloth in real_cloth_library:
            def get_cloth_class(cloth_path):
                cloth_split = cloth_path.split('-')
                if cloth_split[-2].endswith('Upper'):
                    return cloth_split[-2]+'-'+cloth_split[-1][:len(cloth_split[-1])-4]
                else:
                    return cloth_split[-1][:len(cloth_split[-1])-4]
                
            cloth1_class = get_cloth_class(cloth_target)
            cloth2_class = get_cloth_class(cloth)

            if cloth2_class == cloth1_class:
                result = similarity(cloth_target, cloth)
                if result['result']:
                    same.append({
                        'path': cloth,
                        'score': result['score']
                    })

        return sorted(same, key=lambda j: j['score'], reverse=True)

    def get_library_action():
        """
        Retorna uma ação a ser realizada pelo `node_helper` do módulo `ClothAI`, esta ação só pode ser realizada pelo `node_helper` deste módulo, não podendo ser processada pelos outros módulos do projeto.

        As ações retornadas podem ser:
        
        `add-to-library` - solicita a adição da imagem gerada pela IA à biblioteca de roupas do usuário, gerando uma `id` e um arquivo .json para a imagem.
        `fly-by` - permite que o `node_helper` ignore a chamada da ação e continue outros processos, basicamente não executa nenhuma ação.
        """
        similar_clothes = compare_cloth_to_library()

        if len(similar_clothes) >= 1:
            if similar_clothes[0]['score'] > 0.7:
                return {"action": "fly-by", "similar_clothes": similar_clothes, "code": "found-identical"}
            elif similar_clothes[0]["score"] > 0.5:
                return {"action": "add-to-library", "similar_clothes": similar_clothes, "code": "found-similar"}
            else:
                return {"action": "add-to-library", "similar_clothes": similar_clothes, "code": "found-nothing"}
        else:
            return {"action": "add-to-library", "similar_clothes": similar_clothes, "code": "found-nothing"}

    return get_library_action()

# Ideia para os comentários - notícias:
    # Se a pessoa passar mais da metade do tempo estimado de leitura na página e só depois comentar, checar a negatividade do comentário e então adicionar os pontos.

def cloth_library():
    cloth_on_library = is_cloth_on_library('public/predicted-Upper-clothes.png')
    show_message(cloth_on_library)

# predict_clothes()

cloth_weather_data = is_cloth_for_weather(os.getcwd()+'\\modules\\MMM-ClothAI\\public\\predicted_Upper-clothes.png')
show_message(cloth_weather_data)