import torch
import torch.nn as nn
import numpy as np
import yaml
import logging
from pathlib import Path

class ModelTrainingConfig:
    """Training configuration for YOLO models from uploaded files"""
    
    def __init__(self):
        self.hyperparameters = {
            'lr0': 0.01,  # initial learning rate
            'lrf': 0.1,   # final OneCycleLR learning rate (lr0 * lrf)
            'momentum': 0.937,  # SGD momentum/Adam beta1
            'weight_decay': 0.0005,  # optimizer weight decay
            'warmup_epochs': 3.0,  # warmup epochs
            'warmup_momentum': 0.8,  # warmup initial momentum
            'warmup_bias_lr': 0.1,  # warmup initial bias lr
            'box': 0.05,  # box loss gain
            'cls': 0.3,   # cls loss gain
            'cls_pw': 1.0,  # cls BCELoss positive_weight
            'obj': 0.7,   # obj loss gain (scale with pixels)
            'obj_pw': 1.0,  # obj BCELoss positive_weight
            'iou_t': 0.20,  # IoU training threshold
            'anchor_t': 4.0,  # anchor-multiple threshold
            'fl_gamma': 0.0,  # focal loss gamma
            'hsv_h': 0.015,  # image HSV-Hue augmentation (fraction)
            'hsv_s': 0.7,   # image HSV-Saturation augmentation (fraction)
            'hsv_v': 0.4,   # image HSV-Value augmentation (fraction)
            'degrees': 0.0,  # image rotation (+/- deg)
            'translate': 0.1,  # image translation (+/- fraction)
            'scale': 0.9,  # image scale (+/- gain)
            'shear': 0.0,  # image shear (+/- deg)
            'perspective': 0.0,  # image perspective (+/- fraction)
            'flipud': 0.0,  # image flip up-down (probability)
            'fliplr': 0.5,  # image flip left-right (probability)
            'mosaic': 1.0,  # image mosaic (probability)
            'mixup': 0.15,  # image mixup (probability)
        }
    
    def load_hyperparameters(self, config_path):
        """Load hyperparameters from YAML file"""
        try:
            with open(config_path, 'r') as f:
                hyp = yaml.safe_load(f)
                self.hyperparameters.update(hyp)
                return self.hyperparameters
        except Exception as e:
            logging.warning(f"Could not load hyperparameters from {config_path}: {e}")
            return self.hyperparameters

class LossCalculator:
    """Loss calculation utilities from uploaded training files"""
    
    def __init__(self, device='cpu'):
        self.device = device
        self.bce_loss = nn.BCEWithLogitsLoss(reduction='none')
        
    def compute_detection_loss(self, predictions, targets, num_classes=80):
        """Compute YOLO detection loss"""
        # Simplified loss calculation - in real deployment would use full YOLO loss
        box_loss = 0.0
        obj_loss = 0.0 
        cls_loss = 0.0
        
        for pred in predictions:
            # Mock loss calculation
            box_loss += torch.rand(1).item() * 0.05
            obj_loss += torch.rand(1).item() * 0.1
            cls_loss += torch.rand(1).item() * 0.02
        
        total_loss = box_loss + obj_loss + cls_loss
        
        return {
            'total_loss': total_loss,
            'box_loss': box_loss,
            'obj_loss': obj_loss,
            'cls_loss': cls_loss
        }

class DataAugmentation:
    """Data augmentation techniques from uploaded training pipeline"""
    
    def __init__(self, hyp=None):
        self.hyp = hyp or {}
        
    def mosaic_augmentation(self, images, labels):
        """Mosaic augmentation technique"""
        # Mock implementation - in real deployment would implement full mosaic
        return images, labels
        
    def mixup_augmentation(self, images, labels):
        """MixUp augmentation technique"""
        # Mock implementation
        return images, labels
        
    def hsv_augmentation(self, image):
        """HSV color space augmentation"""
        # Mock implementation
        return image

class ModelEvaluator:
    """Model evaluation metrics from uploaded test files"""
    
    def __init__(self):
        self.metrics = {
            'precision': 0.0,
            'recall': 0.0,
            'mAP@0.5': 0.0,
            'mAP@0.5:0.95': 0.0
        }
    
    def calculate_map(self, predictions, ground_truth, iou_threshold=0.5):
        """Calculate mean Average Precision"""
        # Simplified mAP calculation
        if len(predictions) == 0:
            return 0.0
            
        # Mock mAP calculation - would implement full mAP computation in real deployment
        return np.random.uniform(0.7, 0.95)
    
    def calculate_precision_recall(self, predictions, ground_truth):
        """Calculate precision and recall"""
        if len(predictions) == 0:
            return 0.0, 0.0
            
        # Mock calculations
        precision = np.random.uniform(0.8, 0.95)
        recall = np.random.uniform(0.75, 0.9)
        
        return precision, recall
    
    def evaluate_model(self, model, test_data):
        """Comprehensive model evaluation"""
        precision, recall = self.calculate_precision_recall([], [])
        map_50 = self.calculate_map([], [])
        map_50_95 = self.calculate_map([], [], iou_threshold=0.75)
        
        self.metrics = {
            'precision': precision,
            'recall': recall,
            'mAP@0.5': map_50,
            'mAP@0.5:0.95': map_50_95,
            'f1_score': 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        }
        
        return self.metrics

class CheckpointManager:
    """Model checkpoint management from uploaded training utilities"""
    
    def __init__(self, save_dir='./checkpoints'):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
    def save_checkpoint(self, model, optimizer, epoch, metrics, is_best=False):
        """Save model checkpoint"""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': model.state_dict() if hasattr(model, 'state_dict') else None,
            'optimizer_state_dict': optimizer.state_dict() if hasattr(optimizer, 'state_dict') else None,
            'metrics': metrics,
            'timestamp': torch.tensor(time.time())
        }
        
        # Save latest checkpoint
        latest_path = self.save_dir / 'latest.pt'
        torch.save(checkpoint, latest_path)
        
        # Save best checkpoint if this is the best model
        if is_best:
            best_path = self.save_dir / 'best.pt'
            torch.save(checkpoint, best_path)
        
        return str(latest_path)
    
    def load_checkpoint(self, checkpoint_path):
        """Load model checkpoint"""
        try:
            checkpoint = torch.load(checkpoint_path, map_location='cpu')
            return checkpoint
        except Exception as e:
            logging.error(f"Error loading checkpoint: {e}")
            return None

class TrainingLogger:
    """Training logging utilities"""
    
    def __init__(self, log_dir='./logs'):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_dir / 'training.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def log_epoch(self, epoch, metrics, lr):
        """Log epoch results"""
        self.logger.info(
            f"Epoch {epoch}: "
            f"Loss: {metrics.get('total_loss', 0):.4f}, "
            f"mAP@0.5: {metrics.get('mAP@0.5', 0):.4f}, "
            f"LR: {lr:.6f}"
        )
    
    def log_training_start(self, config):
        """Log training start"""
        self.logger.info("Starting training with configuration:")
        for key, value in config.items():
            self.logger.info(f"  {key}: {value}")
    
    def log_training_end(self, final_metrics):
        """Log training completion"""
        self.logger.info("Training completed!")
        self.logger.info("Final metrics:")
        for key, value in final_metrics.items():
            self.logger.info(f"  {key}: {value:.4f}")

def create_optimizer(model, hyp):
    """Create optimizer from hyperparameters"""
    # Mock optimizer creation
    return torch.optim.SGD(
        model.parameters() if hasattr(model, 'parameters') else [],
        lr=hyp.get('lr0', 0.01),
        momentum=hyp.get('momentum', 0.937),
        weight_decay=hyp.get('weight_decay', 0.0005)
    )

def create_scheduler(optimizer, hyp, epochs):
    """Create learning rate scheduler"""
    # Mock scheduler creation
    return torch.optim.lr_scheduler.OneCycleLR(
        optimizer,
        max_lr=hyp.get('lr0', 0.01),
        total_steps=epochs,
        pct_start=0.1,
        final_div_factor=1.0 / hyp.get('lrf', 0.1)
    )

import time