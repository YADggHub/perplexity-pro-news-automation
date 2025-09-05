#!/bin/bash
set -e

echo "🚀 Perplexity Pro News Automation - Automated Setup"
echo "=================================================="

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция логирования
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка операционной системы
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="debian"
            log_info "Обнаружена Debian/Ubuntu система"
        elif [ -f /etc/redhat-release ]; then
            OS="redhat"
            log_info "Обнаружена RedHat/CentOS система"
        else
            OS="linux"
            log_info "Обнаружена Linux система"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        log_info "Обнаружена macOS система"
    else
        log_error "Неподдерживаемая операционная система: $OSTYPE"
        exit 1
    fi
}

# Установка Docker
install_docker() {
    log_info "Установка Docker..."

    case $OS in
        "debian")
            sudo apt-get update
            sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

            echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            ;;
        "macos")
            if command -v brew >/dev/null 2>&1; then
                brew install --cask docker
            else
                log_error "Homebrew не найден. Установите Docker Desktop вручную"
                exit 1
            fi
            ;;
        *)
            log_error "Автоматическая установка Docker не поддерживается для $OS"
            exit 1
            ;;
    esac

    # Добавление пользователя в группу docker
    sudo usermod -aG docker $USER

    log_success "Docker установлен"
}

# Установка Docker Compose
install_docker_compose() {
    log_info "Установка Docker Compose..."

    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose

    log_success "Docker Compose установлен"
}

# Проверка установки Python
check_python() {
    if command -v python3.11 >/dev/null 2>&1; then
        PYTHON_CMD="python3.11"
        log_success "Python 3.11 найден"
    elif command -v python3 >/dev/null 2>&1; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        if [[ $(echo "$PYTHON_VERSION >= 3.11" | bc) -eq 1 ]]; then
            PYTHON_CMD="python3"
            log_success "Python $PYTHON_VERSION найден"
        else
            log_warning "Найден Python $PYTHON_VERSION, рекомендуется 3.11+"
            PYTHON_CMD="python3"
        fi
    else
        log_error "Python не найден"
        exit 1
    fi
}

# Создание .env файла
setup_env_file() {
    log_info "Настройка файла конфигурации..."

    if [ ! -f .env ]; then
        cp .env.example .env
        log_info "Создан файл .env из шаблона"

        echo ""
        log_warning "НЕОБХОДИМО НАСТРОИТЬ .env ФАЙЛ!"
        echo ""
        echo "Обязательные параметры:"
        echo "- PERPLEXITY_EMAIL=ваш-email@example.com"
        echo "- PERPLEXITY_PASSWORD=ваш-пароль"
        echo "- TELEGRAM_BOT_TOKEN=токен-от-@BotFather"
        echo "- TG_*_CHANNEL=ID-ваших-каналов"
        echo ""

        read -p "Открыть .env файл для редактирования сейчас? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} .env
        fi
    else
        log_info "Файл .env уже существует"
    fi
}

# Проверка зависимостей
check_dependencies() {
    log_info "Проверка зависимостей..."

    # Docker
    if ! command -v docker >/dev/null 2>&1; then
        log_warning "Docker не найден"
        read -p "Установить Docker автоматически? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_docker
        else
            log_error "Docker необходим для работы системы"
            exit 1
        fi
    else
        log_success "Docker найден"
    fi

    # Docker Compose
    if ! command -v docker-compose >/dev/null 2>&1; then
        log_warning "Docker Compose не найден"
        install_docker_compose
    else
        log_success "Docker Compose найден"
    fi

    # Python (для локальной разработки)
    check_python
}

# Выбор способа установки
choose_installation_method() {
    echo ""
    log_info "Выберите способ установки:"
    echo "1. Docker (рекомендуется для продакшена)"
    echo "2. Локальная установка (для разработки)"
    echo "3. VPS установка (для сервера)"
    echo ""

    read -p "Введите номер (1-3): " -n 1 -r
    echo

    case $REPLY in
        1)
            INSTALL_METHOD="docker"
            ;;
        2)
            INSTALL_METHOD="local"
            ;;
        3)
            INSTALL_METHOD="vps"
            ;;
        *)
            log_error "Неверный выбор"
            exit 1
            ;;
    esac

    log_info "Выбран метод установки: $INSTALL_METHOD"
}

# Docker установка
install_docker_method() {
    log_info "Установка через Docker..."

    # Создание необходимых директорий
    mkdir -p data logs temp

    # Сборка и запуск
    log_info "Сборка Docker образа..."
    docker-compose build

    log_info "Запуск системы..."
    docker-compose up -d

    # Проверка статуса
    sleep 10
    if docker-compose ps | grep -q "Up"; then
        log_success "Система запущена успешно!"
        log_info "Веб-интерфейс: http://localhost:8080"
        log_info "Логи: docker-compose logs -f"
    else
        log_error "Ошибка запуска системы"
        docker-compose logs
        exit 1
    fi
}

# Локальная установка
install_local_method() {
    log_info "Локальная установка..."

    # Создание виртуального окружения
    log_info "Создание виртуального окружения..."
    $PYTHON_CMD -m venv venv
    source venv/bin/activate

    # Обновление pip
    pip install --upgrade pip

    # Установка зависимостей
    log_info "Установка зависимостей..."
    pip install -r requirements.txt

    # Создание директорий
    mkdir -p data logs temp

    log_success "Локальная установка завершена!"
    log_info "Активируйте окружение: source venv/bin/activate"
    log_info "Запуск системы: python main.py"
}

# VPS установка
install_vps_method() {
    log_info "Установка на VPS..."

    # Обновление системы
    sudo apt-get update && sudo apt-get upgrade -y

    # Установка Docker если нужно
    if ! command -v docker >/dev/null 2>&1; then
        install_docker
        install_docker_compose
    fi

    # Настройка файрвола
    log_info "Настройка файрвола..."
    sudo ufw allow ssh
    sudo ufw allow 8080/tcp
    sudo ufw --force enable

    # Установка как Docker
    install_docker_method

    # Настройка автозапуска
    log_info "Настройка автозапуска..."

    cat > perplexity-startup.service << EOF
[Unit]
Description=Perplexity Pro News Automation
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=true
WorkingDirectory=$(pwd)
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

    sudo mv perplexity-startup.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable perplexity-startup.service

    log_success "VPS установка завершена!"
    log_info "Система будет автоматически запускаться при перезагрузке"

    # Показ информации о системе
    echo ""
    log_info "Информация о сервере:"
    echo "IP адрес: $(curl -s ifconfig.me)"
    echo "Веб-интерфейс: http://$(curl -s ifconfig.me):8080"
    echo "SSH порт: 22"
    echo ""
}

# Проверка после установки
post_install_check() {
    log_info "Проверка установки..."

    case $INSTALL_METHOD in
        "docker")
            if docker-compose ps | grep -q "Up"; then
                log_success "✅ Система работает"
            else
                log_error "❌ Система не запущена"
                return 1
            fi
            ;;
        "local")
            if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
                log_success "✅ Виртуальное окружение создано"
            else
                log_error "❌ Проблема с виртуальным окружением"
                return 1
            fi
            ;;
        "vps")
            if systemctl is-active --quiet perplexity-startup.service; then
                log_success "✅ Служба настроена"
            else
                log_warning "⚠️ Проверьте настройку службы"
            fi
            ;;
    esac

    # Проверка файлов
    required_files=(
        "main.py"
        "config.py" 
        "requirements.txt"
        ".env"
        "docker-compose.yml"
    )

    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            log_success "✅ $file"
        else
            log_error "❌ $file не найден"
            return 1
        fi
    done

    return 0
}

# Показ итоговой информации
show_final_info() {
    echo ""
    echo "🎉 УСТАНОВКА ЗАВЕРШЕНА!"
    echo "======================="
    echo ""

    case $INSTALL_METHOD in
        "docker")
            echo "🐳 Система запущена в Docker контейнерах"
            echo "📊 Веб-интерфейс: http://localhost:8080"
            echo ""
            echo "Полезные команды:"
            echo "• Логи: docker-compose logs -f"
            echo "• Остановка: docker-compose down"
            echo "• Перезапуск: docker-compose restart"
            echo "• Статус: docker-compose ps"
            ;;
        "local")
            echo "💻 Система установлена локально"
            echo ""
            echo "Для запуска:"
            echo "1. source venv/bin/activate"
            echo "2. python main.py"
            echo ""
            echo "Веб-интерфейс будет доступен после запуска"
            ;;
        "vps")
            echo "🌐 Система развернута на VPS"
            echo "📊 Веб-интерфейс: http://$(curl -s ifconfig.me):8080"
            echo ""
            echo "Система настроена на автозапуск при перезагрузке сервера"
            ;;
    esac

    echo ""
    echo "📚 Документация:"
    echo "• README.md - обзор системы"
    echo "• INSTALL.md - подробная установка"
    echo "• docs/ - дополнительная документация"
    echo ""
    echo "🆘 Поддержка:"
    echo "• Логи: tail -f logs/perplexity_news.log"
    echo "• Проблемы: проверьте настройки в .env файле"
    echo ""
    echo "⚡ Следующие шаги:"
    echo "1. Настройте .env файл с вашими учетными данными"
    echo "2. Проверьте работу через веб-интерфейс"
    echo "3. Настройте расписание в планировщике"
    echo ""
    echo "🎯 Ожидаемый результат:"
    echo "• 15+ качественных постов в день"
    echo "• Стоимость ~$0.04 за пост"
    echo "• Автоматическая публикация в Telegram"
    echo ""
}

# Главная функция
main() {
    log_info "Начало установки Perplexity Pro News Automation System"

    # Проверка прав
    if [[ $EUID -eq 0 ]]; then
        log_warning "Не рекомендуется запускать установку от root"
    fi

    # Основная установка
    detect_os
    choose_installation_method
    check_dependencies
    setup_env_file

    case $INSTALL_METHOD in
        "docker")
            install_docker_method
            ;;
        "local")
            install_local_method
            ;;
        "vps")
            install_vps_method
            ;;
    esac

    # Проверка и финализация
    if post_install_check; then
        show_final_info
    else
        log_error "Установка завершилась с ошибками"
        exit 1
    fi
}

# Обработка сигналов
trap 'log_error "Установка прервана пользователем"; exit 1' SIGINT SIGTERM

# Запуск
main "$@"
