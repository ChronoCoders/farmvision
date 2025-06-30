import torch
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
from ultralytics import YOLO




corn_diseases_and_recommendations = {
    'Corn maize healthy': {
        'recommendations': 'Congratulations! Your Corn is healthy.'
    },
    'Cercospora Leaf Spot Gray Leaf Spot': {
        'recommendations': 'This is a serious fungal disease caused by Cercospora zeae-maydis. It primarily damages corn leaves. Symptoms include small, gray, oval lesions. Management involves resistant varieties, crop rotation, residue management, and fungicides.'
    },
    'Corn maize Northern Leaf Blight': {
        'recommendations': 'This is a widespread fungal disease that significantly impacts yield, caused by Exserohilum turcicum. It mainly damages corn leaves, forming long, oval, grayish-green lesions that turn necrotic. Management involves resistant hybrids, crop rotation, residue management, and fungicides.'
    },
    'Corn maize Common rust': {
        'recommendations': 'This is a common fungal disease of corn caused by Puccinia sorghi, also known as corn common rust. It forms small, round to oval, orange-brown pustules on leaves. Management includes resistant varieties, fungicides, and field sanitation.'
    }
}












def leaf_disease_detection(img_path):
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = YOLO(f"{BASE_DIR}/detection/yolo/corn_leaf.pt")
    results = model.predict(source=img_path, conf=0.25, iou=0.7, show=False, save=True,project=f"{BASE_DIR}/static",name='detected',  device=device, exist_ok=True)
    results_dict = {}
    for r in results:       
        print(f"Şəkil '{r.path}' üçün {len(r.boxes)} obyekt aşkarlanmışdır.")

        
        for box in r.boxes:
            cls_id = int(box.cls)
            conf = float(box.conf)
            xyxy = box.xyxy[0].tolist() 

            print(f"Sinif: {r.names[cls_id]}, Əminlik: {conf:.2f}, Koordinatlar: {xyxy}")
            results_dict['class_name'] = r.names[cls_id]
            results_dict['confidence'] = conf

    if results_dict.get('class_name') in corn_diseases_and_recommendations:
        recommendation_text = corn_diseases_and_recommendations.get(results_dict.get('class_name'))['recommendations']
        print(f"Aşkarlanan sinif: {results_dict['class_name']}")
        print(f"Tövsiyə: {recommendation_text}")
        return {'name': results_dict.get('class_name'),'recommendations': recommendation_text}
    else:
        return {'name': results_dict.get('class_name'),'recommendations': 'Not recommendation'} 








""" Leaf disease classification dictionary with recommendations.

leaf_class = {1:{'name': 'Apple Scab', 'recommendations':'Elma Karalekesi Hastalığı (Apple Scab) Elma Karalekesi Hastalığı, elma ve bazı diğer gülgiller familyasından süs bitkileri (özellikle yaban elması) ile armut ağaçlarında görülen, ekonomik açıdan en önemli ve yaygın fungal hastalıklardan biridir. Elma için Venturia inaequalis mantarı, armut için ise Venturia pyrina mantarı bu hastalığa neden olur.',},
              2:{'name': 'Apple Black rot', 'recommendations':'test etdim2'},
              3:{'name': 'Apple Healthy', 'recommendations':'test etdim2'},
              4:{'name': 'Blueberry Healthy', 'recommendations':'test etdim2'},
              5:{'name': 'Cherry (including_sour) Powdery mildew', 'recommendations':'test etdim2'},
              6:{'name': 'Cherry (including_sour) Healthy', 'recommendations':'test etdim2'},
              7:{'name': 'Corn (maize) Cercospora leaf spot Gray leaf spot', 'recommendations':'test etdim2'},
              8:{'name': 'Corn (maize) Common rust', 'recommendations':'test etdim2'},
              9:{'name': 'Apple Black rot', 'recommendations':'test etdim2'},
              10:{'name': 'Corn (maize) Northern Leaf Blight', 'recommendations':'test etdim2'},
              11:{'name': 'Corn (maize) healthy', 'recommendations':'test etdim2'},
              12:{'name': 'Grape Black rot', 'recommendations':'test etdim2'},
              13:{'name': 'Grape Esca (Black Measles)', 'recommendations':'test etdim2'},
              14:{'name': 'Grape Leaf blight_(Isariopsis_Leaf_Spot)', 'recommendations':'test etdim2'},
              15:{'name': 'Grape Healthy', 'recommendations':'test etdim2'},
              16:{'name': 'Orange Haunglongbing (Citrus greening)', 'recommendations':'test etdim2'},
              17:{'name': 'Peach Bacterial Spot', 'recommendations':'test etdim2'},
              18:{'name': 'Peach healthy', 'recommendations':'test etdim2'},
              19:{'name': 'Pepper bell Bacterial spot', 'recommendations':'test etdim2'},
              20:{'name': 'Pepper bell healthy', 'recommendations':'test etdim2'},
              21:{'name': 'Potato Early blight', 'recommendations':'test etdim2'},
              22:{'name': 'Potato Late blight', 'recommendations':'test etdim2'},
              23:{'name': 'Potato healthy', 'recommendations':'test etdim2'},
              24:{'name': 'Raspberry healthy', 'recommendations':'test etdim2'},
              25:{'name': 'Soybean healthy', 'recommendations':'test etdim2'},
              26:{'name': 'Squash Powdery_mildew', 'recommendations':'test etdim2'},
              27:{'name': 'Strawberry Leaf scorch', 'recommendations':'test etdim2'},
              28:{'name': 'Strawberry healthy', 'recommendations':'test etdim2'},
              29:{'name': 'Tomato Bacterial spot', 'recommendations':'test etdim2'},
              30:{'name': 'Tomato Early blight', 'recommendations':'test etdim2'},
              31:{'name': 'Tomato Late Blight', 'recommendations':'test etdim2'},
              32:{'name': 'Tomato Leaf Mold', 'recommendations':'test etdim2'},
              33:{'name': 'Tomato Septoria leaf spot', 'recommendations':'test etdim2'},
              34:{'name': 'Tomato Spider mites Two-spotted spider mite', 'recommendations':'test etdim2'},
              35:{'name': 'Tomato Target Spot', 'recommendations':'test etdim2'},
              36:{'name': 'Tomato Yellow Leaf Curl Virus', 'recommendations':'test etdim2'},
              37:{'name': 'Tomato mosaic virus', 'recommendations':'test etdim2'},
              38:{'name': 'Tomato Healthy', 'recommendations':'test etdim2'},
              39:{'name': 'background', 'recommendations':'test etdim2'},
              
              
}

"""