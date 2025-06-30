from ultralytics import YOLO

# Load a pretrained YOLO model (recommended for training)
# Note: "yolo11n.pt" is a detection model.
# If you want actual segmentation masks, you should use a segmentation model like "yolo11n-seg.pt".
#model = YOLO("yolo11n.pt")
model = YOLO("./face.pt")

# Perform object detection on an image using the model
results = model("https://ultralytics.com/images/bus.jpg")

# The 'results' object is a list of Results objects, one for each image processed.
# Since we processed a single image, we'll work with results[0].
if results:
    result = results[0]

    # 1. Print the detected classes to console
    print("\nDetected Classes:")
    if result.boxes: # Check if there are any bounding box detections
        class_names = model.names # Get the mapping from class ID to class name [2]
        for box in result.boxes:
            class_id = int(box.cls) # Get the class ID for the current detection [3, 10]
            class_name = class_names[class_id]
            confidence = box.conf.item() # Get the confidence score
            print(f"- {class_name} (Confidence: {confidence:.2f})")
    else:
        print("No objects detected.")

    # 2. Save the segmented/detected image to file
    # The .save() method on a Results object saves the image with detections (bounding boxes for detection models,
    # and masks for segmentation models) drawn on it. [4, 10]
    output_path = "bus_detected.jpg"
    result.save(filename=output_path)
    print(f"\nImage with detections saved to: {output_path}")

    # You can also print the raw results object for more details
    print("\nRaw Results object:")
else:
    print("No results found.")
