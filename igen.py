from PIL import Image, ImageDraw, ImageFont

def create_image(text, width=1080, height=1080, font_family="fonts/MontserratAlternates-Regular.ttf", 
                     font_size=45, font_color="darkblue", bg_color="white", 
                     output_path="text_image.png"):
    
    img = Image.new('RGB', (width, height), bg_color)
    
    # Create a drawing context
    draw = ImageDraw.Draw(img)
    
    # Load font
    try:
        # Try to load custom font
        font = ImageFont.truetype(font_family, font_size)
    except OSError:
        # Fall back to default font if custom font not found
        print(f"Font '{font_family}' not found, using default font")
        font = ImageFont.load_default()
    
    # Handle multi-line text
    lines = text.strip().split('\n')
    
    # Calculate dimensions for multi-line text
    line_heights = []
    line_widths = []
    
    for line in lines:
        line = line.strip()  # Remove leading/trailing whitespace
        if line:  # Only process non-empty lines
            bbox = draw.textbbox((0, 0), line, font=font)
            line_widths.append(bbox[2] - bbox[0])
            line_heights.append(bbox[3] - bbox[1])
    
    # Calculate total text dimensions
    max_line_width = max(line_widths) if line_widths else 0
    total_text_height = sum(line_heights) + (len(line_heights) - 1) * 10  # Add spacing between lines
    
    # Calculate starting position to center the entire text block
    start_x = (width - max_line_width) // 2
    start_y = (height - total_text_height) // 2
    
    # Draw each line
    current_y = start_y
    for i, line in enumerate(lines):
        line = line.strip()
        if line:  # Only draw non-empty lines
            # Center each line individually (optional - comment out if you want left-aligned)
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            line_x = (width - line_width) // 2
            
            draw.text((line_x, current_y), line, font=font, fill=font_color)
            current_y += line_heights[min(i, len(line_heights)-1)] + 10  # Move to next line

    # Save the image
    img.save(output_path)
    print(f"Image saved as: {output_path}")
    
    return img

# Example with long text
if __name__ == "__main__":
    create_image(
        "this is a test",
        font_color="darkblue",
    )