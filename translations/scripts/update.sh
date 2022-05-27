cd ..
cd ..
. .env/Scripts/activate
pybabel extract -o translations/messages.pot .
pybabel update -i translations/messages.pot -d translations
