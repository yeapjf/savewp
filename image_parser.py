import struct, imghdr

def test_jpeg(h, f):
    # SOI APP2 + ICC_PROFILE
    if h[0:4] == '\xff\xd8\xff\xe2' and h[6:17] == b'ICC_PROFILE':
        print "A"
        return 'jpeg'

    # SOI APP14 + Adobe
    if h[0:4] == '\xff\xd8\xff\xee' and h[6:11] == b'Adobe':
        return 'jpeg'

    # SOI DQT
    if h[0:4] == '\xff\xd8\xff\xdb':
        return 'jpeg'

imghdr.tests.append(test_jpeg)

def get_image_size(fname):
    """Determines the image type of input file and returns its size.

    Keyword arguments:
    fname -- Name of the file.
    width -- Width of the image.
    height -- Height of the image.
    """

    with open(fname, 'rb') as fhandle:
        head = fhandle.read(24)
        if len(head) != 24:
            return

        what = imghdr.what(None, head)

        if what == 'png':
            check = struct.unpack('>i', head[4:8])[0]

            if check != 0x0d0a1a0a:
                return

            width, height = struct.unpack('>ii', head[16:24])
        elif what == 'gif':
            width, height = struct.unpack('<HH', head[6:10])
        elif what == 'jpeg':
            try:
                fhandle.seek(0)
                size = 2
                ftype = 0

                while not 0xc0 <= ftype <= 0xcf or ftype in (0xc4, 0xc8, 0xcc):
                    fhandle.seek(size, 1)
                    byte = fhandle.read(1)

                    while ord(byte) == 0xff:
                        byte = fhandle.read(1)

                    ftype = ord(byte)
                    size = struct.unpack('>H', fhandle.read(2))[0] - 2

                fhandle.seek(1, 1)
                height, width = struct.unpack('>HH', fhandle.read(4))
            except Exception:
                return
        else:
            return

        return width, height
