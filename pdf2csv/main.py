
import argparse,warnings
from extract_imageonefile import DataEngine
# from extract_image import DataEngine
if __name__ == '__main__':
    import warnings

    warnings.filterwarnings("ignore")
    parser = argparse.ArgumentParser()

    """
    Data Argument
    """
    parser.add_argument('--dirPath', type=str, default="./")
    # path = input("pls enter path of directory:")
    # if(not path):
    #     path = "./"
    args = parser.parse_args()
    # args.dirPath = path
    engine = DataEngine(args)
    engine.run()