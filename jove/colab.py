from google.colab import drive
import importlib.util
import sys

# Mount your drive. It will be at this path: "/content/gdrive/My Drive/"
drive.mount('/content/gdrive', force_remount=True)

sys.path.append('gdrive/My Drive/CS3100Spring20/Jove/')
sys.path.append('gdrive/My Drive/CS3100Spring20/Jove/jove')
sys.path += ['../..',
             '../../3rdparty',
             '../../..',
             '../../../3rdparty',
             '../../../..',
             '../../../../3rdparty']
