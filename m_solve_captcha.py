from a_captcha_screenshot import get_captcha
from b_crop_image import manipulate_image
from c_read_captcha import extractObjectText
from d_object_detection import detect_objects
from e_click_object import click_on_tiles, click_on_center_of_box
import time


def main():
    
    # 1. Launch browser & take screenshot
    left, top, width, height = get_captcha()
    captcha_image = 'captcha_image.png'
    print(f"[INFO] left: {left}, top: {top}, width: {width}, height: {height}")
    
    # 2. Get user input and crop the image into seperate tiles or one grid
    rows = int(input("Enter number of rows: "))
    columns = int(input("Enter number of columns: "))
    is_one_image = input("Is it one image? (y/n): ").strip().lower() == 'y'
    cropped_image = manipulate_image(captcha_image, True, rows, columns)
    cropped_image = 'cropped_image.png'
    
    # 3. Set object we must find
    object_to_find = extractObjectText('captcha_top.png')
    print(f"[INFO] Set object to find: {object_to_find}")
    
    # 4. Run detection 
    model_path = "./models/yolo11n.pt"
    img, detections, result = detect_objects(cropped_image, model_path, object_to_find)

    # 5. Click on the detected tiles
    macOS = True # MacOS Screenshots render in 2x resolution, have to divide by 2 to get the correct coordinates
    if macOS: 
        tile_width = int(width // columns) // 2
        tile_height = int(height // rows) // 2
        grid_top_left = (int(left // 2), int(top // 2))
    else:
        tile_width = int(width // columns)
        tile_height = int(height // rows)
        grid_top_left = (int(left), int(top))
    print(f"[INFO] Grid top left: {grid_top_left}")
    print("Sleeping for 5 seconds before clicking...")
    time.sleep(5)  # Wait for 2 seconds before clicking
    if is_one_image:
        for box in detections:
            click_on_tiles(box, grid_top_left, tile_width, tile_height, columns, rows)
    else:
        click_on_center_of_box(detections, grid_top_left) # IS yes 
    
    # 6. Click SUBMIT baby

    



if __name__ == "__main__":
    main()