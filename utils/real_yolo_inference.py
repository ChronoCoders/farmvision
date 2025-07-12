import torch
import cv2
import numpy as np
import time
from pathlib import Path
import logging
from PIL import Image

class YOLOInference:
    """Real YOLO inference engine for fruit detection"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.models = {}
        self.max_batch_size = 1  # Limit batch size for memory
        self.class_names = {
            'fruit': ['elma', 'armut', 'portakal', 'mandalina', 'seftali', 'nar', 'limon', 'hurma'],
            'disease': ['Corn maize healthy', 'Cercospora Leaf Spot Gray Leaf Spot', 
                       'Corn maize Northern Leaf Blight', 'Corn maize Common rust'],
            'tree': ['tree']
        }
        logging.info(f"YOLO Inference initialized on {self.device}")
    
    def load_model(self, model_path, model_type='fruit'):
        """Load YOLO model from path"""
        try:
            if not Path(model_path).exists():
                logging.warning(f"Model file not found: {model_path}")
                return False
                
            # Load model using torch.hub or ultralytics
            model = torch.hub.load('ultralytics/yolov7', 'custom', model_path, trust_repo=True)
            model.to(self.device)
            model.eval()
            
            self.models[model_type] = model
            logging.info(f"Loaded {model_type} model from {model_path}")
            return True
            
        except Exception as e:
            logging.error(f"Error loading model {model_path}: {e}")
            return False
    
    def preprocess_image(self, image_path, img_size=640):
        """Fixed preprocessing with memory management"""
        try:
            # Check file exists and is readable
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
                
            # Read with error handling
            image = cv2.imread(image_path)
            if image is None:
                # Try with PIL as fallback
                try:
                    pil_image = Image.open(image_path)
                    image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                except Exception:
                    raise ValueError(f"Could not read image: {image_path}")
            
            # Check image dimensions
            if len(image.shape) != 3 or image.shape[2] != 3:
                raise ValueError("Invalid image format - expected 3-channel image")
            
            h, w = image.shape[:2]
            
            # Validate image size
            if h == 0 or w == 0:
                raise ValueError("Invalid image dimensions")
                
            # Memory-efficient resizing
            max_size = 2048  # Limit max image size
            if max(h, w) > max_size:
                scale = max_size / max(h, w)
                new_h, new_w = int(h * scale), int(w * scale)
                image = cv2.resize(image, (new_w, new_h))
                h, w = new_h, new_w
            
            # Continue with original preprocessing...
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            scale = img_size / max(h, w)
            new_h, new_w = int(h * scale), int(w * scale)
            
            resized = cv2.resize(image_rgb, (new_w, new_h))
            
            # Pad to square
            padded = np.zeros((img_size, img_size, 3), dtype=np.uint8)
            padded[:new_h, :new_w] = resized
            
            # Normalize
            normalized = padded.astype(np.float32) / 255.0
            
            # Convert to tensor with memory check
            try:
                tensor = torch.from_numpy(normalized).permute(2, 0, 1).unsqueeze(0)
                tensor = tensor.to(self.device)
            except RuntimeError as e:
                if "out of memory" in str(e):
                    # Clear GPU cache and retry on CPU
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                    self.device = torch.device('cpu')
                    tensor = tensor.to(self.device)
                else:
                    raise
            
            return tensor, scale, (h, w)
            
        except Exception as e:
            logging.error(f"Image preprocessing error: {e}")
            return None, None, None
    
    def postprocess_detections(self, predictions, scale, orig_size, conf_threshold=0.25):
        """Process YOLO output to extract detections"""
        try:
            detections = []
            orig_h, orig_w = orig_size
            
            # Extract predictions (assuming YOLOv7 format)
            if len(predictions) > 0:
                pred = predictions[0]  # First image in batch
                
                # Filter by confidence
                conf_mask = pred[:, 4] > conf_threshold
                pred = pred[conf_mask]
                
                if len(pred) > 0:
                    # Extract boxes, confidences, and classes
                    boxes = pred[:, :4]
                    confidences = pred[:, 4]
                    class_ids = pred[:, 5:].argmax(dim=1)
                    
                    # Scale boxes back to original image size
                    boxes[:, [0, 2]] *= orig_w / 640
                    boxes[:, [1, 3]] *= orig_h / 640
                    
                    # Convert to detections format
                    for i in range(len(boxes)):
                        x1, y1, x2, y2 = boxes[i].cpu().numpy()
                        conf = confidences[i].cpu().item()
                        class_id = class_ids[i].cpu().item()
                        
                        detection = {
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': float(conf),
                            'class_id': int(class_id),
                            'class_name': self.get_class_name(class_id)
                        }
                        detections.append(detection)
            
            return detections
            
        except Exception as e:
            logging.error(f"Error postprocessing detections: {e}")
            return []
    
    def get_class_name(self, class_id, model_type='fruit'):
        """Get class name from class ID"""
        class_names = self.class_names.get(model_type, [])
        if 0 <= class_id < len(class_names):
            return class_names[class_id]
        return f"unknown_{class_id}"
    
    def detect_fruits(self, image_path, model_type='fruit', conf_threshold=0.25):
        """Perform fruit detection on image"""
        try:
            start_time = time.time()
            
            # Check if model is loaded
            if model_type not in self.models:
                # Try to load default model
                model_paths = {
                    'fruit': 'detection_models/yolov7_fruit.pt',
                    'disease': 'detection_models/yolov7_disease.pt',
                    'tree': 'detection_models/yolov7_tree.pt'
                }
                
                model_path = model_paths.get(model_type)
                if model_path and not self.load_model(model_path, model_type):
                    # Fall back to base model if available
                    base_paths = [
                        'detection_models/yolov7.pt',
                        'detection_models/best.pt',
                        'yolov7.pt'
                    ]
                    
                    for base_path in base_paths:
                        if self.load_model(base_path, model_type):
                            break
                    else:
                        raise ValueError(f"No {model_type} model available")
            
            # Preprocess image
            tensor, scale, orig_size = self.preprocess_image(image_path)
            if tensor is None:
                raise ValueError("Failed to preprocess image")
            
            # Run inference
            model = self.models[model_type]
            with torch.no_grad():
                predictions = model(tensor)
            
            # Postprocess results
            detections = self.postprocess_detections(predictions, scale, orig_size, conf_threshold)
            
            processing_time = time.time() - start_time
            
            # Calculate results
            total_count = len(detections)
            total_weight = 0.0
            
            # Get weight coefficients
            from utils.yolo_detection import FRUIT_WEIGHTS
            
            for detection in detections:
                fruit_name = detection['class_name']
                weight = FRUIT_WEIGHTS.get(fruit_name, 0.1)
                detection['weight'] = weight
                total_weight += weight
            
            result = {
                'detections': detections,
                'total_count': total_count,
                'total_weight': round(total_weight, 3),
                'processing_time': round(processing_time, 2),
                'confidence': conf_threshold,
                'algorithm': 'YOLO v7 Real',
                'device': str(self.device)
            }
            
            logging.info(f"Detected {total_count} objects in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logging.error(f"Error in fruit detection: {e}")
            # Return fallback result indicating error
            return {
                'detections': [],
                'total_count': 0,
                'total_weight': 0.0,
                'processing_time': 0.0,
                'confidence': conf_threshold,
                'algorithm': 'YOLO v7 Real (Error)',
                'error': str(e)
            }

    def detect_leaf_disease(self, image_path, conf_threshold=0.25):
        """Detect leaf diseases using trained model"""
        return self.detect_fruits(image_path, 'disease', conf_threshold)
    
    def detect_trees(self, image_path, conf_threshold=0.25):
        """Detect trees using trained model"""
        return self.detect_fruits(image_path, 'tree', conf_threshold)
    
    def get_model_info(self):
        """Get information about loaded models"""
        info = {
            'device': str(self.device),
            'loaded_models': list(self.models.keys()),
            'cuda_available': torch.cuda.is_available()
        }
        
        if torch.cuda.is_available():
            info['gpu_name'] = torch.cuda.get_device_name(0)
            info['gpu_memory'] = torch.cuda.get_device_properties(0).total_memory
        
        return info

# Global inference engine instance
yolo_engine = YOLOInference()