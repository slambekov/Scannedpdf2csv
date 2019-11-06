
import sys
from pdf2image import convert_from_path
import cv2
import numpy as np
import table
from os import walk
import glob
import sys
import pandas as pd
class DataEngine:
    def __init__(self,args):
        self.args = args
        pass
    def process_last_col(self,result):
        """
        this function is for processing last columns
        """
        def process_val(cell):
            cell = str(cell)
            if(cell):
                pass
            else:
                return ""
            cell = cell.replace('C','')
            cell = cell.replace('R','')
            str_result = cell + "CR"
            return str_result
            pass
        cols = result["Balance"].apply(process_val)
        result["Balance"] = cols
        return result
        pass
    def process_pdf(self,path_pdf):
        """
        this function is just convert pdf in a path to csv file in the path
        """
        try:
            pages = convert_from_path(path_pdf,dpi=300)
            if(len(pages)>1):
                final = []
                for index,page in enumerate(pages):
                    img_object = page
                    opencvImage = cv2.cvtColor(np.array(img_object), cv2.COLOR_RGB2BGR)
                    # opencvImage = cv2.resize(opencvImage,(800,1000))
                    # cv2.imshow("",opencvImage)
                    # cv2.waitKey(0)
                    # exit(0)
                    result = table.process_image(opencvImage)
                    if(result.empty):
                        continue
                    else:
                        pass
                    self.process_last_col(result)
                    final.append(result)
                pass
                path = path_pdf.replace('.pdf','.csv')
                result = pd.concat(final)
                result.to_csv(path)
            else:
                img_object = pages[0]
                opencvImage = cv2.cvtColor(np.array(img_object), cv2.COLOR_RGB2BGR)
                # opencvImage = cv2.resize(opencvImage,(800,1000))
                # cv2.imshow("",opencvImage)
                # cv2.waitKey(0)
                # exit(0)
                result = table.process_image(opencvImage)
                if(result.empty):
                    return
                else:
                    pass
                self.process_last_col(result)
                path = path_pdf.replace('.pdf','.csv')
                result.to_csv(path)
                pass
        finally:
            pass
        pass
    def run(self):
        """
        find all pdf files in a path and convert them all to csv file
        """
        root_dir = self.args.dirPath
        for filename in glob.iglob(root_dir + '**/*.pdf', recursive=True):
            self.process_pdf(filename)
        pass