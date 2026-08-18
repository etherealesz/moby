#!/bin/bash

read -p "What's your package name? " -r PACKAGE_NAME

echo "Setting package name to: $PACKAGE_NAME..."

sed -i.bak \
  "s/\"name\": \".*\"/\"name\": \"$PACKAGE_NAME\"/" package.json && \
  rm package.json.bak

rm -rf \
  node_modules \
  bun.lock \
  bun.block \
  pnpm-lock.yaml \
  package-lock.json \
  yarn.lock

echo "Reinstalling dependencies..."
bun install

rm -f scripts/init.sh
rm -f scripts/init.ps1

echo "Initialization complete, you're all set!"
