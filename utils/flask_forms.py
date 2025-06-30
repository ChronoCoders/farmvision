from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SelectField, FloatField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from wtforms.widgets import TextArea

class ProjectForm(FlaskForm):
    """
    Flask adaptation of Django Projects_Form
    """
    title = StringField('Proje Başlığı', 
                       validators=[DataRequired(), Length(min=2, max=200)])
    
    description = TextAreaField('Açıklama', 
                               validators=[Optional(), Length(max=1000)],
                               widget=TextArea())
    
    farm_name = StringField('Çiftlik Adı', 
                           validators=[Optional(), Length(max=100)])
    
    field_name = StringField('Tarla Adı', 
                            validators=[Optional(), Length(max=100)])
    
    location = StringField('Konum', 
                          validators=[Optional(), Length(max=200)])
    
    submit = SubmitField('Proje Oluştur')

class FruitDetectionForm(FlaskForm):
    """
    Advanced fruit detection form
    """
    image = FileField('Meyve Görüntüsü', 
                     validators=[FileRequired(), 
                               FileAllowed(['jpg', 'jpeg', 'png'], 'Sadece JPG, JPEG ve PNG dosyaları!')])
    
    fruit_type = SelectField('Meyve Türü',
                            choices=[
                                ('elma', '🍎 Elma'),
                                ('armut', '🍐 Armut'),
                                ('portakal', '🍊 Portakal'),
                                ('mandalina', '🍊 Mandalina'),
                                ('seftali', '🍑 Şeftali'),
                                ('nar', '🍅 Nar'),
                                ('limon', '🍋 Limon'),
                                ('mixed', '🍇 Karışık')
                            ],
                            default='mixed')
    
    confidence = FloatField('Güven Eşiği (%)',
                           validators=[NumberRange(min=10, max=95)],
                           default=25)
    
    project_id = SelectField('Proje (Opsiyonel)',
                            choices=[],
                            validators=[Optional()],
                            coerce=int)
    
    submit = SubmitField('Tespit Başlat')

class MultiDetectionForm(FlaskForm):
    """
    Advanced multi-fruit detection form
    """
    image = FileField('Çoklu Meyve Görüntüsü',
                     validators=[FileRequired(),
                               FileAllowed(['jpg', 'jpeg', 'png'], 'Sadece JPG, JPEG ve PNG dosyaları!')])
    
    detection_mode = SelectField('Tespit Modu',
                                choices=[
                                    ('all', 'Tüm Meyveler'),
                                    ('citrus', 'Narenciye Grubu'),
                                    ('tree_fruits', 'Ağaç Meyveleri'),
                                    ('custom', 'Özel Seçim')
                                ],
                                default='all')
    
    confidence = FloatField('Güven Eşiği (%)',
                           validators=[NumberRange(min=10, max=95)],
                           default=25)
    
    iou_threshold = FloatField('IoU Eşiği',
                              validators=[NumberRange(min=0.3, max=0.9)],
                              default=0.7)
    
    model_version = SelectField('Model Versiyonu',
                               choices=[
                                   ('yolov7', 'YOLO v7 (Varsayılan)'),
                                   ('yolov7x', 'YOLO v7x (Yüksek Doğruluk)'),
                                   ('yolov7-tiny', 'YOLO v7-Tiny (Hızlı)')
                               ],
                               default='yolov7')
    
    project_id = SelectField('Proje (Opsiyonel)',
                            choices=[],
                            validators=[Optional()],
                            coerce=int)
    
    submit = SubmitField('Çoklu Tespit Başlat')

class LeafDiseaseForm(FlaskForm):
    """
    Leaf disease detection form
    """
    image = FileField('Yaprak Görüntüsü',
                     validators=[FileRequired(),
                               FileAllowed(['jpg', 'jpeg', 'png'], 'Sadece JPG, JPEG ve PNG dosyaları!')])
    
    crop_type = SelectField('Ürün Türü',
                           choices=[
                               ('corn', '🌽 Mısır'),
                               ('wheat', '🌾 Buğday'),
                               ('potato', '🥔 Patates'),
                               ('tomato', '🍅 Domates'),
                               ('general', '🌱 Genel')
                           ],
                           default='corn')
    
    confidence = FloatField('Güven Eşiği (%)',
                           validators=[NumberRange(min=10, max=95)],
                           default=25)
    
    project_id = SelectField('Proje (Opsiyonel)',
                            choices=[],
                            validators=[Optional()],
                            coerce=int)
    
    submit = SubmitField('Hastalık Tespiti Başlat')

class TreeDetectionForm(FlaskForm):
    """
    Tree detection from drone imagery form
    """
    image = FileField('Drone/Hava Görüntüsü',
                     validators=[FileRequired(),
                               FileAllowed(['jpg', 'jpeg', 'png', 'tif', 'tiff'], 
                                         'JPG, PNG veya TIFF dosyaları!')])
    
    confidence = FloatField('Güven Eşiği (%)',
                           validators=[NumberRange(min=10, max=95)],
                           default=25)
    
    iou_threshold = FloatField('IoU Eşiği',
                              validators=[NumberRange(min=0.3, max=0.9)],
                              default=0.7)
    
    project_id = SelectField('Proje (Opsiyonel)',
                            choices=[],
                            validators=[Optional()],
                            coerce=int)
    
    submit = SubmitField('Ağaç Tespiti Başlat')

class VegetationAnalysisForm(FlaskForm):
    """
    Vegetation analysis form with 15+ algorithms
    """
    image = FileField('GeoTIFF/Multispektral Görüntü',
                     validators=[FileRequired(),
                               FileAllowed(['tif', 'tiff', 'jpg', 'jpeg', 'png'], 
                                         'GeoTIFF, JPG veya PNG dosyaları!')])
    
    algorithm = SelectField('Analiz Algoritması',
                           choices=[
                               ('ndvi', 'NDVI - Normalized Difference Vegetation Index'),
                               ('gli', 'GLI - Green Leaf Index'),
                               ('vari', 'VARI - Visible Atmospherically Resistant Index'),
                               ('ndwi', 'NDWI - Normalized Difference Water Index'),
                               ('savi', 'SAVI - Soil Adjusted Vegetation Index'),
                               ('evi', 'EVI - Enhanced Vegetation Index'),
                               ('tgi', 'TGI - Triangular Greenness Index'),
                               ('msavi', 'MSAVI - Modified SAVI'),
                               ('osavi', 'OSAVI - Optimized SAVI'),
                               ('rdvi', 'RDVI - Renormalized Difference VI'),
                               ('gndvi', 'GNDVI - Green NDVI'),
                               ('cvi', 'CVI - Chlorophyll Vegetation Index'),
                               ('arvi', 'ARVI - Atmospherically Resistant VI'),
                               ('gci', 'GCI - Green Coverage Index')
                           ],
                           default='ndvi')
    
    colormap = SelectField('Renk Haritası',
                          choices=[
                              ('rdylgn', 'Kırmızı-Sarı-Yeşil'),
                              ('viridis', 'Viridis'),
                              ('plasma', 'Plasma'),
                              ('inferno', 'Inferno'),
                              ('magma', 'Magma'),
                              ('coolwarm', 'Soğuk-Sıcak'),
                              ('spectral', 'Spektral')
                          ],
                          default='rdylgn')
    
    min_range = FloatField('Minimum Değer',
                          validators=[Optional(), NumberRange(min=-1, max=1)],
                          default=-1)
    
    max_range = FloatField('Maksimum Değer',
                          validators=[Optional(), NumberRange(min=-1, max=1)],
                          default=1)
    
    project_id = SelectField('Proje (Opsiyonel)',
                            choices=[],
                            validators=[Optional()],
                            coerce=int)
    
    submit = SubmitField('Vegetation Analizi Başlat')

class GeoTIFFUploadForm(FlaskForm):
    """
    GeoTIFF file upload and processing form
    """
    geotiff_file = FileField('GeoTIFF Dosyası',
                           validators=[FileRequired(),
                                     FileAllowed(['tif', 'tiff'], 'Sadece GeoTIFF dosyaları!')])
    
    process_type = SelectField('İşlem Türü',
                              choices=[
                                  ('histogram', 'Histogram Analizi'),
                                  ('rgb_extract', 'RGB Çıkarma'),
                                  ('vegetation', 'Vegetation Analizi'),
                                  ('statistics', 'İstatistiksel Analiz')
                              ],
                              default='histogram')
    
    bins = IntegerField('Histogram Bin Sayısı',
                       validators=[NumberRange(min=16, max=1024)],
                       default=256)
    
    submit = SubmitField('GeoTIFF İşle')

def populate_project_choices(form, user_id):
    """
    Helper function to populate project choices for forms
    """
    from models import Project
    
    projects = Project.query.filter_by(user_id=user_id).all()
    choices = [('', 'Proje Seçin')]
    choices.extend([(p.id, p.title) for p in projects])
    
    # Update form choices
    if hasattr(form, 'project_id'):
        form.project_id.choices = choices
    
    return choices