import qrcode
import os
from pathlib import Path
from config import settings
from utils.logger import logger

class QrGenerator:
    @staticmethod
    def generate_vpn_qr(data: str, filename: str) -> str:
        """Genera un QR a partir de la configuración y devuelve la ruta del archivo."""
        try:
            qr_path = Path(settings.QR_CODE_PATH)
            qr_path.mkdir(parents=True, exist_ok=True)
            
            file_full_path = qr_path / f"{filename}.png"
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(str(file_full_path))
            
            return str(file_full_path)
        except Exception as e:
            logger.error(f"Error generando QR: {e}")
            return ""

    @staticmethod
    def save_conf_file(content: str, filename: str) -> str:
        """Guarda el contenido en un archivo .conf para enviarlo por Telegram."""
        try:
            conf_path = Path(settings.CLIENT_CONFIGS_PATH)
            conf_path.mkdir(parents=True, exist_ok=True)
            
            file_full_path = conf_path / f"{filename}.conf"
            file_full_path.write_text(content)
            
            return str(file_full_path)
        except Exception as e:
            logger.error(f"Error guardando archivo .conf: {e}")
            return ""
