import struct
from multiprocessing import Process, Manager, cpu_count

HEAD = (0x17AB17CD).to_bytes(4, byteorder='big')
TAIL = (0x19BA23DC).to_bytes(4, byteorder='big')
HEAD_LEN = len(HEAD)
TAIL_LEN = len(TAIL)
ENTITY_LEN = 32

ENTITY_FORMAT = struct.Struct('<20siii')


def do_with_record(*record):
    pass


def read_basic(file_path, start, end):
    i = start

    with open(file_path, 'rb') as f:
        while i < end:
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


def read_single(file_path, index, start, end, d):
    with open(file_path, 'rb') as f:
        first_head_start_pos = start
        last_tail_end_pos = end

        for i in range(start, end):
            f.seek(i)
            head_bytes = f.read(HEAD_LEN)
            if head_bytes == HEAD:
                first_head_start_pos = i
                break

        for i in range(end, start, -1):
            f.seek(i)
            tail_bytes = f.read(TAIL_LEN)
            if tail_bytes == TAIL:
                last_tail_end_pos = i + TAIL_LEN
                break

        read_basic(file_path, first_head_start_pos, last_tail_end_pos)
        d[index] = {
            'first_head_start_pos': first_head_start_pos,
            'last_tail_end_pos': last_tail_end_pos
        }


def read_multi_process(file_path, process_num=None):
    if process_num is None:
        process_num = cpu_count()

    m = Manager()
    d = m.dict()
    p_list = []

    with open(file_path, 'rb') as f:
        f.seek(0, 2)
        num_bytes = f.tell()

    part_num_bytes = num_bytes // process_num

    seek_list = []
    for i in range(process_num):
        seek_list.append(i * part_num_bytes)

    seek_list.append(num_bytes)

    for i in range(process_num):
        p = Process(target=read_single, args=(file_path, i, seek_list[i], seek_list[i + 1], d))
        p_list.append(p)

    for p in p_list:
        p.start()

    for p in p_list:
        p.join()

    for i in range(process_num - 1):
        start = d[i]['last_tail_end_pos']
        end = d[i + 1]['first_head_start_pos']
        read_basic(file_path, start, end)


if __name__ == "__main__":
    import time
    file_path = 'data.bat'

    start_time = time.time()

    read_multi_process(file_path)
    end_time = time.time()
    print(end_time - start_time)