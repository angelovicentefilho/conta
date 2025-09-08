import sys
import os
import socket
import re
from urllib.parse import urlparse

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app.config.settings import Settings
    settings = Settings()
except ImportError:
    # Fallback para valores padrão se não conseguir importar
    class FallbackSettings:
        environment = "dev"
        host = "0.0.0.0"
        port = 8000
        mongodb_url = "mongodb://localhost:27017"
        mongodb_database = "financeiro_db"
        redis_url = "redis://localhost:6379/0"
        app_name = "Financeiro Backend"
        app_version = "0.1.0"
    
    settings = FallbackSettings()

def cyan(text): return f"\033[1;36m{text}\033[0m"
def magenta(text): return f"\033[1;35m{text}\033[0m"
def gray(text): return f"\033[38;5;245m{text}\033[0m"
def green(text): return f"\033[1;32m{text}\033[0m"
def red(text): return f"\033[1;31m{text}\033[0m"

def check_service(host, port):
    try:
        with socket.create_connection((host, int(port)), timeout=1):
            return green("✓ Connected")
    except Exception:
        return red("✗ Unavailable")

def strip_ansi(text):
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', text)

def parse_url_host_port(url, default_port):
    """Extrai host e porta de uma URL"""
    try:
        parsed = urlparse(url)
        host = parsed.hostname or 'localhost'
        port = parsed.port or default_port
        return host, port
    except:
        return 'localhost', default_port

# Extrair informações de conexão
mongo_host, mongo_port = parse_url_host_port(settings.mongodb_url, 27017)
redis_host, redis_port = parse_url_host_port(settings.redis_url, 6379)

# Root context da API
api_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app"))
python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

rows = [
    ("Root Context:", cyan(api_root)),
    ("Environment:", cyan(settings.environment)),
    ("API Host:", cyan(f"{settings.host}:{settings.port}")),
    ("App Name:", cyan(getattr(settings, 'app_name', 'Financeiro Backend'))),
    ("App Version:", cyan(getattr(settings, 'app_version', '0.1.0'))),
    ("MongoDB:", cyan(f"{mongo_host}:{mongo_port}/{settings.mongodb_database}")),
    ("Redis:", cyan(f"{redis_host}:{redis_port}")),
    ("Python:", cyan(python_version)),
    ("MongoDB Status:", check_service(mongo_host, mongo_port)),
    ("Redis Status:", check_service(redis_host, redis_port)),
]

# Calcular larguras
label_width = max(len(label) for label, _ in rows)
value_width = max(len(strip_ansi(str(value))) for _, value in rows)
table_width = label_width + value_width + 5

title_text = '💰 Sistema Financeiro - Status'
title_color = magenta(title_text)
title_len = len(title_text) - 2  # Subtrair os emojis
pad_total = table_width - 2 - title_len
pad_left = pad_total // 2
pad_right = pad_total - pad_left
title_line = ' ' * pad_left + title_color + ' ' * pad_right

# Imprimir tabela
print(gray("┌" + "─" * (table_width - 2) + "┐"))
print(gray("│") + title_line + gray("│"))
print(gray("├" + "─" * (table_width - 2) + "┤"))
for label, value in rows:
    value_str = str(value)
    pad = value_width - len(strip_ansi(value_str))
    print(gray("│") + f" {label.ljust(label_width)} {value_str}{' ' * pad} " + gray("│"))
print(gray("└" + "─" * (table_width - 2) + "┘"))