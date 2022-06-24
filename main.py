# import imagecodecs
import argparse
import csv
import numpy
import pathlib
from pathlib import Path
import skimage.io
import skimage.measure
from typing import List


def find_images_from_directories(directories_parameter: str, dictionary_parameter: dict) -> List[Path]:
    # Finds images in directories
    list_of_image_paths = []
    for path in pathlib.Path(directories_parameter).iterdir():
        is_image = check_file_is_image(path)
        if is_image:
            list_of_image_paths.append(path)
            save_image_name_to_dictionary(path, dictionary_parameter)
    return list_of_image_paths


def check_file_is_image(path: pathlib.Path) -> bool:
    # Checks if file is a ".tiff" image and returns True if so
    if path.is_file():
        open_path = open(path, 'r').name
        if ".tif" in open_path:
            return True


def save_image_name_to_dictionary(path: pathlib.Path, dictionary_parameter: dict):
    # The name of the image is added to the dictionary
    image_name = path.name
    check_for_duplicates = True
    counter = 1
    while check_for_duplicates:
        # If the name is a duplicate, it will be constantly renamed until it isn't
        if image_name in dictionary_parameter:
            counter += 1
            image_name = path.name.replace(".tif", f"({counter})") + ".tif"
        else:
            check_for_duplicates = False
    dictionary_parameter[image_name] = []


def load_images(image_path_list_parameter: List[Path], dictionary_parameter: dict) -> List[numpy.ndarray]:
    # Reads and loads images into list
    list_of_images = []
    counter = 0
    for image_path in image_path_list_parameter:
        current_image = skimage.io.imread(image_path, plugin="tifffile")
        is_blank = check_image_is_blank(current_image)
        if is_blank:
            # Blank images are ignored
            key = list(dictionary_parameter.keys())[counter]
            dictionary_parameter.pop(key)
            counter -= 1
        else:
            list_of_images.append(current_image)
        counter += 1
    return list_of_images


def check_image_is_blank(current_image: numpy.ndarray) -> bool:
    # Returns true if first line of image is blank
    if sum(current_image[0]) / len(current_image[0]) < 1:
        return True


def get_image_metrics(list_of_images: List[numpy.ndarray], dictionary_parameter: dict) -> dict:
    # Gets all metrics for image quality of each image
    counter = 0
    for image in list_of_images:
        signal_noise = calculate_signal_noise(image)
        image_blur = calculate_image_blur(image)
        save_image_metrics_to_dictionary(counter, signal_noise, image_blur, dictionary_parameter)
        counter += 1
    return dictionary_parameter


def calculate_signal_noise(current_image: numpy.ndarray) -> float:
    # Calculates signal noise ratio of image
    mean_of_image = numpy.mean(current_image)
    standard_deviation_of_image = numpy.std(current_image)
    signal_noise_ratio = (mean_of_image ** 2 / standard_deviation_of_image ** 2)
    return signal_noise_ratio


def calculate_image_blur(current_image: numpy.ndarray) -> float:
    # Calculates blurriness of image and returns value 0-1
    return skimage.measure.blur_effect(current_image)


def save_image_metrics_to_dictionary(current_image: int, signal_noise_parameter: float, image_blur_parameter: float,
                                     dictionary_parameter: dict):
    # The metrics of each image are added to the dictionary with their corresponding image names
    key = list(dictionary_parameter.keys())[current_image]
    key = ensure_key_in_dictionary(current_image, key, dictionary_parameter)
    dictionary_parameter[key] = [signal_noise_parameter, image_blur_parameter]


def ensure_key_in_dictionary(current_image: int, key_parameter: str, dictionary_parameter: dict) -> str:
    # Check that image name is not a duplicate, and if it is, rename it
    key_in_dictionary = False
    counter = 1
    while not key_in_dictionary:
        if key_parameter not in dictionary_parameter:
            counter += 1
            key_parameter = str(list(dictionary_parameter.keys())[current_image]) + f"({counter})"
        else:
            key_in_dictionary = True
    return key_parameter


def export_dictionaries(directory_parameter: str, dictionary_parameter: dict) -> str:
    file = open(directory_parameter + ".csv", 'w')
    writer = csv.writer(file)
    writer.writerow(["Image Name", "Signal Noise Ratio", "Blurriness (0-1)"])
    for i in range(len(dictionary_parameter)):
        writer.writerow([list(dictionary_parameter.keys())[i],
                         list(dictionary_parameter.values())[i][0], list(dictionary_parameter.values())[i][1]])
    file.close()
    return file.name.split('/')[-1]


def check_if_csv_save_already_exists(directory: str, current_folder_parameter: str) -> bool:
    try:
        open(directory + ".csv", 'x')
    except FileExistsError:
        file = open(directory + ".csv", 'w')
        print(f"\x1b[2K \033[5;32;49mA save for the folder {current_folder_parameter}\033[5;32;49m"
              f" already exists, would you like overwrite it? [Y] or [N] ", end="\r")
        overwrite = input("\n")
        while True:
            if overwrite.upper() == "Y" or overwrite.upper() == "YES":
                overwrite = True
                break
            elif overwrite.upper() == "N" or overwrite.upper() == "NO":
                overwrite = False
                break
            print(f"\x1b[2K \033[5;32;49mTry again, [Y] or [N]\033[5;32;49m")
            overwrite = input()
        if overwrite:
            file.truncate(0)
            file.close()
            return False
        else:
            return True


def main(directories_parameter: list):
    # Main function
    style_line = "\x1b[2K \033[5;32;49m"
    print()
    for i in range(len(directories_parameter)):
        dictionary = {}
        directory = directories_parameter[i]
        current_folder = "\033[1;32;40m" + directory.split('/')[-1] + "\033[0;0m"
        csv_exists = check_if_csv_save_already_exists(directory, current_folder)

        if not csv_exists:
            print(f"{style_line}Finding images for: {current_folder}", end="\r")
            image_path_list: List[Path] = find_images_from_directories(directory, dictionary)
            # Finds images in directories
            print(f"{style_line}Loading images for: {current_folder}", end="\r")
            image_list: List[numpy.ndarray] = load_images(image_path_list, dictionary)
            # Reads and loads images into list
            print(f"{style_line}Processing images for: {current_folder}", end="\r")
            dictionary: dict = get_image_metrics(image_list, dictionary)
            # Gets all metrics for image quality of each image and saves to dictionary
            print(f"{style_line}Saving images for: {current_folder}", end="\r")
            csv_save_name: str = export_dictionaries(directory, dictionary)
            print(f"\x1b[2K \033[5;34;49m\rSaving complete for {csv_save_name}\033[0;0m")


if __name__ == '__main__':
    # Process command line input before main function is called
    parser = argparse.ArgumentParser(description='Get image quality metrics.')
    parser.add_argument('p', nargs='*', type=str, help='The path of the images')
    arguments = parser.parse_args()
    directories = arguments.p

    if len(directories) == 0:
        directories = [input("Name a directory (use command line to enter multiple directories): ")]
        for image_dir in directories:
            if not Path(image_dir).exists():
                msg = f"Directory {image_dir} doesn't exist"
                raise FileNotFoundError(msg)

    main(directories)
