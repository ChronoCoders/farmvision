import torch
import torch.nn as nn
import numpy as np
from pathlib import Path

# YOLO Model Components from uploaded experimental.py and common.py files

class CrossConv(nn.Module):
    """Cross Convolution Downsample"""
    def __init__(self, c1, c2, k=3, s=1, g=1, e=1.0, shortcut=False):
        super(CrossConv, self).__init__()
        c_ = int(c2 * e)  # hidden channels
        self.cv1 = Conv(c1, c_, (1, k), (1, s))
        self.cv2 = Conv(c_, c2, (k, 1), (s, 1), g=g)
        self.add = shortcut and c1 == c2

    def forward(self, x):
        return x + self.cv2(self.cv1(x)) if self.add else self.cv2(self.cv1(x))

class Sum(nn.Module):
    """Weighted sum of 2 or more layers"""
    def __init__(self, n, weight=False):
        super(Sum, self).__init__()
        self.weight = weight
        self.iter = range(n - 1)
        if weight:
            self.w = nn.Parameter(-torch.arange(1., n) / 2, requires_grad=True)

    def forward(self, x):
        y = x[0]
        if self.weight:
            w = torch.sigmoid(self.w) * 2
            for i in self.iter:
                y = y + x[i + 1] * w[i]
        else:
            for i in self.iter:
                y = y + x[i + 1]
        return y

class Conv(nn.Module):
    """Standard convolution"""
    def __init__(self, c1, c2, k=1, s=1, p=None, g=1, act=True):
        super(Conv, self).__init__()
        self.conv = nn.Conv2d(c1, c2, k, s, autopad(k, p), groups=g, bias=False)
        self.bn = nn.BatchNorm2d(c2)
        self.act = SiLU() if act is True else (act if isinstance(act, nn.Module) else nn.Identity())

    def forward(self, x):
        return self.act(self.bn(self.conv(x)))

    def fuseforward(self, x):
        return self.act(self.conv(x))

class SiLU(nn.Module):
    """SiLU activation function"""
    @staticmethod
    def forward(x):
        return x * torch.sigmoid(x)

class Hardswish(nn.Module):
    """Hard-SiLU activation function"""
    @staticmethod
    def forward(x):
        return x * torch.nn.functional.hardtanh(x + 3, 0., 6.) / 6.

def autopad(k, p=None):
    """Pad to 'same'"""
    if p is None:
        p = k // 2 if isinstance(k, int) else [x // 2 for x in k]
    return p

class YOLOModelConfig:
    """YOLO Model Configuration Manager"""
    
    def __init__(self):
        self.model_configs = {
            'yolov7': {
                'config_path': 'detection_models/configs/yolov7_1751323775733.yaml',
                'input_size': 640,
                'num_classes': 80,
                'anchors': [
                    [12,16, 19,36, 40,28],
                    [36,75, 76,55, 72,146], 
                    [142,110, 192,243, 459,401]
                ]
            },
            'yolov7x': {
                'config_path': 'detection_models/configs/yolov7x_1751323775737.yaml',
                'input_size': 640,
                'num_classes': 80,
                'anchors': [
                    [12,16, 19,36, 40,28],
                    [36,75, 76,55, 72,146],
                    [142,110, 192,243, 459,401]
                ]
            },
            'yolov7-tiny': {
                'config_path': 'detection_models/configs/yolov7-tiny_1751323775736.yaml', 
                'input_size': 416,
                'num_classes': 80,
                'anchors': [
                    [10,13, 16,30, 33,23],
                    [30,61, 62,45, 59,119],
                    [116,90, 156,198, 373,326]
                ]
            }
        }
        
        self.fruit_classes = {
            0: 'elma',
            1: 'armut', 
            2: 'portakal',
            3: 'mandalina',
            4: 'seftali',
            5: 'nar',
            6: 'limon',
            7: 'hurma'
        }
        
        self.disease_classes = {
            0: 'Corn maize healthy',
            1: 'Cercospora Leaf Spot Gray Leaf Spot',
            2: 'Corn maize Northern Leaf Blight',
            3: 'Corn maize Common rust'
        }
        
        self.tree_classes = {
            0: 'tree'
        }

    def get_model_config(self, model_name):
        """Get model configuration"""
        return self.model_configs.get(model_name, self.model_configs['yolov7'])
    
    def get_fruit_weight(self, fruit_class):
        """Get fruit weight coefficient (kg)"""
        weights = {
            'elma': 0.105,
            'armut': 0.220,
            'portakal': 0.180,
            'mandalina': 0.125,
            'seftali': 0.185,
            'nar': 0.300,
            'limon': 0.060,
            'hurma': 0.010  # Türkiye hurması: 8-12 gram ortalama
        }
        return weights.get(fruit_class, 0.1)

class DetectionPostProcessor:
    """Advanced detection post-processing from uploaded files"""
    
    def __init__(self, conf_thresh=0.25, iou_thresh=0.45):
        self.conf_thresh = conf_thresh
        self.iou_thresh = iou_thresh
    
    def non_max_suppression(self, predictions, conf_thresh=None, iou_thresh=None):
        """Apply Non-Maximum Suppression"""
        if conf_thresh is None:
            conf_thresh = self.conf_thresh
        if iou_thresh is None:
            iou_thresh = self.iou_thresh
            
        # Mock NMS implementation - in real deployment would use actual YOLO NMS
        filtered_predictions = []
        
        for pred in predictions:
            if pred['confidence'] >= conf_thresh:
                filtered_predictions.append(pred)
        
        # Simple IoU-based filtering simulation
        final_predictions = []
        for pred in filtered_predictions:
            is_duplicate = False
            for final_pred in final_predictions:
                iou = self.calculate_iou(pred['bbox'], final_pred['bbox'])
                if iou > iou_thresh:
                    is_duplicate = True
                    # Keep the one with higher confidence
                    if pred['confidence'] > final_pred['confidence']:
                        final_predictions.remove(final_pred)
                        final_predictions.append(pred)
                    break
            
            if not is_duplicate:
                final_predictions.append(pred)
        
        return final_predictions
    
    def calculate_iou(self, box1, box2):
        """Calculate Intersection over Union"""
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        
        # Calculate intersection area
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i <= x1_i or y2_i <= y1_i:
            return 0.0
        
        intersection_area = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Calculate union area
        box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
        box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
        union_area = box1_area + box2_area - intersection_area
        
        return intersection_area / union_area if union_area > 0 else 0.0

    def count_objects_in_region(self, detections, region_coords=None):
        """Count objects in specific region from uploaded counting algorithms"""
        if region_coords is None:
            return len(detections)
        
        x_min, y_min, x_max, y_max = region_coords
        count = 0
        
        for detection in detections:
            bbox = detection['bbox']
            center_x = (bbox[0] + bbox[2]) / 2
            center_y = (bbox[1] + bbox[3]) / 2
            
            if x_min <= center_x <= x_max and y_min <= center_y <= y_max:
                count += 1
        
        return count

class ModelEnsemble:
    """Ensemble of multiple YOLO models for improved accuracy"""
    
    def __init__(self, models=None):
        self.models = models or ['yolov7', 'yolov7x']
        self.config_manager = YOLOModelConfig()
        self.post_processor = DetectionPostProcessor()
    
    def ensemble_predict(self, image_path, confidence=0.25):
        """Run ensemble prediction with multiple models"""
        all_predictions = []
        
        for model_name in self.models:
            config = self.config_manager.get_model_config(model_name)
            
            # Mock prediction for each model
            predictions = self.mock_model_predict(image_path, model_name, confidence)
            all_predictions.extend(predictions)
        
        # Apply ensemble NMS
        final_predictions = self.post_processor.non_max_suppression(
            all_predictions, conf_thresh=confidence
        )
        
        return final_predictions
    
    def mock_model_predict(self, image_path, model_name, confidence):
        """Mock model prediction - replace with actual model inference"""
        # Simulate different model behaviors
        base_detections = np.random.randint(3, 12)
        
        if model_name == 'yolov7x':
            # More accurate but slower
            confidence_boost = 0.1
            detection_boost = 1.2
        elif model_name == 'yolov7-tiny':
            # Faster but less accurate  
            confidence_boost = -0.05
            detection_boost = 0.8
        else:
            # Standard yolov7
            confidence_boost = 0.0
            detection_boost = 1.0
        
        detections = []
        num_detections = int(base_detections * detection_boost)
        
        for i in range(num_detections):
            detection = {
                'class': np.random.randint(0, 7),  # Fruit classes
                'confidence': min(0.95, confidence + np.random.uniform(0, 0.4) + confidence_boost),
                'bbox': [
                    np.random.randint(50, 400),
                    np.random.randint(50, 400), 
                    np.random.randint(500, 600),
                    np.random.randint(500, 600)
                ],
                'model': model_name
            }
            detections.append(detection)
        
        return detections