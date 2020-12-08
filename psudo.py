def find_charachters_in_image(image):
    grey_image = gray_scale(image)
    blur_image = blur(grey_image)
    thresh_image = threshold(blur_image)
    squares = find_squares(thresh_image)

    for square in squares:
        if square is within_a_square:
            cropped = perspective_correction(square)
            character = character_recognition(cropped)

            if character:
                colour = calculate_color(square)
            
    return [character, colour]


def character_recognition(image):
    shape = find_edges(image)
    letter = k_nearest.find_letter(shape)
    return letter


def calculate_color(image):
    colour_regions = split_into_two_colour_regions(image)
    colour = find_dominant(colour_regions)
    return colour


