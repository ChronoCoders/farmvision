from django.shortcuts import render
from pathlib import Path
from django.core.files.storage import FileSystemStorage
import time
from yolowebapp2 import predict_tree,hashing,leaf_detection #,tasknode,options
BASE_DIR = Path(__file__).resolve().parent.parent
from django.http import FileResponse
from dron_map.models import Users

def index(request):
    if request.user.is_authenticated:
        print(str(BASE_DIR),"BASE_DIRBASE_DIRBASE_DIRBASE_DIR")
        userss = Users.objects.get(kat_id=request.user.id)
        response = {}
        if request.method == 'POST':

            meyve_qrupu = request.POST.get('meyve_qrupu')
            agac_sayi = request.POST.get('agac_sayi')
            agac_yasi = request.POST.get('agac_yasi')
            ekilis_sira = request.POST.get('ekilis_sira')
            filename = request.FILES.get('file')
            
            if meyve_qrupu is not None and agac_sayi is not None and agac_yasi is not None and ekilis_sira is not None and filename is not None:
                fs = FileSystemStorage(location=str(BASE_DIR)+"/static/images/")
                saved_filename = fs.save(filename.name, filename)
                start_time = time.time()
                
                if meyve_qrupu == "mandalina":
                    if 0 < int(agac_yasi) <= 4:
                        
                        detec = predict_tree.preddict(path_to_weights="mandalina.pt",path_to_source=f"{BASE_DIR}/static/images/{filename}")
                        #detec = subprocess.check_output(["/home/murad/Belgeler/myprojectenv/bin/python","/home/murad/Belgeler/yolowebapp/polls/yolo/detectcount.py", "--weights", "mandalina.pt", "--conf", "0.1", "--img-size", "640","--view-img", "--no-trace", "--source", f"/home/murad/Belgeler/yolowebapp/static/images/{filename}", "--project", "/home/murad/Belgeler/yolowebapp/static", "--name", "detected"], timeout=600)
                        response['kilo'] = int(detec[-3:-1].decode("utf-8"))*0.125
                        response['count'] = detec[-3:-1].decode("utf-8")
                        response['toplam_ceki'] = int(agac_sayi)*response['kilo']
                        print(response['toplam_ceki'])

                    elif 4 < int(agac_yasi) <= 8:
                        pass
                    elif 8 < int(agac_yasi) <= 30:
                        pass

                elif meyve_qrupu == "elma":
                    detec = predict_tree.preddict(path_to_weights="elma.pt",path_to_source=f"{BASE_DIR}/static/images/{filename}")    #subprocess.check_output(["python", "C:/Users/Murad/Desktop/yolowebapp/polls/yolo/detectcount.py", "--weights", "mandora.pt", "--conf", "0.1", "--img-size", "1280", "--view-img","--no-trace", "--source", f"C:/Users/Murad/Desktop/yolowebapp/static/images/{filename}", "--project", "C:/Users/Murad/Desktop/yolowebapp/static", "--name", "detected"])
                    response['kilo'] = int(detec[-3:-1].decode("utf-8"))*0.105
                    response['count'] = detec[-3:-1].decode("utf-8")
                    response['toplam_ceki'] = int(agac_sayi)*response['kilo']

                elif meyve_qrupu == "armut":
                    detec = predict_tree.preddict(path_to_weights="armut.pt",path_to_source=f"{BASE_DIR}/static/images/{filename}")  #subprocess.check_output(["python", "C:/Users/Murad/Desktop/yolowebapp/polls/yolo/detectcount.py", "--weights", "mandora.pt", "--conf", "0.1", "--img-size", "1280", "--view-img","--no-trace", "--source", f"C:/Users/Murad/Desktop/yolowebapp/static/images/{filename}", "--project", "C:/Users/Murad/Desktop/yolowebapp/static", "--name", "detected"])
                    response['kilo'] = int(detec[-3:-1].decode("utf-8"))*0.220
                    response['count'] = detec[-3:-1].decode("utf-8")
                    response['toplam_ceki'] = int(agac_sayi)*response['kilo']

                elif meyve_qrupu == "seftale":
                    detec = predict_tree.preddict(path_to_weights="seftale.pt",path_to_source=f"{BASE_DIR}/static/images/{filename}")  #subprocess.check_output(["python", "C:/Users/Murad/Desktop/yolowebapp/polls/yolo/detectcount.py", "--weights", "seftali.pt", "--conf", "0.1", "--img-size", "640", "--view-img","--no-trace", "--source", f"C:/Users/Murad/Desktop/yolowebapp/static/images/{filename}", "--project", "C:/Users/Murad/Desktop/yolowebapp/static", "--name", "detected"])
                    response['count'] = detec[-3:-1].decode("utf-8")
                    response['kilo'] = int(detec[-3:-1].decode("utf-8"))*0.185
                    response['toplam_ceki'] = int(agac_sayi)*response['kilo']
                    """
				elif meyve_qrupu == "portakal":				
					detec = subprocess.check_output(["python", "{BASE_DIR}/detection/yolo/detectcount.py","--weights","mandora.pt", "--conf", "0.1","--img-size","1280","--view-img","--no-trace","--source",f"C:/Users/Murad/Desktop/yolowebapp/static/images/{saved_filename}","--project","C:/Users/Murad/Desktop/yolowebapp/static","--name","detected"])
					response['count'] = detec[-4:-1].decode("utf-8")
					response['kilo'] = int(detec[-4:-1].decode("utf-8"))*0.210
					response['toplam_ceki'] = int(agac_sayi)*response['kilo']
					"""
                elif meyve_qrupu == "nar":
                    detec = predict_tree.preddict(path_to_weights="nar.pt",path_to_source=f"{BASE_DIR}/static/images/{filename}")  #subprocess.check_output(["python", "C:/Users/Murad/Desktop/yolowebapp/polls/yolo/detectcount.py", "--weights", "mandora.pt", "--conf", "0.1", "--img-size", "1280", "--view-img","--no-trace", "--source", f"C:/Users/Murad/Desktop/yolowebapp/static/images/{filename}", "--project", "C:/Users/Murad/Desktop/yolowebapp/static", "--name", "detected"])
                    response['count'] = detec[-3:-1].decode("utf-8")
                    response['kilo'] = int(detec[-3:-1].decode("utf-8"))*0.300
                    response['toplam_ceki'] = int(agac_sayi)*response['kilo']

                elif meyve_qrupu == "hurma":
                    detec = predict_tree.preddict(path_to_weights="hurma.pt",path_to_source=f"{BASE_DIR}/static/images/{filename}")  #subprocess.check_output(["python", "C:/Users/Murad/Desktop/yolowebapp/polls/yolo/detectcount.py", "--weights", "mandora.pt", "--conf", "0.1", "--img-size", "1280", "--view-img","--no-trace", "--source", f"C:/Users/Murad/Desktop/yolowebapp/static/images/{filename}", "--project", "C:/Users/Murad/Desktop/yolowebapp/static", "--name", "detected"])
                    response['count'] = detec[-3:-1].decode("utf-8")
                    #response['kilo'] = int(detec[-3:-1].decode("utf-8"))*0.125

                response['time'] = f"{(time.time()-start_time):.2f}"
                response['image'] = f'images/{saved_filename}'
                response['image_detection'] = f'detected/{filename}'
                return render(request, "main.html", {"response": response, "userss": userss})
            else:
                return render(request, "main.html",)
        else:
            return render(request, "main.html", {"userss": userss})
    else:
        return render(request, "login.html",)
    



def multi_detection_image(request):
    if request.user.is_authenticated:
        print(str(BASE_DIR),"BASE_DIRBASE_DIRBASE_DIRBASE_DIR")
        userss = Users.objects.get(kat_id=request.user.id)
        response = {}
        if request.method == 'POST':

            meyve_qrupu = request.POST.get('meyve_qrupu')            
            ekilis_sira = request.POST.get('ekilis_sira')            
            filename = request.FILES.getlist('file')
            print(filename,"Filenamaaaaa")
            
            start_time = time.time()
            agac_sayi = 1
            if meyve_qrupu == "mandalina":

                hass = hashing.add_prefix2(filename=f"{time.time()}") 
                fs = FileSystemStorage(location=str(hass[0])) 
                for image in filename:                    
                    saved_filename = fs.save(image.name, image)         
                    
                detec = predict_tree.multi_predictor(path_to_weights="mandalina.pt",path_to_source=hass[0],ekilis_sira=ekilis_sira,hashing=hass[1])
                #detec = subprocess.check_output(["/home/murad/Belgeler/myprojectenv/bin/python","/home/murad/Belgeler/yolowebapp/polls/yolo/detectcount.py", "--weights", "mandalina.pt", "--conf", "0.1", "--img-size", "640","--view-img", "--no-trace", "--source", f"/home/murad/Belgeler/yolowebapp/static/images/{filename}", "--project", "/home/murad/Belgeler/yolowebapp/static", "--name", "detected"], timeout=600)
                #response['kilo'] = int(detec[-3:-1].decode("utf-8"))*0.125
                #response['count'] = detec[-3:-1].decode("utf-8")
                #response['toplam_ceki'] = int(agac_sayi)*response['kilo']
                #print(detec,"detectiooooooooooooommnnnn")

               

            elif meyve_qrupu == "elma":
                detec = predict_tree.multi_predictor(path_to_weights="elma.pt",path_to_source=f"{BASE_DIR}/static/images/{filename}")    #subprocess.check_output(["python", "C:/Users/Murad/Desktop/yolowebapp/polls/yolo/detectcount.py", "--weights", "mandora.pt", "--conf", "0.1", "--img-size", "1280", "--view-img","--no-trace", "--source", f"C:/Users/Murad/Desktop/yolowebapp/static/images/{filename}", "--project", "C:/Users/Murad/Desktop/yolowebapp/static", "--name", "detected"])
                response['kilo'] = int(detec[-3:-1].decode("utf-8"))*0.105
                response['count'] = detec[-3:-1].decode("utf-8")
                response['toplam_ceki'] = int(agac_sayi)*response['kilo']

            elif meyve_qrupu == "armut":
                detec = predict_tree.multi_predictor(path_to_weights="armut.pt",path_to_source=f"{BASE_DIR}/static/images/{filename}")  #subprocess.check_output(["python", "C:/Users/Murad/Desktop/yolowebapp/polls/yolo/detectcount.py", "--weights", "mandora.pt", "--conf", "0.1", "--img-size", "1280", "--view-img","--no-trace", "--source", f"C:/Users/Murad/Desktop/yolowebapp/static/images/{filename}", "--project", "C:/Users/Murad/Desktop/yolowebapp/static", "--name", "detected"])
                response['kilo'] = int(detec[-3:-1].decode("utf-8"))*0.220
                response['count'] = detec[-3:-1].decode("utf-8")
                response['toplam_ceki'] = int(agac_sayi)*response['kilo']

            elif meyve_qrupu == "seftale":
                detec = predict_tree.multi_predictor(path_to_weights="seftale.pt",path_to_source=f"{BASE_DIR}/static/images/{filename}")  #subprocess.check_output(["python", "C:/Users/Murad/Desktop/yolowebapp/polls/yolo/detectcount.py", "--weights", "seftali.pt", "--conf", "0.1", "--img-size", "640", "--view-img","--no-trace", "--source", f"C:/Users/Murad/Desktop/yolowebapp/static/images/{filename}", "--project", "C:/Users/Murad/Desktop/yolowebapp/static", "--name", "detected"])
                response['count'] = detec[-3:-1].decode("utf-8")
                response['kilo'] = int(detec[-3:-1].decode("utf-8"))*0.185
                response['toplam_ceki'] = int(agac_sayi)*response['kilo']
                """
            elif meyve_qrupu == "portakal":				
                detec = subprocess.check_output(["python", "{BASE_DIR}/polls/yolo/detectcount.py","--weights","mandora.pt", "--conf", "0.1","--img-size","1280","--view-img","--no-trace","--source",f"C:/Users/Murad/Desktop/yolowebapp/static/images/{saved_filename}","--project","C:/Users/Murad/Desktop/yolowebapp/static","--name","detected"])
                response['count'] = detec[-4:-1].decode("utf-8")
                response['kilo'] = int(detec[-4:-1].decode("utf-8"))*0.210
                response['toplam_ceki'] = int(agac_sayi)*response['kilo']
                """
            elif meyve_qrupu == "nar":
                detec = predict_tree.multi_predictor(path_to_weights="nar.pt",path_to_source=f"{BASE_DIR}/static/images/{filename}")  #subprocess.check_output(["python", "C:/Users/Murad/Desktop/yolowebapp/polls/yolo/detectcount.py", "--weights", "mandora.pt", "--conf", "0.1", "--img-size", "1280", "--view-img","--no-trace", "--source", f"C:/Users/Murad/Desktop/yolowebapp/static/images/{filename}", "--project", "C:/Users/Murad/Desktop/yolowebapp/static", "--name", "detected"])
                response['count'] = detec[-3:-1].decode("utf-8")
                response['kilo'] = int(detec[-3:-1].decode("utf-8"))*0.300
                response['toplam_ceki'] = int(agac_sayi)*response['kilo']

            elif meyve_qrupu == "hurma":
                detec = predict_tree.multi_predictor(path_to_weights="hurma.pt",path_to_source=f"{BASE_DIR}/static/images/{filename}")  #subprocess.check_output(["python", "C:/Users/Murad/Desktop/yolowebapp/polls/yolo/detectcount.py", "--weights", "mandora.pt", "--conf", "0.1", "--img-size", "1280", "--view-img","--no-trace", "--source", f"C:/Users/Murad/Desktop/yolowebapp/static/images/{filename}", "--project", "C:/Users/Murad/Desktop/yolowebapp/static", "--name", "detected"])
                response['count'] = detec[-3:-1].decode("utf-8")
                #response['kilo'] = int(detec[-3:-1].decode("utf-8"))*0.125

            #response['time'] = f"{(time.time()-start_time):.2f}"
            #response['image'] = f'images/{saved_filename}'
            #response['image_detection'] = f'detected/{filename}'
            return render(request, "multi_detection_fruit.html", {"response": hass[1], "userss": userss})
            
        else:
            return render(request, "multi_detection_fruit.html", {"userss": userss})
    else:
        return render(request, "login.html",)
    


def leaf_detection_image(request):
    if request.user.is_authenticated:
        response = {}
        print(str(BASE_DIR),"BASE_DIRBASE_DIRBASE_DIRBASE_DIR")
        userss = Users.objects.get(kat_id=request.user.id)       
        if request.method == 'POST':

            filename = request.FILES.get('file')                       
            fs = FileSystemStorage(location=str(BASE_DIR)+"/static/images/")
            saved_filename = fs.save(str(filename.name).lower(), filename)         
            
            leaf_detection_disease = leaf_detection.leaf_disease_detection(img_path=f"{BASE_DIR}/static/images/{saved_filename}")
            response['image'] = f'images/{saved_filename}'
            if leaf_detection_disease.get('recommendations') == 'Not recommendation':                     
                response['image_detection'] = f'images/{saved_filename}'
            else:
                response['image_detection'] = f'detected/{saved_filename}'
            return render(request, "leaf_detection.html", {"leaf_detection": leaf_detection_disease, "userss": userss, "response": response})
        else:
            return render(request, "leaf_detection.html", {"userss": userss})
    else:
        return render(request, "login.html",)




def download_image(request, slug):
    print(slug,"sluggggggggggggggggg")
    return FileResponse(open(f"{BASE_DIR}/media/{slug}_result.zip", 'rb'), as_attachment=True)