
import struct
import random
HEAD = (0x17AB17CD).to_bytes(4, byteorder='big')
TAIL = (0x19BA23DC).to_bytes(4, byteorder='big')
HEAD_LEN = len(HEAD)
TAIL_LEN = len(TAIL)
ENTITY_LEN = 32

ENTITY_FORMAT = struct.Struct('<20siii')


def do_with_record(*record):
    pass


def read(file_path):
    with open(file_path, 'rb') as f:
        f.seek(0, 2)
        num_bytes = f.tell()

        i = 0
        while i < num_bytes:
            f.seek(i)
            head_bytes = f.read(HEAD_LEN)

            if head_bytes == HEAD:
                j = i + HEAD_LEN + ENTITY_LEN
                f.seek(j)
                tail_bytes = f.read(TAIL_LEN)
                if tail_bytes == TAIL:
                    f.seek(i + HEAD_LEN)
                    entity = f.read(ENTITY_LEN)
                    name, serialnum, school, gradelevel = ENTITY_FORMAT.unpack(entity)
                    do_with_record(name, serialnum, school, gradelevel)
                    i = j + TAIL_LEN
                else:
                    i += 1
            else:
                i += 1


if __name__ == "__main__":
    import time
    file_path = 'data.bat'

    start_time = time.time()

    read(file_path)
    end_time = time.time()
    print(end_time - start_time)