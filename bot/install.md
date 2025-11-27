# 1. Clonar el repositorio (si no lo tienes ya)
cd ~
git clone https://github.com/mowgliph/usipipo.git
cd usipipo

# 2. Instalar Docker y Docker Compose
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl enable --now docker

# 3. Dar permisos a los scripts
chmod +x init-services.sh

# 4. Iniciar los servicios
sudo ./init-services.sh

# 5. Configurar el bot de Telegram
cd bot
npm install
cp .env.example .env
nano .env  # Configura tu token y usuarios autorizados

# 6. Iniciar el bot
npm start