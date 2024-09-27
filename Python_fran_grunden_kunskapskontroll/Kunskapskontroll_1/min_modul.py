# Min fina modul

def pluss(a, b):
    """Gives the sum of 2 variables"""
    summan = a+b
    return summan


def change(a):
    """Change letters to jibberish"""
    result = ""  
    for i in a:
        changed = chr(ord(i) + 30)  
        result += changed  
    return result 

text = "Hejsan hoppsan"
skiftad_text = change(text)

print(f"Original text: {text}")
print(f"Skiftad text: {skiftad_text}")
