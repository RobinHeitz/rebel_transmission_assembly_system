# %%

from PIL import Image
import io, base64

# def resize_image(path, size, output_path):

#     image = Image.open(path)
#     image = image.resize(size,Image.ANTIALIAS)
#     image.save(fp=output_path)



# path = "gui/assembly_pictures/"
# output_path = path

# output_name = lambda i: f"step_{i}_resize.png"

# for i in range(1,4):

#     pic = path + f"step{i}.png"
#     output_path = path + output_name(i)

#     resize_image(pic, (300,300), output_path)

    



def resize_bin_output(path, size):
    
    image = Image.open(path)
    image = image.resize(size, Image.ANTIALIAS)
    output = io.BytesIO()
    image.save(output, format="PNG")
    return base64.b64encode(output.getvalue())


p = "gui/assembly_pictures/cable_connected.png"
resize_bin_output(p, (300,300))
