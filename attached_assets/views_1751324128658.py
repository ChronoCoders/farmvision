from django.shortcuts import render
from pathlib import Path
from yolowebapp2 import histogram as hs
import os,json,subprocess
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from .forms import  Projects_Form #UserForm, UsersForm,
from .models import Users, Projects
from django.shortcuts import get_object_or_404
from yolowebapp2 import predict_tree,hashing,tasknode,options
BASE_DIR = Path(__file__).resolve().parent.parent
from asgiref.sync import sync_to_async
import asyncio
import os
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"



def projects(request):
    if request.user.is_authenticated:
        userss = Users.objects.get(kat_id=request.user.id)
        projes = Projects.objects.filter(kat_user__kat_id=request.user.id)
        
        return render(request, "projects.html", {"userss": userss, "projes": projes})
    else:
        return render(request, "login.html",)
    




def add_projects(request, slug=None, id=None):
    if request.user.is_authenticated:
        url = get_object_or_404(Users, kat_id=request.user.id)

        if slug == "update" and id is not None:
            projes = Projects.objects.get(id=id)
            if request.method == 'POST':
                form = Projects_Form(request.POST or None,
                                     request.FILES or None, instance=projes)
                
                if form.is_valid():
                    form.picture = form.cleaned_data['picture']
                    
                    form.save()
                return render(request, "add-projects.html", {'userss': url, "projes": projes})
            else:
                return render(request, "add-projects.html", {'userss': url, "projes": projes})

        elif slug == "delete" and id is not None:
            projes = Projects.objects.get(id=id).delete()
            return redirect("dron_map:projects",)

        elif slug == "add" and id is None:
            if request.method == 'POST':
                form = Projects_Form(request.POST or None,request.FILES or None)
                Title= request.POST.get('Title')
                Field= request.POST.get('Field')
                
                if form.is_valid():
                    
                    hass = hashing.add_prefix(filename=f"{Title}{Field}")
                    
                                 
                    images_lists = request.FILES.getlist('picture') 
                    form.picture = form.cleaned_data['picture']                    
                    #form.hashing_path = f"{BASE_DIR}/static/results/{hass[1]}"
                    form.instance.hashing_path = f"{hass[1]}"                  
                    form.save()                
                    for image in images_lists:                        
                        fs = FileSystemStorage(location=str(hass[0]))                        
                        saved_filename = fs.save(image.name, image)
                    p = tasknode.Node_processing(f"{hass[0]}")
                    p.download_task(f"{BASE_DIR}/static/results/{hass[1]}")
                    
                return render(request, "add-projects.html", {'userss': url, })
            else:
                return render(request, "add-projects.html", {'userss': url },)

    else:
        return render(request, "login.html",)

def task_path( id,path,file):        
    return f'results/{id}/{path}/{file}'

def get_full_task_path(id,path,file):
    return os.path.join(BASE_DIR, f'static/results/{id}/{path}',file)

def get_statistics(id,type):       

    if type == "static":
        task = get_full_task_path(id,"odm_report", "stats.json")
        
        if os.path.isfile(task):
            try:
                with open(task) as f:
                    j = json.loads(f.read())
            except Exception as e:                
                return str(e)
            return {'gsd': j.get('odm_processing_statistics', {}).get('average_gsd'),
                    'area': j.get('processing_statistics', {}).get('area'),
                    'date': j.get('processing_statistics', {}).get('date'),
                    'end_date': j.get('processing_statistics', {}).get('end_date'),}
        else:
            return {}

    elif type == "orthophoto" or type == "plant":
        task = task_path(id,"odm_orthophoto", "odm_orthophoto.tif")
        return {"odm_orthophoto":task}

    elif type == "dsm" :
        task = task_path(id,"odm_dem", "dsm.tif")
        return {"dsm":task}

    elif type == "dtm" :
        task = task_path(id,"odm_dem", "dtm.tif")
        return {"dtm":task}


    elif type == "camera_shots":
        task = task_path(id,"odm_report", "shots.geojson")
        if os.path.isfile(task):
            try:
                with open(task) as f:
                    j = json.loads(f.read())
            except Exception as e:                
                return str(e)
            return {"camera_shots":j}
        else:
            return {}

            
    elif type == "images_info":
        task = get_full_task_path(id,'/', 'images.json')
       
        if os.path.exists(task):
            try:
                with open(task) as f:
                    j = json.loads(f.read())
            except Exception as e:                
                return str(e)
            return {'camera_model': j[0].get('camera_model'),
                    'altitude':j[0].get('altitude'),
            }
        else:
            return {}
        


def convert(input_path,output_path):
    from osgeo import gdal
    dataset1 = gdal.Open(input_path)
    projection = dataset1.GetProjection()
    geotransform = dataset1.GetGeoTransform()


    dataset2 = gdal.Open(output_path, gdal.GA_Update)
    dataset2.SetGeoTransform( geotransform )
    dataset2.SetProjection( projection )
    dataset2.GetRasterBand(1).SetNoDataValue(0)


def maping(request, id):
    if request.user.is_authenticated:
        userss = Users.objects.get(kat_id=request.user.id)
        projes = Projects.objects.get(id=id)
        algo = options.algorithm
        colors = options.colormaps
        if request.method == 'POST':
            
            orthophoto = get_statistics(id= projes.hashing_path,type="orthophoto")
            static = get_statistics(id= projes.hashing_path,type="static")
            images_info = get_statistics(id= projes.hashing_path,type="images_info")     
            post_range = tuple(map(float,request.POST.getlist('range')))
            post_range = (-abs(post_range[0]),abs(post_range[1]))
            health_color = request.POST.get('health_color')
            cmap = request.POST.get('cmap')

            selected_algo = algo[health_color]
            selected_colormap = colors[cmap]

            

            if health_color == "detect":
                image_path = os.path.split(f'{BASE_DIR}/static/{projes.picture}')[-1]
                image_path2 = f'detected/{image_path}'               
                #detec = predict_tree.tree_detection(img_path=f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}') 
                detec = predict_tree.preddict(path_to_weights="agac.pt",path_to_source=f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}') #subprocess.check_output(["python", path, "--weights", path_to_weights, "--conf", "0.1", "--img-size", "640","--view-img", "--no-trace", "--source", f'C:/Users/Murad/Documents/yolowebapp2/static/{projes.picture}', "--project", path_to_project, "--name", "detected"], timeout=600)

                convert(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',f'{BASE_DIR}/static/detected/odm_orthophoto.tif')               
                return render(request, "map.html", {"userss": userss, "orthophoto": {'path': f"detected/odm_orthophoto.tif",'colormap':cmap,'ranges':post_range,},"algo":algo,"colors":colors, "static":static,"images_info":images_info,"detection": detec[-5:-1].decode("utf-8")})

            elif health_color == "ndvi":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                ndvi = a.Ndvi(post_range,cmap)                      
                return render(request, "map.html", {"userss": userss, "orthophoto": ndvi,"algo":algo,"colors":colors, "static":static,"images_info":images_info})

            elif health_color == "gli":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                gli = a.Gli(post_range,cmap)
                return render(request, "map.html", {"userss": userss, "orthophoto": gli,"algo":algo,"colors":colors, "static":static,"images_info":images_info})

            elif health_color == "vari":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                vari = a.Vari(post_range,cmap)
                return render(request, "map.html", {"userss": userss, "orthophoto": vari,"algo":algo,"colors":colors, "static":static,"images_info":images_info})

            elif health_color == "vndvi":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                vndvi = a.VNDVI(post_range,cmap)
                return render(request, "map.html", {"userss": userss, "orthophoto": vndvi,"algo":algo,"colors":colors, "static":static,"images_info":images_info})
            
            elif health_color == "ndyi":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                ndyi = a.NDYI(post_range,cmap)
                return render(request, "map.html", {"userss": userss, "orthophoto": ndyi,"algo":algo,"colors":colors, "static":static,"images_info":images_info})
            
            elif health_color == "ndre":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                ndre = a.NDRE(post_range,cmap)
                return render(request, "map.html", {"userss": userss, "orthophoto": ndre,"algo":algo,"colors":colors, "static":static,"images_info":images_info})
            
            
            elif health_color == "ndwi":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                ndwi = a.NDWI(post_range,cmap)
                return render(request, "map.html", {"userss": userss, "orthophoto": ndwi,"algo":algo,"colors":colors, "static":static,"images_info":images_info})
            
            
            elif health_color == "ndvi_blue":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                ndvi_blue = a.NDVI_Blue(post_range,cmap)
                return render(request, "map.html", {"userss": userss, "orthophoto": ndvi_blue,"algo":algo,"colors":colors, "static":static,"images_info":images_info})
            
            
            elif health_color == "endvi":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                ENDVI = a.ENDVI(post_range,cmap)
                return render(request, "map.html", {"userss": userss, "orthophoto": ENDVI,"algo":algo,"colors":colors, "static":static,"images_info":images_info})
            
            
            elif health_color == "vndvi":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                VNDVI = a.VNDVI(post_range,cmap)
                return render(request, "map.html", {"userss": userss, "orthophoto": VNDVI,"algo":algo,"colors":colors, "static":static,"images_info":images_info})
            
            
            elif health_color == "mpri":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                MPRI = a.MPRI(post_range,cmap)
                return render(request, "map.html", {"userss": userss, "orthophoto": MPRI,"algo":algo,"colors":colors, "static":static,"images_info":images_info})
            
            
            elif health_color == "exg":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                EXG = a.EXG(post_range,cmap)
                return render(request, "map.html", {"userss": userss, "orthophoto": EXG,"algo":algo,"colors":colors, "static":static,"images_info":images_info})
            
            elif health_color == "tgi":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                TGI = a.TGI(post_range,cmap)
                return render(request, "map.html", {"userss": userss, "orthophoto": TGI,"algo":algo,"colors":colors, "static":static,"images_info":images_info})
            
            elif health_color == "bai":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                BAI = a.BAI(post_range,cmap)
                return render(request, "map.html", {"userss": userss, "orthophoto": BAI,"algo":algo,"colors":colors, "static":static,"images_info":images_info})
            
            
            elif health_color == "gndvi":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                GNDVI = a.GNDVI(post_range,cmap)
                return render(request, "map.html", {"userss": userss, "orthophoto": GNDVI,"algo":algo,"colors":colors, "static":static,"images_info":images_info})
            
            
            elif health_color == "grvi":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                GRVI = a.GRVI(post_range,cmap)
                return render(request, "map.html", {"userss": userss, "orthophoto": GRVI,"algo":algo,"colors":colors, "static":static,"images_info":images_info})
            
            elif health_color == "savi":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                SAVI = a.SAVI(post_range,cmap)
                return render(request, "map.html", {"userss": userss, "orthophoto": SAVI,"algo":algo,"colors":colors, "static":static,"images_info":images_info})
            
            
            elif health_color == "mnli":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                MNLI = a.MNLI(post_range,cmap)
                return render(request, "map.html", {"userss": userss, "orthophoto": MNLI,"algo":algo,"colors":colors, "static":static,"images_info":images_info})
            
            
            elif health_color == "msr":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                MSR = a.MSR(post_range,cmap)
                return render(request, "map.html", {"userss": userss, "orthophoto": MSR,"algo":algo,"colors":colors, "static":static,"images_info":images_info})
            
            
            
            elif health_color == "rdvi":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                RDVI = a.RDVI(post_range,cmap)
                return render(request, "map.html", {"userss": userss, "orthophoto": RDVI,"algo":algo,"colors":colors, "static":static,"images_info":images_info})
            
            
            elif health_color == "tdvi":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                TDVI = a.TDVI(post_range,cmap)
                return render(request, "map.html", {"userss": userss, "orthophoto": TDVI,"algo":algo,"colors":colors, "static":static,"images_info":images_info})
            
            
            elif health_color == "osavi":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                OSAVI = a.OSAVI(post_range,cmap)
                return render(request, "map.html", {"userss": userss, "orthophoto": OSAVI,"algo":algo,"colors":colors, "static":static,"images_info":images_info})
            
            
            elif health_color == "lai":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                LAI = a.LAI(post_range,cmap)
                return render(request, "map.html", {"userss": userss, "orthophoto": LAI,"algo":algo,"colors":colors, "static":static,"images_info":images_info})
            
            elif health_color == "evi":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                EVI = a.EVI(post_range,cmap)
                return render(request, "map.html", {"userss": userss, "orthophoto": EVI,"algo":algo,"colors":colors, "static":static,"images_info":images_info})
            
            elif health_color == "arvi":
                a = hs.algos(f'{BASE_DIR}/static/{orthophoto["odm_orthophoto"]}',projes.hashing_path)
                ARVI = a.ARVI(post_range,cmap)
                return render(request, "map.html", {"userss": userss, "orthophoto": ARVI,"algo":algo,"colors":colors, "static":static,"images_info":images_info})
            
            
           
        else:
            orthophoto = get_statistics(id= projes.hashing_path,type="orthophoto")
            static = get_statistics(id= projes.hashing_path,type="static")
            images_info = get_statistics(id= projes.hashing_path,type="images_info")
           
            return render(request, "map.html", {"userss": userss, "projes": projes,"orthophoto":orthophoto,"algo":algo,"colors":colors,"static":static,"images_info":images_info})

    else:
        return render(request, "login.html",)
