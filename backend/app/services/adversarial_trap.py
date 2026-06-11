"""
AI Trap: Offensive Defense System for Data Poisoning

This module implements a training-time data poisoning system that generates
adversarial image variants to degrade unauthorized AI model training.

Core Design:
- Generate multiple adversarial variants with randomized perturbations
- Inject a consistent hidden trigger pattern across all variants
- Optimize to push image embeddings away from true semantic class
- Score poison strength based on embedding divergence and prediction inconsistency
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import io
import json
from typing import List, Tuple, Dict, Optional
import copy


class AdversarialTrapGenerator:
    """
    Generates poisoned image variants designed to degrade AI model training.
    
    This system is NOT a simple adversarial attack. It's a training-time data
    poisoning system that:
    1. Generates multiple variants
    2. Injects consistent hidden triggers
    3. Pushes embeddings away from true semantic class
    4. Measures poison strength
    """
    
    def __init__(self):
        """Initialize the trap generator with a pretrained model for embedding analysis."""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load MobileNetV3 for embedding analysis (more capacity than MobileNetV3)
        self.model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.IMAGENET1K_V1)
        self.model.to(self.device)
        self.model.eval()
        
        # Remove classification head, keep features
        self.feature_extractor = nn.Sequential(self.model.features, self.model.avgpool)
        self.feature_extractor.eval()
        
        # Classification head for analysis
        self.classifier = self.model.classifier
        
        # Standard ImageNet preprocessing
        self.mean = [0.485, 0.456, 0.406]
        self.std = [0.229, 0.224, 0.225]
        
        self.preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(self.mean, self.std)
        ])
        
        # For low-level imperceptibility: keep track of baseline noise level
        self.epsilon_range = (0.005, 0.025)  # Imperceptible range
    
    def _load_image(self, image_bytes: bytes) -> Tuple[Image.Image, Tuple[int, int]]:
        """Load image from bytes and track original dimensions."""
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        original_size = img.size  # (W, H)
        return img, original_size
    
    def _get_fgsm_perturbation(
        self,
        image_tensor: torch.Tensor,
        epsilon: float,
        targeted_class: Optional[int] = None
    ) -> torch.Tensor:
        """
        Compute FGSM perturbation to maximally fool the model.
        
        Args:
            image_tensor: Preprocessed image tensor (1, 3, 224, 224)
            epsilon: Perturbation magnitude
            targeted_class: If None, untargeted attack on predicted class.
                           If int, attack toward a specific class.
        
        Returns:
            Perturbation tensor (3, 224, 224)
        """
        image_tensor_copy = image_tensor.clone().detach()
        image_tensor_copy.requires_grad = True
        
        # Forward pass
        features = self.feature_extractor(image_tensor_copy)
        features_flat = torch.flatten(features, 1)  # Flatten spatial dims
        output = self.classifier(features_flat)
        
        # Compute loss
        if targeted_class is None:
            # Untargeted: attack the predicted class
            pred_class = output.argmax(dim=1).item()
            target = torch.tensor([pred_class], device=self.device)
        else:
            target = torch.tensor([targeted_class], device=self.device)
        
        criterion = nn.CrossEntropyLoss()
        loss = criterion(output, target)
        
        # Backward pass
        loss.backward()
        
        # Extract perturbation: sign of gradient
        grad = image_tensor_copy.grad.sign()
        
        # Return as (3, 224, 224)
        return (epsilon * grad).squeeze(0).detach().cpu()
    
    def _generate_frequency_trigger(
        self,
        shape: Tuple[int, int, int],
        frequency: float = 30.0,
        phase_offset: float = 0.0
    ) -> torch.Tensor:
        """
        Generate a imperceptible frequency-domain trigger pattern.
        
        Uses high-frequency sinusoidal patterns that are:
        - Consistent across all variants
        - Imperceptible to humans
        - Detectable by deep networks
        
        Args:
            shape: (C, H, W) tensor shape
            frequency: Frequency of the wave pattern
            phase_offset: Phase shift for consistency
        
        Returns:
            Trigger tensor with values in [-0.002, 0.002] to stay imperceptible
        """
        C, H, W = shape
        
        # Create coordinate grids
        x = np.linspace(0, 1, W)
        y = np.linspace(0, 1, H)
        xv, yv = np.meshgrid(x, y)
        
        # Multi-frequency pattern for subtlety
        pattern = (
            0.0015 * np.sin(2 * np.pi * frequency * xv + phase_offset) +
            0.0015 * np.cos(2 * np.pi * frequency * yv + phase_offset) +
            0.001 * np.sin(4 * np.pi * frequency * (xv + yv) + phase_offset)
        )
        
        # Normalize to small range
        pattern = pattern / (pattern.max() + 1e-6) * 0.002
        
        # Replicate across channels
        trigger = torch.from_numpy(pattern).float()
        trigger = trigger.unsqueeze(0).repeat(C, 1, 1)
        
        return trigger
    
    def _compute_embedding_shift(
        self,
        original_tensor: torch.Tensor,
        perturbed_tensor: torch.Tensor
    ) -> Tuple[float, float]:
        """
        Measure how much the poisoned image's embedding drifts from original.
        
        Returns:
            (embedding_distance, confidence_drop_percent)
        """
        with torch.no_grad():
            # Extract embeddings
            orig_features = self.feature_extractor(original_tensor)
            pert_features = self.feature_extractor(perturbed_tensor)
            
            orig_emb = orig_torch.flatten(features, 1)
            pert_emb = pert_torch.flatten(features, 1)
            
            # Cosine distance
            cos_sim = F.cosine_similarity(orig_emb, pert_emb, dim=1)
            embedding_distance = (1.0 - cos_sim[0].item()) * 100  # Convert to percentage
            
            # Classification confidence drop
            orig_logits = self.classifier(orig_emb)
            pert_logits = self.classifier(pert_emb)
            
            orig_conf = orig_logits.softmax(dim=1).max(dim=1)[0].item()
            pert_conf = pert_logits.softmax(dim=1).max(dim=1)[0].item()
            
            confidence_drop = max(0, (orig_conf - pert_conf) / orig_conf) * 100
            
        return embedding_distance, confidence_drop
    
    def _upsample_perturbation(
        self,
        perturbation_full_res: torch.Tensor,
        target_size: Tuple[int, int]
    ) -> torch.Tensor:
        """
        Upsample perturbation from 224x224 to original image size.
        
        Args:
            perturbation_full_res: (3, 224, 224) perturbation
            target_size: (H, W) target size
        
        Returns:
            (3, H, W) upsampled perturbation
        """
        pert_batch = perturbation_full_res.unsqueeze(0)
        upsampled = F.interpolate(
            pert_batch,
            size=(target_size[1], target_size[0]),  # (H, W)
            mode='bilinear',
            align_corners=False
        )
        return upsampled.squeeze(0)
    
    def generate_variants(
        self,
        image_bytes: bytes,
        num_variants: int = 20,
        intensity: float = 50.0,
        apply_trigger: bool = True
    ) -> Tuple[List[bytes], List[Dict]]:
        """
        Generate multiple adversarial variants with trigger injection.
        
        Args:
            image_bytes: Input image
            num_variants: Number of variants to generate (20-100)
            intensity: Poison intensity (1-100 scale)
            apply_trigger: Whether to inject frequency-domain trigger
        
        Returns:
            (poisoned_image_bytes_list, metadata_list)
        """
        # Load original image
        original_img, original_size = self._load_image(image_bytes)
        
        # Preprocess
        img_tensor = self.preprocess(original_img).unsqueeze(0).to(self.device)
        
        # Convert intensity (1-100) to epsilon (0.005-0.025)
        epsilon = self.epsilon_range[0] + (intensity / 100.0) * (self.epsilon_range[1] - self.epsilon_range[0])
        
        # Generate consistent trigger once
        trigger = self._generate_frequency_trigger((3, 224, 224))
        
        # Original embedding for reference
        with torch.no_grad():
            original_embedding = self.feature_extractor(img_tensor).squeeze(-1).squeeze(-1)
        
        poisoned_variants = []
        metadata_list = []
        
        for i in range(num_variants):
            # Randomize epsilon within range for diversity
            epsilon_var = epsilon * np.random.uniform(0.8, 1.2)
            
            # Generate FGSM perturbation
            pert = self._get_fgsm_perturbation(
                img_tensor,
                epsilon=epsilon_var,
                targeted_class=None
            )
            
            # Add trigger
            if apply_trigger:
                pert = pert + trigger.to(self.device)
            
            # Clamp to ensure imperceptibility
            pert = torch.clamp(pert, -0.05, 0.05)
            
            # Apply perturbation
            poisoned_tensor = img_tensor + pert.unsqueeze(0).to(self.device)
            poisoned_tensor = torch.clamp(poisoned_tensor, -2.1, 2.1)  # Clamp in normalized space
            
            # Measure drift
            pert_emb_dist, conf_drop = self._compute_embedding_shift(img_tensor, poisoned_tensor)
            
            # Convert to image bytes
            poisoned_pil = self._tensor_to_pil(poisoned_tensor, original_size)
            img_bytes = self._pil_to_bytes(poisoned_pil)
            
            poisoned_variants.append(img_bytes)
            metadata_list.append({
                "variant_id": i,
                "epsilon": float(epsilon_var),
                "embedding_drift_percent": round(pert_emb_dist, 2),
                "confidence_drop_percent": round(conf_drop, 2),
                "has_trigger": apply_trigger
            })
        
        return poisoned_variants, metadata_list
    
    def _tensor_to_pil(
        self,
        tensor: torch.Tensor,
        target_size: Tuple[int, int]
    ) -> Image.Image:
        """
        Convert normalized tensor back to PIL image.
        
        Args:
            tensor: (1, 3, 224, 224) or (3, 224, 224) normalized tensor
            target_size: (W, H) target size
        
        Returns:
            PIL Image
        """
        if tensor.dim() == 4:
            tensor = tensor.squeeze(0)
        
        # Denormalize
        tensor_cpu = tensor.cpu()
        for t, m, s in zip(tensor_cpu, self.mean, self.std):
            t.mul_(s).add_(m)
        
        # Clamp to valid range
        tensor_cpu = torch.clamp(tensor_cpu, 0, 1)
        
        # Upsample to original size
        tensor_upsample = F.interpolate(
            tensor_cpu.unsqueeze(0),
            size=(target_size[1], target_size[0]),
            mode='bilinear',
            align_corners=False
        ).squeeze(0)
        
        # Convert to PIL
        img = transforms.ToPILImage()(tensor_upsample)
        return img
    
    def _pil_to_bytes(self, pil_img: Image.Image) -> bytes:
        """Convert PIL image to PNG bytes."""
        buffer = io.BytesIO()
        pil_img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def calculate_poison_score(
        self,
        metadata_list: List[Dict]
    ) -> float:
        """
        Calculate overall poison strength score.
        
        Combines:
        - Average embedding drift
        - Average confidence drop
        - Consistency across variants
        
        Returns:
            Poison strength (0-100 scale)
        """
        if not metadata_list:
            return 0.0
        
        avg_embedding_drift = np.mean([m["embedding_drift_percent"] for m in metadata_list])
        avg_conf_drop = np.mean([m["confidence_drop_percent"] for m in metadata_list])
        
        # Consistency: lower std is better (more consistent poison)
        embedding_drift_std = np.std([m["embedding_drift_percent"] for m in metadata_list])
        consistency_bonus = max(0, 10 - embedding_drift_std)  # Bonus up to 10 points
        
        # Combined score
        poison_score = (avg_embedding_drift * 0.4 + avg_conf_drop * 0.5 + consistency_bonus * 0.1)
        
        return min(100.0, max(0.0, poison_score))
    
    def generate_trap_package(
        self,
        image_bytes: bytes,
        num_variants: int = 20,
        intensity: float = 50.0,
        return_zip: bool = False
    ) -> Dict:
        """
        Generate complete trap package: poisoned variants + scores.
        
        Args:
            image_bytes: Input image
            num_variants: Number of variants (20-100)
            intensity: Poison intensity (1-100)
            return_zip: If True, return as zip file bytes
        
        Returns:
            {
                "poisoned_images": [...bytes...],
                "poison_strength_score": float,
                "metadata": [...],
                "summary": {...}
            }
        """
        # Generate variants
        poisoned_images, metadata = self.generate_variants(
            image_bytes,
            num_variants=num_variants,
            intensity=intensity,
            apply_trigger=True
        )
        
        # Calculate poison score
        poison_score = self.calculate_poison_score(metadata)
        
        # Summary
        summary = {
            "num_variants": len(poisoned_images),
            "poison_strength_score": round(poison_score, 2),
            "avg_embedding_drift": round(np.mean([m["embedding_drift_percent"] for m in metadata]), 2),
            "avg_confidence_drop": round(np.mean([m["confidence_drop_percent"] for m in metadata]), 2),
            "trigger_injected": True
        }
        
        result = {
            "poisoned_images": poisoned_images,
            "poison_strength_score": poison_score,
            "metadata": metadata,
            "summary": summary
        }
        
        if return_zip:
            result["zip_bytes"] = self._create_zip_package(poisoned_images, metadata, summary)
        
        return result
    
    def _create_zip_package(
        self,
        poisoned_images: List[bytes],
        metadata: List[Dict],
        summary: Dict
    ) -> bytes:
        """
        Create a zip file containing all poisoned images and metadata.
        
        Returns:
            ZIP file bytes
        """
        import zipfile
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add images
            for i, img_bytes in enumerate(poisoned_images):
                zf.writestr(f"poisoned_{i:03d}.png", img_bytes)
            
            # Add metadata
            zf.writestr("metadata.json", json.dumps(metadata, indent=2))
            zf.writestr("summary.json", json.dumps(summary, indent=2))
        
        return zip_buffer.getvalue()
