echo "BUILD START"
echo "----- Switching to Vercel libraries -----"
sed -i 's/-r digitalocean.txt/-r vercel.txt/' requirements/production.txt
echo "----- Installing dependencies -----"
python3.9 -m pip install -r requirements.txt
echo "----- Collecting static files -----"
python3.9 manage.py collectstatic --noinput --clear
if [[ $VERCEL_GIT_COMMIT_REF == "master"|| $VERCEL_GIT_COMMIT_REF == "production" ]] ; then
    echo "----- Migrating database -----"
    python3.9 manage.py migrate
fi
echo "BUILD END"
