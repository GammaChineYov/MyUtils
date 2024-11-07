def bv2av(bv):
    table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
    tr = {}
    for i in range(58):
        tr[table[i]] = i
    s = [11, 10, 3, 8, 4, 6]
    xor = 177451812
    add = 8728348608
    r = 0
    for i in range(6):
        r += tr[bv[s[i]]] * 58 ** i
    return (r - add) ^ xor

def av2bv(av):
    table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
    tr = {}
    for i in range(58):
        tr[i] = table[i]
    s = [11, 10, 3, 8, 4, 6]
    xor = 177451812
    add = 8728348608
    av = (int(av) ^ xor) + add
    r = list('BV1  4 1 7  ')
    for i in range(6):
        r[s[i]] = tr[av // 58 ** i % 58]
    return ''.join(r)

if __name__ == "__main__":
    # bv->av->bv可能不同，但再转一遍还是同样的av，与转换网站结果一致
    bv = "BV1JLDwYTEzt"
    av = bv2av(bv)
    print(bv, av)
    print(bv, av2bv(av))
    print(bv, bv2av(av2bv(av)))