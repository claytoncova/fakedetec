import os
import cv2
import numpy as np
from PIL import Image
from exif import Image as ExifImage
from skimage.metrics import structural_similarity as ssim
from skimage.feature import local_binary_pattern
from scipy import stats
import pywt
from datetime import datetime
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
import matplotlib.pyplot as plt

class ImageAnalyzer:
    def __init__(self, output_dir: str = "output"):
        """Initialize the image analyzer with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def analyze_image(self, image_path: str) -> Dict:
        """Main analysis function that coordinates all detection methods."""
        results = {
            "filename": os.path.basename(image_path),
            "timestamp": datetime.now().isoformat(),
            "analysis_results": {}
        }
        
        # Load image
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("Could not load image")
            
            # Run all analysis methods
            results["analysis_results"]["metadata"] = self._analyze_metadata(image_path)
            results["analysis_results"]["ela"] = self._error_level_analysis(image_path)
            results["analysis_results"]["noise"] = self._analyze_noise_patterns(img)
            results["analysis_results"]["histogram"] = self._analyze_color_histogram(img)
            results["analysis_results"]["copy_move"] = self._detect_copy_move(img)
            results["analysis_results"]["ai_artifacts"] = self._detect_ai_artifacts(img)
            
            # Save results
            self._save_results(results, image_path)
            return results
            
        except Exception as e:
            return {"error": str(e), "filename": image_path}
    
    def _analyze_metadata(self, image_path: str) -> Dict:
        """Analyze image metadata for suspicious patterns."""
        metadata_results = {
            "suspicious": False,
            "findings": [],
            "exif_data": {},
            "parecer": ""
        }
        
        try:
            with open(image_path, 'rb') as img_file:
                exif_img = ExifImage(img_file)
                
                if exif_img.has_exif:
                    for tag in exif_img.list_all():
                        try:
                            value = exif_img.get(tag)
                            metadata_results["exif_data"][tag] = str(value)
                            
                            # Check for suspicious metadata
                            if tag == "Software" and any(editor in str(value).lower() 
                                for editor in ["photoshop", "gimp", "lightroom"]):
                                metadata_results["suspicious"] = True
                                metadata_results["findings"].append(
                                    f"Suspicious editing software detected: {value}")
                                metadata_results["parecer"] = "A análise dos metadados (EXIF) revelou a presença de software de edição de imagem (como Photoshop, Gimp ou Lightroom), o que indica que a imagem foi manipulada por ferramentas de edição. Isso constitui um forte indício de adulteração, pois metadados originais (por exemplo, de câmeras digitais) não deveriam conter tais softwares."
                        except Exception:
                            continue
                            
            if not metadata_results["suspicious"]:
                metadata_results["parecer"] = "A análise dos metadados (EXIF) não revelou indícios de adulteração. Os dados extraídos são compatíveis com imagens originais (por exemplo, provenientes de câmeras digitais)."
            
        except Exception as e:
            metadata_results["error"] = str(e)
            
        return metadata_results
    
    def _error_level_analysis(self, image_path: str) -> Dict:
        """Perform Error Level Analysis (ELA) to detect edited regions."""
        try:
            # Save image with specific quality
            temp_path = self.output_dir / f"temp_{os.path.basename(image_path)}"
            img = Image.open(image_path)
            img.save(temp_path, quality=90)
            
            # Calculate difference
            original = cv2.imread(str(temp_path))
            compressed = cv2.imread(image_path)
            diff = cv2.absdiff(original, compressed)
            
            # Analyze difference
            mean_diff = np.mean(diff)
            std_diff = np.std(diff)
            
            # Clean up
            os.remove(temp_path)
            
            return {
                "mean_difference": float(mean_diff),
                "std_difference": float(std_diff),
                "suspicious": mean_diff > 5.0 or std_diff > 10.0,
                "findings": ["High error level detected"] if mean_diff > 5.0 else [],
                "parecer": "A análise de nível de erro (ELA) revelou uma diferença média (ou desvio padrão) elevada, o que indica que a imagem foi recompressa ou editada. Imagens originais (por exemplo, capturadas por câmeras digitais) geralmente apresentam um nível de erro uniforme e baixo. A presença de regiões com erro elevado constitui um forte indício de adulteração." if (mean_diff > 5.0 or std_diff > 10.0) else "A análise de nível de erro (ELA) não revelou diferenças significativas, indicando que a imagem não apresenta indícios de adulteração por recompressão ou edição."
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_noise_patterns(self, img: np.ndarray) -> Dict:
        """Analyze image noise patterns for inconsistencies."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply wavelet transform
            coeffs = pywt.dwt2(gray, 'haar')
            cA, (cH, cV, cD) = coeffs
            
            # Analyze coefficients
            noise_stats = {
                "horizontal": float(np.std(cH)),
                "vertical": float(np.std(cV)),
                "diagonal": float(np.std(cD))
            }
            
            # Check for suspicious patterns
            suspicious = any(std > 20.0 for std in noise_stats.values())
            
            return {
                "noise_statistics": noise_stats,
                "suspicious": suspicious,
                "findings": ["Inconsistent noise patterns detected"] if suspicious else [],
                "parecer": "A análise de padrões de ruído (via transformada wavelet) revelou inconsistências (por exemplo, desvios-padrão elevados nas bandas horizontal, vertical ou diagonal). Imagens originais (por exemplo, capturadas por câmeras digitais) geralmente apresentam um ruído uniforme. A presença de inconsistências constitui um forte indício de adulteração." if suspicious else "A análise de padrões de ruído (via transformada wavelet) não revelou inconsistências, indicando que a imagem não apresenta indícios de adulteração."
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_color_histogram(self, img: np.ndarray) -> Dict:
        """Analyze color histogram for artificial patterns."""
        try:
            histograms = {}
            for i, col in enumerate(['b', 'g', 'r']):
                hist = cv2.calcHist([img], [i], None, [256], [0, 256])
                histograms[col] = hist.flatten().tolist()
            
            # Calculate histogram statistics
            stats = {
                col: {
                    "mean": float(np.mean(hist)),
                    "std": float(np.std(hist)),
                    "entropy": float(stats.entropy(hist))
                }
                for col, hist in histograms.items()
            }
            
            # Check for suspicious patterns
            suspicious = any(s["entropy"] < 4.0 for s in stats.values())
            
            return {
                "histogram_statistics": stats,
                "suspicious": suspicious,
                "findings": ["Artificial color patterns detected"] if suspicious else [],
                "parecer": "A análise do histograma de cores revelou padrões artificiais (por exemplo, entropia baixa), o que indica que a imagem foi gerada ou manipulada artificialmente. Imagens originais (por exemplo, capturadas por câmeras digitais) geralmente apresentam uma distribuição de cores natural. A presença de padrões artificiais constitui um forte indício de adulteração." if suspicious else "A análise do histograma de cores não revelou padrões artificiais, indicando que a imagem não apresenta indícios de adulteração."
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _detect_copy_move(self, img: np.ndarray) -> Dict:
        """Detect copy-move forgery using block matching."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Divide image into blocks
            block_size = 16
            h, w = gray.shape
            blocks = []
            
            for i in range(0, h-block_size, block_size):
                for j in range(0, w-block_size, block_size):
                    block = gray[i:i+block_size, j:j+block_size]
                    blocks.append((block, (i, j)))
            
            # Compare blocks
            similar_blocks = []
            for i, (block1, pos1) in enumerate(blocks):
                for block2, pos2 in blocks[i+1:]:
                    if np.array_equal(block1, block2):
                        similar_blocks.append((pos1, pos2))
            
            return {
                "suspicious": len(similar_blocks) > 0,
                "similar_blocks_count": len(similar_blocks),
                "findings": ["Copy-move forgery detected"] if similar_blocks else [],
                "parecer": "A análise de blocos similares (detecção de copy-move) revelou a presença de blocos idênticos (ou muito similares) em regiões distintas da imagem, o que constitui um forte indício de adulteração (por exemplo, duplicação de elementos). Imagens originais (por exemplo, capturadas por câmeras digitais) não deveriam apresentar tais duplicações." if similar_blocks else "A análise de blocos similares (detecção de copy-move) não revelou a presença de blocos idênticos, indicando que a imagem não apresenta indícios de adulteração por duplicação de elementos."
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _detect_ai_artifacts(self, img: np.ndarray) -> Dict:
        """Detect common artifacts in AI-generated images."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Analyze local binary patterns
            lbp = local_binary_pattern(gray, 8, 1, method='uniform')
            lbp_hist, _ = np.histogram(lbp, bins=10, density=True)
            
            # Check for artificial patterns
            entropy = stats.entropy(lbp_hist)
            suspicious = entropy < 2.0  # AI-generated images often have lower entropy
            
            return {
                "entropy": float(entropy),
                "suspicious": suspicious,
                "findings": ["AI generation artifacts detected"] if suspicious else [],
                "parecer": "A análise de artefatos (por exemplo, entropia baixa) revelou padrões típicos de imagens geradas por Inteligência Artificial (IA). Imagens originais (por exemplo, capturadas por câmeras digitais) geralmente apresentam uma entropia elevada. A presença de artefatos de IA constitui um forte indício de adulteração ou geração artificial." if suspicious else "A análise de artefatos não revelou padrões típicos de imagens geradas por Inteligência Artificial (IA), indicando que a imagem não apresenta indícios de adulteração ou geração artificial."
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _save_results(self, results: Dict, image_path: str) -> None:
        """Save analysis results and visualizations."""
        def convert_np(obj):
            if isinstance(obj, (np.generic,)):
                return obj.item()
            if isinstance(obj, (np.bool_, bool)):
                return bool(obj)
            if isinstance(obj, (np.integer,)):
                return int(obj)
            if isinstance(obj, (np.floating,)):
                return float(obj)
            return str(obj)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        
        # Save JSON report
        report_path = self.output_dir / f"{base_name}_report.json"
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2, default=convert_np)
        
        # Save visualizations if available
        if "ela" in results["analysis_results"]:
            img = cv2.imread(image_path)
            if img is not None:
                # Save ELA visualization
                ela_img = self._create_ela_visualization(img)
                cv2.imwrite(str(self.output_dir / f"{base_name}_ela.jpg"), ela_img)
                
                # Save histogram visualization
                self._create_histogram_visualization(img, base_name)
    
    def _create_ela_visualization(self, img: np.ndarray) -> np.ndarray:
        """Create visualization for Error Level Analysis."""
        # Save and reload image to simulate compression
        temp_path = self.output_dir / "temp_ela.jpg"
        cv2.imwrite(str(temp_path), img, [cv2.IMWRITE_JPEG_QUALITY, 90])
        compressed = cv2.imread(str(temp_path))
        os.remove(temp_path)
        
        # Calculate difference
        diff = cv2.absdiff(img, compressed)
        return diff
    
    def _create_histogram_visualization(self, img: np.ndarray, base_name: str) -> None:
        """Create and save color histogram visualization."""
        plt.figure(figsize=(10, 6))
        for i, col in enumerate(['b', 'g', 'r']):
            hist = cv2.calcHist([img], [i], None, [256], [0, 256])
            plt.plot(hist, color=col)
        plt.title('Color Histogram')
        plt.xlabel('Pixel Value')
        plt.ylabel('Frequency')
        plt.savefig(str(self.output_dir / f"{base_name}_histogram.png"))
        plt.close() 