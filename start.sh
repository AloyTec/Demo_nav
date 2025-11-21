#!/bin/bash

echo "🚀 Iniciando Sistema de Optimización de Rutas..."
echo ""

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Iniciar Backend
echo -e "${BLUE}📍 Iniciando Backend (Puerto 5001)...${NC}"
cd backend
/usr/bin/python3 app.py &
BACKEND_PID=$!
cd ..

# Esperar un momento
sleep 2

# Iniciar Frontend
echo -e "${BLUE}🎨 Iniciando Frontend (Puerto 3000)...${NC}"
npm run dev &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}✅ Sistema iniciado exitosamente!${NC}"
echo ""
echo "📍 Backend API: http://localhost:5001"
echo "🌐 Frontend App: http://localhost:3000"
echo ""
echo "Presiona Ctrl+C para detener todos los servicios"
echo ""

# Función para limpiar al salir
cleanup() {
    echo ""
    echo "🛑 Deteniendo servicios..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup INT TERM

# Mantener el script corriendo
wait
