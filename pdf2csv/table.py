import os
import cv2
import imutils
import numpy as np
import pytesseract
import pandas as pd

# average line hight in table
table_line_height =200
# stretch the cropped image by padding
padding = 10
min_area_cell = 500
max_last_height_bonus = 50
def remove_edge(image,border = 3):
    """
    change all color of pixels  in edge to black color (0,0,0)
    this function change image directly.
    border: can be used for specifying width of image that should be converted to black color
    """
    cv2.rectangle(image,(0,0),(image.shape[1],image.shape[0]),(0,0,0),border)
    return image
def endOfCol(image,rect):
    """
    this function return all rects that contain titles in table headers , yellow bar.
    """
    img = image.copy()
    img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    crop = img[rect[1]:rect[1]+rect[3],rect[0]:rect[0]+rect[2]]
    origin_crop = crop.copy()
    kernel = np.ones((15,15),dtype=np.uint8)
    # crop = cv2.erode(crop,kernel)
    crop = cv2.morphologyEx(crop,cv2.MORPH_OPEN,kernel=kernel)
    crop = ~crop
    crop= remove_edge(crop)
    cnts,_ = cv2.findContours(crop,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    rects = []
    for c in cnts:
        if(cv2.contourArea(c)<min_area_cell):
            pass
        else:
            rects.append(cv2.boundingRect(c))
        pass
    def keyfunc(cell):
        return cell[1]
    rects.sort(key=keyfunc)
    real_rects = []
    for i,rect in enumerate(rects):
        global table_line_height
        if(i>0):
            height = rects[i][1]-rects[i-1][1]
            if(height>table_line_height):
                # real_rects.append(rects[i])
                break
            else:
                if(rects[i][1]-rects[i-1][1]<10):
                    continue
                    pass
                real_rects.append(rect)
            pass
        else:
            real_rects.append(rect)
        pass
    return real_rects
    pass
def get_cells(image):
    """
    this function is for getting a rect that contain each cell text.
    """
    image = image.copy()
    img = image.copy()
    image = cv2.cvtColor(image,cv2.COLOR_BGR2HSV,dst=image)

    lower = np.array([21, 39, 64])
    upper = np.array([40, 255, 255])
    mask = cv2.inRange(image, lower, upper)
    kernel = np.ones((15,15),np.uint8)
    close = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    contours, hierarchy = cv2.findContours(close,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    rect = None
    max_area = 0
    if(contours):
        pass
    else:
        return None,None,None,
    for c in contours:
        # compute the center of the contour, then detect the name of the
        # shape using only the contour
        if(cv2.contourArea(c)>max_area):
            max_area = cv2.contourArea(c)
            rect = cv2.boundingRect(c)
            pass
    
    mask = mask[rect[1]:rect[1]+rect[3],rect[0]:rect[0]+rect[2]]
    close = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    close = ~close
    cv2.rectangle(close,(0,0),(close.shape[1],close.shape[0]),color=(0,0,0),thickness=2)
    contours, hierarchy = cv2.findContours(close,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

    rects = []
    for c in contours:
        if(cv2.contourArea(c)<10):
            pass
        else:
            rects.append(cv2.boundingRect(c))
    def keyfunc(cell):
        return cell[0]
        pass
    rects.sort(key=keyfunc)
    rect_firstItem = (rects[0][0],rects[0][1],rects[1][0]-rects[0][0],rects[0][3])
    rect_firstcol = (rect[0],rect[1]+rect[3],rect_firstItem[2]+2,img.shape[0]-rect[1]-rect[3])
    #check the end of first colums
    rows = endOfCol(img.copy(),rect_firstcol)
    return img[rect_firstcol[1]:rect_firstcol[1]+rows[-1][1]+rows[-1][3]+max_last_height_bonus,rect_firstcol[0]:image.shape[0]],rows,rects
    pass

def get_dates(image,rows,rects):
    """
    get all dates values
    """
    result = []
    for i, row in enumerate(rows):
        img = image.copy()
        height = 0
        if(i == (len(rows)-1)):
            height = max_last_height_bonus
        crop = img[row[1]-padding:row[1]+row[3]+padding+height,0:row[0]+row[2]+2]
        crop = cv2.resize(crop,(crop.shape[1]*3,crop.shape[0]*3),dst=crop,interpolation=cv2.INTER_AREA)
        # cv2.imshow("crop",crop)
        # cv2.waitKey(0)
        config = None
        config = "-c tessedit_char_whitelist=01234567890.:, --psm 11"
        text_day = pytesseract.image_to_string(crop,config=config)
        config = config = None
        text_month = pytesseract.image_to_string(crop,config=config)
        for i in range(10):
            text_month = text_month[-4:]
        text_month = text_day + " " + text_month
        # print(text_month)
        result.append(text_month)
        pass
    # print(result)
    return result
    pass
def get_balances(image,rows,rects):
    """
    get all balances values
    """
    result = []
    for i, row in enumerate(rows):
        img = image.copy()
        end_y = 0
        height = 0
        if(i == (len(rows)-1)):
            height = max_last_height_bonus
        if(i+1<len(rows)):
            end_y = rows[i+1][1]
        else:
            end_y = row[1]+row[3]
        crop = img[row[1]-padding:end_y+height,rects[4][0]-100:rects[4][0]+rects[4][2]+padding+10]
        # cv2.imshow("crop",crop)
        # cv2.waitKey(0)
        # config = "-c tessedit_char_whitelist=01234567890.:, --psm 11"
        config = None
        text = pytesseract.image_to_string(crop,config=config)
        result.append(text)
        pass
    # print(result)
    return result
    pass
def get_Credits(image,rows,rects):
    """
    get all Credits values
    """
    result = []
    for i, row in enumerate(rows):
        img = image.copy()
        end_y = 0
        height = 0
        if(i == (len(rows)-1)):
            height = max_last_height_bonus
        if(i+1<len(rows)):
            end_y = rows[i+1][1]
        else:
            end_y = row[1]+row[3]
        crop = img[row[1]-padding:end_y+height,rects[3][0]-50:rects[4][0]-100]
        # crop = cv2.resize(crop,(crop.shape[1]*3,crop.shape[0]*3),dst=crop,interpolation=cv2.INTER_AREA)
        # cv2.imshow("crop",crop)
        # cv2.waitKey(0)
        config = "-c tessedit_char_whitelist=01234567890.:, --psm 11"
        # config = None
        text = pytesseract.image_to_string(crop,config=config)
        print(text)
        result.append(text)
        pass
    # print(result)
    return result
    pass
def get_Debits(image,rows,rects):
    """
    get all Debits values
    """
    result = []
    for i, row in enumerate(rows):
        img = image.copy()
        height = 0
        if(i == (len(rows)-1)):
            height = max_last_height_bonus
        end_y = 0
        if(i+1<len(rows)):
            end_y = rows[i+1][1]
        else:
            end_y = row[1]+row[3]
        crop = img[row[1]-padding:end_y+height,rects[2][0]-60:rects[3][0]-20]
        config = "-c tessedit_char_whitelist=01234567890.:, --psm 11"
        text = pytesseract.image_to_string(crop,config=config)
        result.append(text)
        pass
    # print(result)
    return result
    pass
def get_Transactions(image,rows,rects):
    """
    get all Transactions values
    """
    result = []
    for i, row in enumerate(rows):
        img = image.copy()
        end_y = 0
        height = 0
        if(i == (len(rows)-1)):
            height = max_last_height_bonus
        if(i+1<len(rows)):
            end_y = rows[i+1][1]
        else:
            end_y = row[1]+row[3]
        crop = img[row[1]-padding:end_y+height,rects[1][0]-padding:rects[2][0]-50]
        # cv2.imshow("crop",crop)
        # cv2.waitKey(0)
        text = pytesseract.image_to_string(crop)
        result.append(text)
        pass
    # print(result)
    return result
    pass
def process_image(img, morph_size=(18, 18)):
    """
    this function return panda object that contain all table infos in image
    morph_size is args for opencv. don't change this value.
    """
    img,rows,rects = get_cells(img)
    # cv2.imshow("img",img)
    # cv2.waitKey(0)
    # return pd.DataFrame()
    if(rects):
        pass
    else:
        return pd.DataFrame()
    # cv2.imshow("img",img)
    # cv2.waitKey(0)
    date_result = get_dates(img.copy(),rows,rects)
    trans_result = get_Transactions(img.copy(),rows,rects)
    debit_result = get_Debits(img.copy(),rows,rects)
    credit_result = get_Credits(img.copy(),rows,rects)
    balance_result = get_balances(img.copy(),rows,rects)
    result = pd.DataFrame()
    result['Date'] = date_result
    result['Transaction'] = trans_result
    result['Debit'] = debit_result
    result['Credit'] = credit_result
    result['Balance'] = balance_result
    return result

if __name__ == "__main__":
    in_file = os.path.join("data", "out.jpg")
    img = cv2.imread(os.path.join(in_file))
    result = process_image(img)
    result.to_csv("1.csv")
    pass