#!/bin/sh
# Entrypoint script cho Railway/Docker deployment.
#
# What: Chạy database migration rồi khởi động gunicorn
# Why:  Đặt startup logic ở đây thay vì trong Dockerfile CMD để dễ debug
#       và tránh vấn đề shell expansion khi truyền biến môi trường
# How:  sh entrypoint.sh (được gọi bởi Dockerfile ENTRYPOINT)

set -e  # Dừng ngay nếu có lệnh nào fail

echo "[Entrypoint] Chạy flask db upgrade..."
flask db upgrade

echo "[Entrypoint] Khởi động gunicorn..."
exec gunicorn run:app \
    --bind "0.0.0.0:${PORT:-5000}" \
    --workers 1 \
    --timeout 120 \
    --log-level info
