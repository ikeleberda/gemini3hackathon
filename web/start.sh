#!/bin/sh
set -e
echo "Synchronizing database schema..."
npx prisma db push --skip-generate
echo "Starting Next.js server..."
exec node server.js
