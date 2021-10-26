coverage run --source=polog --omit="*tests*" -m pytest --cache-clear
coverage html
open htmlcov/index.html
pygount polog --suffix=py --format=summary
