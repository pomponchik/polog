coverage run --source=polog --omit="*tests*" -m pytest
coverage html
open htmlcov/index.html
