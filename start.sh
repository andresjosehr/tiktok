#!/bin/bash
# ============================================================
# TikTok Live Event System - Comandos de inicio
# ============================================================
#
# IMPORTANTE: Ejecutar desde la raiz del proyecto
# Cada comando debe correrse en una terminal separada
#
# ============================================================

# Activar entorno virtual
source venv/Scripts/activate

case "$1" in
    # ----------------------------------------------------------
    # 1. SERVIDOR WEB (siempre necesario)
    # ----------------------------------------------------------
    # Levanta Django en todas las interfaces para acceso LAN
    # Accesible desde: http://localhost:8000 o http://192.168.1.X:8000
    #
    # URLs principales:
    #   /admin/          - Panel de administracion
    #   /simulator/      - Simulador de eventos
    #   /audio/          - Reproductor de audio
    #   /dino/           - Juego DinoChrome
    server)
        echo "========================================"
        echo "  Iniciando servidor web Django"
        echo "  http://localhost:8000"
        echo "========================================"
        python manage.py runserver 0.0.0.0:8000
        ;;

    # ----------------------------------------------------------
    # 2. SISTEMA COMPLETO (produccion)
    # ----------------------------------------------------------
    # Inicia workers + conexion a TikTok Live
    # Requiere: tiktok_user configurado en admin
    live)
        echo "========================================"
        echo "  Iniciando sistema LIVE"
        echo "  Workers + TikTok capture"
        echo "========================================"
        python manage.py start_event_system --verbose
        ;;

    # ----------------------------------------------------------
    # 3. MODO SIMULADOR (testing)
    # ----------------------------------------------------------
    # Inicia workers SIN conectar a TikTok
    # Usa /simulator/ en el navegador para enviar eventos
    sim)
        echo "========================================"
        echo "  Iniciando modo SIMULADOR"
        echo "  Workers listos, usa /simulator/"
        echo "========================================"
        python manage.py start_event_system --simulator --verbose
        ;;

    # ----------------------------------------------------------
    # 4. BASE DE DATOS (Docker MySQL)
    # ----------------------------------------------------------
    db)
        echo "Levantando MySQL..."
        docker-compose up -d db
        echo "MySQL corriendo en puerto 3307"
        ;;

    # ----------------------------------------------------------
    # 5. POBLAR DATOS INICIALES
    # ----------------------------------------------------------
    init)
        echo "Poblando datos iniciales..."
        python manage.py migrate
        python manage.py populate_initial_data
        ;;

    # ----------------------------------------------------------
    # AYUDA
    # ----------------------------------------------------------
    *)
        echo ""
        echo "============================================"
        echo "  TikTok Live Event System"
        echo "============================================"
        echo ""
        echo "  Uso: ./start.sh <comando>"
        echo ""
        echo "  Comandos disponibles:"
        echo ""
        echo "    server  - Iniciar servidor web Django"
        echo "    live    - Sistema completo (workers + TikTok)"
        echo "    sim     - Modo simulador (workers sin TikTok)"
        echo "    db      - Levantar MySQL (Docker)"
        echo "    init    - Poblar datos iniciales"
        echo ""
        echo "  Ejemplo de uso para testing:"
        echo ""
        echo "    Terminal 1:  ./start.sh db"
        echo "    Terminal 2:  ./start.sh server"
        echo "    Terminal 3:  ./start.sh sim"
        echo "    Navegador:   http://localhost:8000/simulator/"
        echo ""
        echo "  Ejemplo de uso para produccion:"
        echo ""
        echo "    Terminal 1:  ./start.sh db"
        echo "    Terminal 2:  ./start.sh server"
        echo "    Terminal 3:  ./start.sh live"
        echo ""
        echo "============================================"
        echo ""
        ;;
esac
