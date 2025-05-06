#!/bin/bash

echo "🔍 Vérification complète de l'état du site Django..."

# === Variables ===
VENV_PATH="/home/tristan/apesf/venv"
PROJECT_PATH="/home/tristan/apesf/apesf_site"
DJANGO_MANAGE="$PROJECT_PATH/manage.py"
GUNICORN_SOCKET="/home/tristan/apesf/gunicorn.sock"
PUBLIC_IP="51.83.73.146"

# === Venv ===
echo -n "🔧 Environnement virtuel : "
if [ -f "$VENV_PATH/bin/activate" ]; then
    echo "✅ trouvé"
    source "$VENV_PATH/bin/activate"
else
    echo "❌ non trouvé"
fi

# === Gunicorn dans venv ===
echo -n "🔧 Gunicorn (venv) : "
if command -v gunicorn &> /dev/null; then
    echo "✅ présent"
else
    echo "❌ manquant"
fi

# === Services système ===
for service in postgresql nginx gunicorn; do
    echo -n "🖥️  Service $service : "
    if systemctl is-active --quiet $service; then
        echo "✅ actif"
    else
        echo "❌ inactif"
    fi
done

# === Port 8000 ===
echo -n "🔌 Port 8000 : "
if sudo lsof -i :8000 &> /dev/null; then
    echo "⚠️  utilisé"
else
    echo "✅ libre"
fi

# === Socket gunicorn (si utilisé) ===
if [ -S "$GUNICORN_SOCKET" ]; then
    echo "📡 Socket Gunicorn : ✅ présent ($GUNICORN_SOCKET)"
else
    echo "📡 Socket Gunicorn : ⚠️  absent (non critique si port TCP utilisé)"
fi

# === Migrations Django ===
echo -n "🗃️  Migrations : "
cd "$PROJECT_PATH"
MISSING=$(python manage.py showmigrations | grep '\[ \]' | wc -l)
if [ "$MISSING" -eq 0 ]; then
    echo "✅ toutes appliquées"
else
    echo "⚠️  $MISSING non appliquées"
fi

# === Accès HTTP public ===
echo -n "🌐 Test HTTP ($PUBLIC_IP) : "
if curl -s --head http://$PUBLIC_IP | grep "200 OK" > /dev/null; then
    echo "✅ en ligne"
else
    echo "❌ inaccessible (vérifier nginx ou Gunicorn)"
fi

echo ""
echo "🎯 Vérification terminée."
