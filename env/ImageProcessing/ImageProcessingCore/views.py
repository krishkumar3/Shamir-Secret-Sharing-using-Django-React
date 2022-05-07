from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from ImageProcessingCore.serializers import CoreSerializer,ImageOutputsSerializer
from rest_framework import viewsets
from ImageProcessingCore.models import Core,ImageOutputs
from os import path
from math import sqrt
import numpy as np
from random import randint
from datetime import datetime
from pathlib import Path
import hashlib
from PIL import Image
from Crypto import Random
from Crypto.Cipher import AES
from PyQt5 import QtCore, QtGui
import json
import base64
from Crypto.Cipher import AES
import os
import sys
Qt = QtCore.Qt

BASE_DIR = Path(__file__).resolve().parent.parent
output_path = os.path.join(BASE_DIR, 'outputs')
file_name = None
identifier = None
class ImageViewSet(viewsets.ModelViewSet):
    queryset = Core.objects.all()
    serializer_class = CoreSerializer

class ImageOutputsViewSet(viewsets.ModelViewSet):
    queryset = ImageOutputs.objects.all()
    serializer_class = ImageOutputsSerializer

def homepage(request):
    context = {}
    return render(request, "index.html", context)

@csrf_exempt
def getOutputShares(request, id):
    global identifier
    identifier = id
    obj = Core.objects.get(id=id)
    objData = CoreSerializer(obj)
    n = objData.data['n']
    k = objData.data['k']
    path = objData.data['inputImage']
    paths = path.split("/")
    print(paths)
    path = os.path.join(BASE_DIR, 'uploads',paths[2])
    file_name = paths[2]
    print("totalpath: "+path)
    t1 = datetime.now()
    pic = Image.open(path)
    matrix = np.array(pic, np.int32)
    sharesRGB = split_parts_list(n, k, 257, matrix, path)
    print("Partition creation time:")
    print((datetime.now() - t1).seconds)
    context = dict()
    context["n"]= n,
    context["k"]= k,
    context["path"]= path,
    context["time"]= t1

    myKey = "14"
    output_imgs = ImageOutputs.objects.filter(un_id = identifier)
    print(output_imgs)
    return_list = []
    for i in output_imgs:
        val = ImageOutputsSerializer(i)
        # print("share: ",i.values())
        # print("share: ",i['shares'])
        print("share: ", i.shares)
        strimg = base64.b64encode(i.shares.read())
        x = Encrypter(strimg, myKey)
        cipher_text = x.encrypt_image()
        obj = ImageOutputs.objects.filter(un_id = identifier,id = i.id)
        obj.update(cipher =  cipher_text)
        return_list.append(i.shares.name)
    output_list =[]
    print(return_list)
    # for i in return_list:
    #     output_list.append( i.replace("C:\\Users\\krish\\PycharmProjects\\env\\ImageProcessing\\outputs\\","/"))
    # print(output_list)
    return HttpResponse(json.dumps({"images":return_list}))


class LagrangePolynomial:

    def __init__(self, X, Y):
        self.n = len(X)
        self.X = np.array(X)
        self.Y = np.array(Y)
        self.temp = []

    def basis(self, x, i):
        L = [(x - self.X[j]) / (self.X[i] - self.X[j]) for j in range(self.n) if j != i]
        return np.prod(L, axis=0) * self.Y[i]

    def interpolate(self, x):
        p = [self.basis(x, i) for i in range(self.n)]
        return np.sum(p, axis=0)

    def interpolate_img(self, x):
        p = [self.basis_img(x, i) for i in range(self.n)]
        return np.sum(p, axis=0)

    def basis_img(self, x, i):
        L = []
        temp = []
        done = False
        skip = 0
        for k in range(len(self.X[i])):
            if self.X[i][k] in self.temp:
                skip += 1
        for j in range(self.n):
            if j != i:
                cont = False
                for k in range(len(self.X[i])):
                    k += skip
                    if k >= len(self.X[i]):
                        done = True
                        break
                    self.temp.append(self.X[i][k])
                    for m in range(len(self.X[j])):
                        try:
                            if self.X[j][m] in temp or self.X[j][m] == self.X[i][k]:
                                continue
                            calc = (x - self.X[j][m]) / (self.X[i][k] - self.X[j][m])
                            temp.append(self.X[j][m])
                            L.append(calc)
                            cont = True
                            if len(L) == self.n - 1:
                                done = True
                                break
                        except ZeroDivisionError:
                            continue
                        if done:
                            break
                        if cont:
                            break
                    if done:
                        break
                    if cont:
                        break
            if done:
                break
        return np.prod(L, axis=0) * self.Y[i]


def split_parts_list(n, k, prime, img, path_pic):
    h, w, rgb = img.shape
    name, ext = path.splitext(path_pic)
    np_lists = np.zeros(shape=(n, h, w, 3))
    shrs = [[[[] for j in range(w)] for i in range(h)],
            [[[] for j in range(w)] for i in range(h)],
            [[[] for j in range(w)] for i in range(h)]]

    row_count = 0
    for row in img:
        new_rows = np.zeros(shape=(n, w, 3))
        pix_count = 0
        for pix in row:
            if len(pix) == 3:
                r, g, b = pix[0], pix[1], pix[2] #RGB pixel
            else:  #RGBA pixel
                r, g, b = pix[1], pix[2], pix[3]
            p1, p2, p3 = Scheme(r, n, k, prime), Scheme(g, n, k, prime), Scheme(b, n, k, prime)
            sh1, sh2, sh3 = p1.construct_shares_image(), p2.construct_shares_image(), p3.construct_shares_image()
            for i in range(n):
                new_rows[i][pix_count] = [sh1[i + 1], sh2[i + 1],sh3[i + 1]]
            shrs[0][row_count][pix_count] = sh1
            shrs[1][row_count][pix_count] = sh2
            shrs[2][row_count][pix_count] = sh3
            pix_count += 1
        row_count += 1
        v = 0
        for el in range(n):
            np_lists[el][row_count - 1] = new_rows[el]
            v += 1
    i = 0
    name= name.replace("uploads","outputs")
    for image in np_lists:
        new_img = Image.fromarray(image.astype('uint8'))
        image_p = name + "_share" + str(i)
        image_p += ".png"
        print(" image_p: " + image_p)
        print("id:" , identifier)
        new_img.save(image_p)
        print("Creating Image Object")
        output_obj = ImageOutputs(un_id = identifier,shares= image_p)
        output_obj.save()
        print("Next Iteration")
        i += 1
    return shrs


def reconstruct_image(images, k, prime, shares):
    imgs = [np.array(Image.open(i)) for i in images]
    row_count = 0
    mat_len, row_len, rgb = imgs[0].shape
    len_imgs = len(imgs)
    matrix = [[] for i in range(mat_len)]
    need_calc = []
    img_dict = {}
    rec_info = {}
    counter = 0
    for row in imgs[0]:
        rec_pix = [[] for i in range(row_len)]
        pix_count = 0
        for pix in row:
            shares_r = []
            shares_g = []
            shares_b = []
            save = False
            num = 0
            for j in range(len_imgs):
                red, green, blue = imgs[j][row_count][pix_count][0], imgs[j][row_count][pix_count][1], \
                                   imgs[j][row_count][pix_count][2]
                if (red == 0 or blue == 0 or green == 0) and ([row_count, pix_count] not in need_calc):
                    need_calc.append([row_count, pix_count])
                    img_dict[counter] = [red, green, blue]
                    save = True
                    num = j
                shares_r.append(red)
                shares_g.append(green)
                shares_b.append(blue)
            if save:
                rec_info[counter] = [num, shares_r, shares_g, shares_b]
                counter += 1
            r, g, b = int(Scheme.reconstruct_secret_img(shares[0][row_count][pix_count], shares_r, k, prime)), \
                      int(Scheme.reconstruct_secret_img(shares[1][row_count][pix_count], shares_g, k, prime)), \
                      int(Scheme.reconstruct_secret_img(shares[2][row_count][pix_count], shares_b, k, prime))
            if r == 256:
                r = 0
            if g == 256:
                g = 0
            if b == 256:
                b = 0
            rec_pix[pix_count] = [r, g, b]
            pix_count += 1
        matrix[row_count] = rec_pix
        row_count += 1
    matrix = np.asarray(matrix)
    for i in range(len(need_calc)):
        [red, green, blue] = img_dict[i]
        [row_count, pix_count] = need_calc[i]
        [r, g, b] = matrix[row_count][pix_count]
        R, G, B = euclidean_dist(i, need_calc[i][0], need_calc[i][1], [r, g, b], [red, green, blue], rec_info, matrix,
                                 shares, k, prime)
        matrix[need_calc[i][0]][need_calc[i][1]] = [R, G, B]
    return matrix


def euclidean_dist(cnt, row, col, pix, sh_pix, rec_info, rec_pic, shares, k, prime):
    h, w = len(rec_pic), len(rec_pic[0])
    dist1 = 0
    dist2 = 0
    R = sh_pix[0]
    G = sh_pix[1]
    B = sh_pix[2]
    if R == 0:
        R = 256
    if G == 0:
        G = 256
    if B == 0:
        B = 256

    adjacent = []
    sec_adj = []
    temp_rec = rec_pic
    [num, shares_r, shares_g, shares_b] = rec_info[cnt]
    shares_r[num], shares_g[num], shares_b[num] = R, G, B
    r, g, b = Scheme.reconstruct_secret_img(shares[0][row][col], shares_r, k, prime), \
              Scheme.reconstruct_secret_img(shares[1][row][col], shares_g, k, prime), \
              Scheme.reconstruct_secret_img(shares[2][row][col], shares_b, k, prime)
    temp_rec[row][col] = [r, g, b]
    R, G, B = r, g, b

    for j in range(row - 1, row + 2):
        for i in range(col - 1, col + 2):
            if 0 <= i < w and 0 <= j < h and not (j == row and i == col):
                adjacent.append(rec_pic[j][i])
                sec_adj.append(temp_rec[j][i])

    for a in range(len(adjacent)):
        cR = pix[0] - adjacent[a][0]
        cR2 = R - sec_adj[a][0]
        cG = pix[1] - adjacent[a][1]
        cG2 = G - sec_adj[a][1]
        cB = pix[2] - adjacent[a][2]
        cB2 = B - sec_adj[a][2]
        uR = (pix[0] + adjacent[a][0]) / 2
        uR2 = (R + sec_adj[a][0]) / 2
        dist1 += sqrt(cR * cR * (2 + uR / 256) + cG * cG * 4 + cB * cB * (2 + (255 - uR) / 256))
        dist2 += sqrt(cR2 * cR2 * (2 + uR2 / 256) + cG2 * cG2 * 4 + cB2 * cB2 * (2 + (255 - uR2) / 256))

    if dist1 < dist2:
        R, G, B = pix[0], pix[1], pix[2]
    return [R, G, B]



class Scheme(object):
    def __init__(self, s, n, k, p):
        """
        s: secret
        n: total number of shares
        k: recovery threshold
        p: prime, where p > n
        """
        self.s = s
        self.n = n
        self.k = k
        self.p = p
        # Generate random coefficients
        self.coefs = list(dict.fromkeys([randint(1, 65000) for i in range(1, k)]))

    def construct_shares(self):
        self.coefs.append(self.s)
        values = np.polyval(self.coefs, [i for i in range(1, self.n + 1)]) % self.p
        shares = {i: values[i - 1] for i in range(1, self.n + 1)}
        return shares

    def construct_shares_image(self):
        self.coefs.append(self.s)
        values = np.polyval(self.coefs, [i for i in range(1, self.n + 1)]) % self.p
        shares = {}
        for i in range(1, self.n + 1):
            if int(values[i - 1]) != 256:
                if int(values[i - 1]) == 0:
                    shares[self.n + 1] = 256
                shares[i] = int(values[i - 1])
            else:
                shares[i] = 0
                shares[self.n + 1] = 256

        return shares

    @staticmethod
    def reconstruct_secret(shares: dict, inputs: list, k, p):
        if len(shares) < k:
            raise Exception("More shares needed")

        for el in inputs:
            if el not in shares.values():
                raise Exception("Inadequate share")

        list_input = []
        for i in range(len(inputs)):
            list_input.append(int(list(shares.keys())[list(shares.values()).index(inputs[i])]))

        lp = LagrangePolynomial(list_input, [shares[ind] for ind in list_input])
        secret = lp.interpolate(0) % p

        return secret

    @staticmethod
    def reconstruct_secret_img(shares: dict, inputs: list, k, p):
        if len(shares) < k:
            raise Exception("More shares needed")

        for el in inputs:
            if el not in shares.values():
                raise Exception("Inadequate share")

        list_input = []
        vals = np.array(list(shares.values()))
        for i in range(len(inputs)):
            search = inputs[i]
            if inputs[i] == 256:
                search = 0
            ii = np.where(vals == search)[0]
            lii = [list(shares.keys())[i] for i in ii]
            list_input.append(lii)

        lp = LagrangePolynomial(list_input, [shares[ind[0]] for ind in list_input])

        secret = lp.interpolate_img(0) % p
        return secret

class Encrypter:
    def __init__(self, text,key):
        self.text = text
        self.key =  key
    def encrypt_image(self):
        aes = AESCipher(self.key)
        cipher = aes.encrypt(self.text)
        return cipher

class Decrypter:
    def __init__(self, cipher):
        self.cipher = cipher

    def decrypt_image(self, k):
        key = k
        cipher = self.cipher
        aes = AESCipher(key)
        base64_decoded = aes.decrypt(cipher)
        fh = open("decryptedImage.png", "wb")
        fh.write(base64.b64decode(base64_decoded))
        fh.close()
        return (base64.b64decode(base64_decoded))


class AESCipher(object):

    def __init__(self, key):
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs).encode('utf-8')

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]