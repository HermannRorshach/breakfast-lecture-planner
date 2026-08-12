#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_STATE="${PROJECT_DIR}/.deploy-state"
HEALTHCHECK_URL="${DEPLOY_HEALTHCHECK_URL:-https://malone.guru/}"
COMPOSE=(docker compose --project-directory "${PROJECT_DIR}")
RESTORE_DATABASE=false

usage() {
    cat <<'EOF'
Использование:
  ./rollback.sh                    откатить только код
  ./rollback.sh --restore-database откатить код и восстановить БД

Восстановление БД удалит все изменения данных, сделанные после последнего деплоя.
EOF
}

case "${1:-}" in
    "") ;;
    --restore-database) RESTORE_DATABASE=true ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
esac

cd "${PROJECT_DIR}"

if [[ ! -f "${DEPLOY_STATE}" ]]; then
    echo "Ошибка: не найден ${DEPLOY_STATE}. Сначала должен пройти deploy.sh." >&2
    exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
    echo "Ошибка: на сервере есть незакоммиченные изменения." >&2
    git status --short >&2
    exit 1
fi

# Файл создаётся deploy.sh и содержит только контролируемые значения.
# shellcheck disable=SC1090
source "${DEPLOY_STATE}"

if [[ -z "${PREVIOUS_COMMIT:-}" ]] || ! git cat-file -e "${PREVIOUS_COMMIT}^{commit}"; then
    echo "Ошибка: предыдущий коммит не найден." >&2
    exit 1
fi

if [[ "${RESTORE_DATABASE}" == true ]]; then
    if [[ -z "${DATABASE_BACKUP:-}" ]] || [[ ! -s "${DATABASE_BACKUP}" ]]; then
        echo "Ошибка: резервная копия БД не найдена." >&2
        exit 1
    fi

    "${COMPOSE[@]}" exec -T postgres pg_restore --list \
        < "${DATABASE_BACKUP}" > /dev/null
fi

current_commit="$(git rev-parse HEAD)"
echo "Откат к коммиту ${PREVIOUS_COMMIT}..."
git checkout --detach "${PREVIOUS_COMMIT}"

if [[ "${RESTORE_DATABASE}" == true ]]; then
    echo "Остановка приложения и восстановление PostgreSQL..."
    "${COMPOSE[@]}" stop breakfast_lecture_planner
    if ! "${COMPOSE[@]}" exec -T postgres sh -c \
        'pg_restore --clean --if-exists --single-transaction --no-owner --no-privileges -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
        < "${DATABASE_BACKUP}"; then
        echo "Восстановление БД не удалось; код возвращён к исходному коммиту." >&2
        git checkout --detach "${current_commit}"
        exit 1
    fi
fi

echo "Пересборка и запуск предыдущей версии..."
"${COMPOSE[@]}" build breakfast_lecture_planner
"${COMPOSE[@]}" up -d --remove-orphans

echo "Проверка сайта ${HEALTHCHECK_URL}..."
for attempt in {1..30}; do
    if curl --fail --silent --show-error --location \
        --max-time 10 "${HEALTHCHECK_URL}" > /dev/null; then
        echo "Откат успешно завершён."
        exit 0
    fi

    if [[ "${attempt}" -lt 30 ]]; then
        sleep 2
    fi
done

echo "Предыдущая версия запущена, но сайт не прошёл проверку." >&2
"${COMPOSE[@]}" logs --tail=100 breakfast_lecture_planner >&2 || true
exit 1
