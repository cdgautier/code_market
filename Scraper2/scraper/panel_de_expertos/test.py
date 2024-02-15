def string_to_ascii(string):
    ascii_values = []
    for char in string:
        ascii_values.append(ord(char))
    return ascii_values

# Ejemplo de uso
input_string_pdf = "02. Res. Ex. N° 02 que Aprueba Bases y llama a licitación"
input_string_txt = "02. Res. Ex. N° 02 que Aprueba Bases y llama a licitación"
ascii_values = string_to_ascii(input_string_pdf)
print("ASCII values of '{}' are: {}".format(input_string_pdf, ascii_values))