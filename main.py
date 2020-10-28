import os
from common import check_model_with_custom_bnc

full_name = os.path.abspath('.')+'\\samples\\'+"c-fat500-2"
size, is_timeout = check_model_with_custom_bnc(full_name+'.clq')