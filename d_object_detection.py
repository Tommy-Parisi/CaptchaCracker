from ultralytics import YOLO 
import cv2 
import argparse
import os 
from u_captcha_utils import get_captcha_path

def detect_objects(img_path, model_path, target):
    """
    Loads the YOLO model and performs detection on the input image.

    Returns:
        img: The loaded image (numpy array)
        detections: A list of [x1, y1, x2, y2] bounding boxes
    """
    # Load model
    model = YOLO(model_path)
    model_classes = model.names
    model_labels = {v: k for k, v in model_classes.items()}

    # Validate target
    if target not in model_labels:
        raise ValueError(f"Invalid target '{target}'. Must be one of: {list(model_labels.keys())}")
    
    # Load image
    if not os.path.exists(get_captcha_path(img_path)): 
        raise FileNotFoundError(f"Unable to locate: {img_path}")
    
    img = cv2.imread(get_captcha_path(img_path))

    # Predict
    target_label = model_labels[target]
    result = model.predict(source=img, classes=[target_label])[0]
   
    detections = result.boxes.xyxy.cpu().tolist()
    preds = result.boxes.cls.cpu().tolist()
    confs = result.boxes.conf.cpu().tolist()
    
    #  Create a clone of the image to draw our results on 
    draw_img = img.copy() 
    # Draw the detections, labels, and confidence scores on our image
    for d, p, c in zip(detections, preds, confs): 
        label = f"{model_classes[p]}: {int(c*100)}%"
        cv2.rectangle(draw_img, (int(d[0]), int(d[1])), (int(d[2]), int(d[3])), (255, 0, 0), 1)
        cv2.putText(draw_img, label, (int(d[0]), int(d[1] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
    
    cv2.imwrite(get_captcha_path('captcha_detected.png'), draw_img)

    # Return full image and bounding boxes
    return img, detections, result  # result contains preds and confs too if you want
    


def main(): 
    parser = argparse.ArgumentParser(description="An exammple object detection script.")
    parser.add_argument('--model', '-n', type=str, 
                        default='yolo11n', help='The YOLO model to use')
    parser.add_argument('--target', '-t', type=str, 
                        default='traffic light', 
                        help='The target object to detect from the captcha')
    parser.add_argument('--input', '-i', type=str, 
                        default='./example_images/traffic_lights.png', 
                        help='The input image to process')

    args = parser.parse_args()
    # Download and create an instance of the YOLO11 nano model 
    model = YOLO('./models/yolo11n') 
    model_classes = model.names
 
    # Now we need to check to see if the supplied target class exists in the available model classes
    target = args.target
    valid_targets = list(model_classes.values())
    assert target in valid_targets, f"Invalid --target {target} supplied. Target must be one of {valid_targets}"

    # Create a reverse lookup table from the model classes so we can filter out our detections 
    model_labels = {value: key for key, value in model_classes.items()}

    # Read the input image and display it using OpenCV
    img_path = args.input 
    # But first, check to see if the image exists 
    if not os.path.exists(get_captcha_path(img_path)): 
        raise FileNotFoundError(f"Unable to locate: {img_path}")
    
    img = cv2.imread(get_captcha_path(img_path))
    cv2.imshow("Original Image", img) 
    
    ## Use the YOLO11 model to detect the target of the captcha image
    # YOLO11 expects an int label; Use the lookup to get it 
    target_label = model_labels[target]
    # Perform inference with the model 
    yolo_result = model.predict(source=img, classes=[target_label])
    # Extract the predictions, confidence scores and bounding boxes
    preds = yolo_result[0].boxes.cls.cpu().tolist()
    confs = yolo_result[0].boxes.conf.cpu().tolist()
    detections = yolo_result[0].boxes.xyxy.cpu().tolist()

    # Detections are the xy-coordinates of any target objects in our image
    # This is what we can use to determine where to send clicks on the screen
    # Cast our xy-coordinates to integers
    detections = [[int(i) for i in d] for d in detections]
    print(f'{target} detected at the following coordinates: {detections}')

    # Create a clone of the image to draw our results on 
    draw_img = img.copy() 

    # Draw the detections, labels, and confidence scores on our image
    for d, p, c in zip(detections, preds, confs): 
        label = f"{model_classes[p]}: {int(c*100)}%"
        cv2.rectangle(draw_img, (d[0], d[1]), (d[2], d[3]), (255, 0, 0), 1)
        cv2.putText(draw_img, label, (d[0], d[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
    
    cv2.imwrite(get_captcha_path('captcha_detected.png'), draw_img)
    cv2.imshow("Results Image", draw_img)
    cv2.waitKey(0)


if __name__ == '__main__': 
    main()