import asyncio
import os
import re
import uuid
import ipaddress
from pathlib import Path
from typing import Optional, Dict, List
from loguru import logger
from config import settings

class WireGuardClient:
    """
    Cliente de infraestructura para gestionar WireGuard nativo.
    Manipula /etc/wireguard/wg0.conf y utiliza comandos 'wg'.
    """

    def __init__(self):
        self.interface = settings.WG_INTERFACE or "wg0"
        self.base_path = Path(settings.WG_PATH or "/etc/wireguard")
        self.conf_path = self.base_path / f"{self.interface}.conf"
        self.clients_dir = self.base_path / "clients"
        self.default_quota = 10 * 1024 * 1024 * 1024  # 10 GB
        
        # Asegurar directorio de clientes al iniciar
        os.makedirs(self.clients_dir, exist_ok=True)

    async def _run_cmd(self, cmd: str) -> str:
        """Ejecuta comandos de shell de forma asíncrona."""
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            error_msg = stderr.decode().strip()
            logger.error(f"Comando fallido: {cmd} | Error: {error_msg}")
            raise Exception(f"Error ejecutando comando WireGuard: {error_msg}")
        return stdout.decode().strip()

    async def get_next_available_ip(self) -> str:
        """Calcula la siguiente IP disponible basada en el archivo .conf"""
        try:
            content = self.conf_path.read_text()
            addr_match = re.search(r"Address\s*=\s*([\d.]+)", content)
            if not addr_match:
                raise Exception("No se encontró la dirección base en wg0.conf")
            
            network = ipaddress.IPv4Interface(f"{addr_match.group(1)}/24").network
            
            used_ips = set(re.findall(r"AllowedIPs\s*=\s*([\d.]+)", content))
            
            server_ip = network.network_address + 1
            
            for ip in network.hosts():
                str_ip = str(ip)
                if str_ip not in used_ips and str_ip != str(server_ip):
                    return str_ip
            
            raise Exception("No hay IPs disponibles en el rango de WireGuard")
        except Exception as e:
            logger.error(f"Error calculando IP: {e}")
            raise

    async def create_peer(self, user_id: int, name: str) -> dict:
        """
        Crea un nuevo Peer, actualiza el .conf y lo aplica en vivo.
        """
        # CORRECCIÓN LÓGICA: Añadimos UUID para permitir múltiples llaves por usuario
        client_name = f"tg_{user_id}_{uuid.uuid4().hex[:4]}"
        
        # 1. Generar llaves
        priv_key = await self._run_cmd("wg genkey")
        pub_key = await self._run_cmd(f"echo '{priv_key}' | wg pubkey")
        psk = await self._run_cmd("wg genpsk")
        
        # 2. Obtener IP y claves del servidor
        client_ip = await self.get_next_available_ip()
        server_pub_key = settings.WG_SERVER_PUBKEY or await self._run_cmd(f"wg show {self.interface} public-key")
        
        # 3. Crear bloque de configuración para el servidor
        peer_block = (
            f"\n### CLIENT {client_name}\n"
            f"[Peer]\n"
            f"PublicKey = {pub_key}\n"
            f"PresharedKey = {psk}\n"
            f"AllowedIPs = {client_ip}/32\n"
        )

        # 4. Actualizar wg0.conf (Atómico)
        with open(self.conf_path, "a") as f:
            f.write(peer_block)

        # 5. Aplicar en caliente sin reiniciar la interfaz
        # Usamos <(echo ...) para pasar la PSK de forma segura
        cmd = f"wg set {self.interface} peer {pub_key} allowed-ips {client_ip}/32 preshared-key <(echo {psk})"

        await self._run_cmd(cmd)

        # 6. Generar archivo .conf para el cliente
        client_conf = self._build_client_config(priv_key, client_ip, server_pub_key, psk)
        client_file = self.clients_dir / f"{self.interface}-{client_name}.conf"
        client_file.write_text(client_conf)
        os.chmod(client_file, 0o600)

        # Devolvemos estructura consistente con lo que espera vpn_service.py
        return {
            "id": pub_key,
            "name": name,
            "client_name": client_name, # Este ID incluye el UUID
            "ip": client_ip,
            "config": client_conf,
            "file_path": str(client_file)
        }

    def _build_client_config(self, priv_key: str, ip: str, server_pub: str, psk: str) -> str:
        """Construye el contenido del archivo .conf del cliente."""
        dns = f"{settings.WG_CLIENT_DNS_1 or '1.1.1.1'}"
        endpoint = settings.WG_ENDPOINT or f"{settings.SERVER_IP}:{settings.WG_SERVER_PORT or '51820'}"
        
        return f"""[Interface]
PrivateKey = {priv_key}
Address = {ip}/24
DNS = {dns}
MTU = 1420

[Peer]
PublicKey = {server_pub}
PresharedKey = {psk}
Endpoint = {endpoint}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 15
"""

    async def delete_peer(self, pub_key: str, client_name: str) -> bool:
        """Elimina un peer del servidor y del archivo de configuración."""
        try:
    
            content = self.conf_path.read_text()

            pk_pattern = rf"### CLIENT {re.escape(client_name)}.*?PublicKey\s*=\s*([^\n]+)"
            match = re.search(pk_pattern, content, flags=re.DOTALL)
            
            if match:
                found_pub_key = match.group(1).strip()
                await self._run_cmd(f"wg set {self.interface} peer {found_pub_key} remove")
            elif pub_key:
                 await self._run_cmd(f"wg set {self.interface} peer {pub_key} remove")

            # Limpieza del bloque en texto
            pattern = rf"### CLIENT {re.escape(client_name)}.*?(?=\n### CLIENT|\Z)"
            new_content = re.sub(pattern, "", content, flags=re.DOTALL)
            self.conf_path.write_text(new_content.strip() + "\n")
            
            # 3. Eliminar archivo .conf del cliente
            client_file = self.clients_dir / f"{self.interface}-{client_name}.conf"
            if client_file.exists():
                client_file.unlink()
                
            return True
        except Exception as e:
            logger.error(f"Error eliminando peer {client_name}: {e}")
            return False

    # Alias para mantener consistencia con vpn_service si llama a delete_client
    async def delete_client(self, client_name: str) -> bool:
        return await self.delete_peer(pub_key="", client_name=client_name)

    async def get_usage(self) -> List[Dict]:
        """Obtiene el uso de datos de todos los peers (wg show dump)."""
        try:
            output = await self._run_cmd(f"wg show {self.interface} dump")
            lines = output.split("\n")[1:] # Saltamos la cabecera
            
            usage = []
            for line in lines:
                cols = line.split("\t")
                if len(cols) >= 7:
                    usage.append({
                        "public_key": cols[0],
                        "rx": int(cols[5]),
                        "tx": int(cols[6]),
                        "total": int(cols[5]) + int(cols[6])
                    })
            return usage
        except Exception as e:
            logger.error(f"Error obteniendo métricas WG: {e}")
            return []