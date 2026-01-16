import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import io
import copy

class AdversarialProtector:
    def __init__(self):
        # Initialize with a pre-trained ResNet18 model
        # strict=False allows loading even if some minor version differences exist, 
        # but for standard torchvision models it's usually fine.
        # We use CPU by default to ensure compatibility, can be moved to CUDA if available.
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load a lightweight robust model (ResNet18) in eval mode
        self.model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
        self.model.to(self.device)
        self.model.eval()
        
        # Standard ImageNet normalization
        self.mean = [0.485, 0.456, 0.406]
        self.std = [0.229, 0.224, 0.225]
        
        self.preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(self.mean, self.std)
        ])
        
        # Inverse transform to get back to image space for saving
        # Note: This is an approximation since we can't perfectly invert resizing/cropping
        # So for the actual adversarial image generation, we apply noise to the tensor 
        # and then effectively add it back to the original image in a smart way,
        # or we just work on the resized version.
        # Ideally for "protection" we want the output to be the same resolution as input.
        # So we will generate the noise pattern on the resized image and upsample it back.

    def _get_gradient(self, image_tensor, target_class=None):
        """
        Compute gradient of the loss with respect to the input image.
        If target_class is None, we maximize the loss of the predicted class (untargeted attack).
        """
        image_tensor.requires_grad = True
        output = self.model(image_tensor)
        
        if target_class is None:
            # Untargeted: Attack the most likely class
            target_class = output.max(1)[1]
            
        criterion = nn.CrossEntropyLoss()
        loss = criterion(output, target_class)
        
        self.model.zero_grad()
        loss.backward()
        
        return image_tensor.grad.data, loss.item()

    def protect_image(self, image_bytes, strength=0.01):
        """
        Apply adversarial noise to the image.
        strength: Epsilon value for FGSM (0.001 to 0.05 is usually good for imperceptibility).
        Returns: Protected image bytes, Robustness score
        """
        try:
            # 1. Load Image
            original_image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            # Keep original size for final reconstruction
            original_size = original_image.size
            
            # 2. Preprocess for Model
            # We work on a copy for gradient computation
            img_tensor = self.preprocess(original_image).unsqueeze(0).to(self.device)
            
            # 3. Compute Gradient (FGSM)
            gradient, initial_loss = self._get_gradient(img_tensor)
            
            # 4. Generate Perturbation
            # FGSM: perturbation = epsilon * sign(gradient)
            # We want to INCREASE the loss, so we ADD the gradient based perturbation
            perturbation = strength * gradient.sign()
            
            # 5. Apply Perturbation to the standardized tensor (for score calculation)
            adv_tensor = img_tensor + perturbation
            
            # 6. Calculate Robustness Score
            # We check how much the confidence of the original top class dropped
            with torch.no_grad():
                original_output = self.model(img_tensor)
                adv_output = self.model(adv_tensor)
                
                orig_probs = torch.nn.functional.softmax(original_output, dim=1)
                adv_probs = torch.nn.functional.softmax(adv_output, dim=1)
                
                top_class = orig_probs.max(1)[1]
                orig_conf = orig_probs[0, top_class].item()
                adv_conf = adv_probs[0, top_class].item()
                
                # Score: How much confidence was lost? 
                # If originally 0.9 and now 0.4, score is high.
                # If originally 0.9 and now 0.8, score is low.
                # Max score is when adv_conf is close to 0.
                robustness_score = max(0, (orig_conf - adv_conf) / orig_conf) * 100
            
            # 7. Apply Perturbation to Original Image
            # To apply the perturbation to the FULL resolution image, we need to:
            # a) Denoise/Inverse Normalize the perturbation
            # b) Upsample the perturbation to original size
            # c) Add to original image
            
            # Inverse normalize the perturbation: perturbation is in normalized space.
            # We want it in pixel space (0-1).
            # The normalization was: (x - mean) / std
            # So x_norm = (x - mean)/std
            # We added p_norm. x_adv_norm = x_norm + p_norm
            # x_adv = (x_adv_norm * std) + mean = ((x_norm + p_norm) * std) + mean
            #       = (x_norm * std + mean) + (p_norm * std)
            #       = x + (p_norm * std)
            # So the pixel-space perturbation is p_norm * std
            
            perturbation_cpu = perturbation.squeeze(0).cpu()
            
            # Un-normalize the perturbation per channel
            # We only care about the delta, so we just multiply by std
            for t, s in zip(perturbation_cpu, self.std):
                t.mul_(s)
                
            # Convert to PIL Image for resizing
            # perturbation is now in approx -strength to +strength range (scaled by std)
            # We need to shift it to visualize or resize, but here we just want to resize the float values.
            # simpler approach: work with numpy arrays
            
            pert_np = perturbation_cpu.numpy().transpose(1, 2, 0) # H, W, C
            
            # Resize perturbation to match original image size
            # We use bilinear interpolation for smooth noise
            pert_img = Image.fromarray((pert_np * 255).astype(np.uint8)) # Lossy conversion just for resizing? 
            # Better: use cv2 or scipy for float resizing if high precision needed
            # But for "noise", simple resize of the tensor is often robust enough.
            # Let's use torch's interpolate for the tensor before converting to numpy
            
            pert_tensor_full = torch.nn.functional.interpolate(
                perturbation_cpu.unsqueeze(0), 
                size=(original_size[1], original_size[0]), # H, W
                mode='bilinear', 
                align_corners=False
            ).squeeze(0)
            
            # Add to original image
            # Original image as tensor (0-1)
            orig_tensor_full = transforms.ToTensor()(original_image)
            
            # Clip perturbation effectively
            # But wait, logic above for un-normalization was slightly off because p_norm is signed.
            # Correct logic:
            # We computed grad on normalized space.
            # To apply to (0-1) image:
            # delta_img = epsilon * sign(grad_wrt_pixels)
            # grad_wrt_pixels is approx grad_wrt_norm * (1/std)
            # So just upsampling the sign map usually works well for FGSM equivalent in pixel space.
            # Let's try the simpler approach often used in "Protection" libraries:
            # 1. Compute grad on resized image.
            # 2. Upsample GRADIENT to full size (or sign of gradient).
            # 3. Apply update: img = img + epsilon * sign(upsampled_grad)
            
            grad_up = torch.nn.functional.interpolate(
                gradient, 
                size=(original_size[1], original_size[0]), 
                mode='bilinear', 
                align_corners=False
            )
            
            # Apply Noise
            # We assume original image determines user perception, so we work in 0-1 range
            # transforms.ToTensor() loads as 0-1 float
            
            final_img_tensor = orig_tensor_full + (strength * grad_up.sign().squeeze(0).cpu())
            final_img_tensor = torch.clamp(final_img_tensor, 0, 1)
            
            # Convert back to Bytes
            final_pil = transforms.ToPILImage()(final_img_tensor)
            output_buffer = io.BytesIO()
            final_pil.save(output_buffer, format='PNG')
            return output_buffer.getvalue(), robustness_score

        except Exception as e:
            print(f"Adversarial protection failed: {e}")
            raise e
