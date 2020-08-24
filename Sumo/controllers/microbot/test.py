def mapeo(x):
    val=int.from_bytes(x, "little")
    return int((val - 4281216556) * 100 / (4292861922 - 4281216556))

def test():
    print("soy el test")

negro=b',..\xff'
blanco=b'\xe2\xdf\xdf\xff'

a=test
print(type(a))
