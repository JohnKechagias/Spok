#!/bin/sh

source venv/bin/activate
pyinstaller --clean spok.spec

mkdir dist/assets
mkdir dist/certificates

cp -R assets/icons dist/assets/icons
cp -R fonts dist/fonts
cp -R templates dist/templates
cp -R userlists dist/userlists
cp config.ini dist/config.ini
cp LICENSE dist/LICENSE
cp README.md dist/README.md

touch dist/emailSignarure.html
