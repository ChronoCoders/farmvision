import subprocess,os,time
from pathlib import Path
import openpyxl
from natsort import natsorted 
import numpy as np
import glob
import zipfile
BASE_DIR = Path(__file__).resolve().parent.parent
from ultralytics import YOLO
import torch

python_path = "python"

def preddict(path_to_weights,path_to_source):
    os.chdir(f"{BASE_DIR}/detection/yolo")
    #os.setpgid()
    
    python_file = f"{BASE_DIR}/detection/yolo/detectcount.py" #"/home/murad/Belgeler/yolowebapp/detection/yolo/detectcount.py" 
    path_to_project= f"{BASE_DIR}/static"   #"/home/murad/Belgeler/yolowebapp/static"  
    detec = subprocess.check_output([python_path, python_file, "--weights", path_to_weights, "--conf", "0.1", "--img-size", "640", "--source", path_to_source, "--project", path_to_project, "--name", "detected"], timeout=600)
    #time.sleep(150)
    return detec

def multi_predictor(path_to_weights,path_to_source,ekilis_sira,hashing):
    
    a,b = ekilis_sira.split("-")
    path_to_source_images = natsorted(glob.glob(f"{path_to_source}/*"))
 

    exc_shit = list()
    os.chdir(f"{BASE_DIR}/detection/yolo")
    #os.setpgid()
    
    python_file = f"{BASE_DIR}/detection/yolo/detectcount.py" #"/home/murad/Belgeler/yolowebapp/detection/yolo/detectcount.py" 
    path_to_project= path_to_source   #"/home/murad/Belgeler/yolowebapp/static"  
    for images in path_to_source_images:
        
        detec = subprocess.check_output([python_path, python_file, "--weights", path_to_weights, "--conf", "0.1", "--img-size", "640", "--source", images, "--project", path_to_project, "--name", "detected"], timeout=6000)
        exc_shit.append(int(detec[-3:-1].decode("utf-8")))
    
    
    if not os.path.exists(f'{path_to_source}/excel'):
        os.makedirs(f'{path_to_source}/excel')
    data = np.array(exc_shit).reshape(int(a),int(b))
    wb = openpyxl.Workbook()
    ws = wb.active
    for i in data: 
        print(list(i))
        ws.append(list(i))
    wb.save(f'{path_to_source}/excel/output.xlsx')
    with zipfile.ZipFile(f"{BASE_DIR}/media/{hashing}_result.zip", mode="w") as archive:
        
        archive.write(f'{path_to_source}/excel/output.xlsx',"output.xlsx")
        for images in natsorted(glob.glob(f"{path_to_project}/detected/*")):
            print(images)
            archive.write(images,f"detected/{os.path.split(images)[-1]}")


    #return exc_shit

def tree_detection(img_path):
    print(img_path,"$$$$$$$$$$$$$$$$$$$$$$$$$$$")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    convertor = convert_tiff_to_jpg_png(img_path,f'{BASE_DIR}/static/convertor/convert.jpeg')
    model = YOLO(f"{BASE_DIR}/detection/yolo/agac.pt")
    results = model.predict(source=f'{BASE_DIR}/static/convertor/convert.jpeg', conf=0.25, iou=0.7, show=False, save=True,project=f"{BASE_DIR}/static",name='detected',  device=device, exist_ok=True)
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

    
        print(f"Aşkarlanan sinif: {results_dict['class_name']}",results_dict['confidence'])        
        return {'name': results_dict.get('class_name'),}
    else:
        return {'name': results_dict.get('class_name'),} 
    






def convert_tiff_to_jpg_png(tiff_path, output_folder, output_format='jpeg'):


    from PIL import Image
    im = Image.open('/home/murad/Belgeler/yolowebapp3/static/results/b475d7129f16232cd5df039f5e003fe7c1a8fa07/odm_orthophoto/odm_orthophoto.tif')
    if im.mode in ("RGBA", "P"): im = im.convert("RGB")
    im.save(f'{output_folder}')
