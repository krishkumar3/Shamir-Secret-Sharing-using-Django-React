from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from ImageProcessingCore.serializers import CoreSerializer, ImageOutputsSerializer, DecryptionSerializer, \
    CustomUserSerializer, \
    UserImageListSerializer
from rest_framework import viewsets
from ImageProcessingCore.models import Core, ImageOutputs, Decryption, CustomUser, UserImageList
from os import path
from math import sqrt
import numpy as np
from random import randint
from datetime import datetime
from pathlib import Path
import hashlib
import jwt
from PIL import Image
from Crypto import Random
from Crypto.Cipher import AES
import json
import base64
import os
import sys
from django.http import FileResponse
import secrets
import string
import ast
from django.core.mail import send_mail
import zlib

BASE_DIR = Path(__file__).resolve().parent.parent
output_path = os.path.join(BASE_DIR, 'outputs')
file_name = None
identifier = None
sharesRGB = []


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Core.objects.all()
    serializer_class = CoreSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


class ImageOutputsViewSet(viewsets.ModelViewSet):
    queryset = ImageOutputs.objects.all()
    serializer_class = ImageOutputsSerializer


class DecryptionViewSet(viewsets.ModelViewSet):
    queryset = Decryption.objects.all()
    serializer_class = DecryptionSerializer


class UserImageListViewSet(viewsets.ModelViewSet):
    queryset = UserImageList.objects.all()
    serializer_class = UserImageListSerializer


def homepage(request):
    context = {}
    return render(request, "index.html", context)

def checker(id):
    print("inside counter")
    obj = UserImageList.objects.get(coreId = id)
    count = obj.count + 1
    if count == 3:
        obj.delete()
    else:
        obj.count = count
        obj.save()

@csrf_exempt
def sharedImages(request, email):
    print("email:", email)
    return_list = []
    objects = UserImageList.objects.filter(useremail=email)
    count = 0
    for i in objects:
        count = count + 1
        return_list.append({"pk": i.coreId, "from": i.fromemail})
    payload = {"count": count, "data": return_list}
    return (HttpResponse(json.dumps(payload)))


@csrf_exempt
def autogenKeys(request, num):
    passwords = []
    for i in range(int(num) + 1):
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(10))
        passwords.append(password)
    print(passwords)
    return HttpResponse(json.dumps(passwords), content_type='text/plain')


@csrf_exempt
def sendEmail(request, email):
    obj = CustomUser.objects.get(email=email)
    send_mail(
        'Forgot Password - Test Email',
        'password:' + obj.password,
        'humesworks1@gmail.com',
        [obj.email],
        fail_silently=False,
    )
    return HttpResponse(200)


@csrf_exempt
def signIn(request, email, password):
    try:
        obj = CustomUser.objects.get(email=email, password=password)
        print(obj.username)
        status = {"status": 200, "reason": ""}
    except:
        error = "Unable to find the User"
        status = {"status": 400, "reason": error}
    finally:
        return HttpResponse(json.dumps(status), content_type='text/plain')


@csrf_exempt
def imagePage(request, file):
    path = os.path.join(BASE_DIR, 'frontend', 'src', 'outputs', file)
    print("totalpath: " + path)
    response = FileResponse(open(path, 'rb'))
    return response


@csrf_exempt
def decryptCipher(request, id):
    # global sharesRGB
    # shareRGB = open("SharesRGB.txt","r")
    # rgbcont = shareRGB.read()
    # sharesRGB = json.loads(rgbcont)
    print(id)
    obj = Decryption.objects.get(id=id)
    key_file = obj.keys.read()
    print(len(key_file))
    decryption_data = jwt.decode(key_file, "secret", algorithms=["HS256"])
    keys = ast.literal_eval(decryption_data["keys"])
    print(keys, "Keys")
    core_obj = Core.objects.get(id=decryption_data["id"])
    sharesRGB = json.loads(core_obj.sharesRGB)
    k = decryption_data["minShares"]
    print("K:", k)
    main_key = keys[-1]
    print("MainKey", main_key)
    cipherText_file = obj.cipher.read()
    print(len(cipherText_file))
    cipherText_file = cipherText_file[2:-1]
    print(len(cipherText_file))
    x = Decrypter(cipherText_file)
    try:
        image = x.decrypt_text(main_key)
        # print(image)
        aes = AESCipher(main_key)
        file = open("cipher_1.txt", 'w+')
        images = []
        try:
            print("Inside Try")
            cipher_shares = aes.decrypt(cipherText_file)
            print("step 1 over")
            file.write(cipher_shares)
            shares = cipher_shares.split("=")
            for i in range(len(shares) - 1):
                shares[i] = shares[i] + '='
            for i in shares:
                print("length:", len(i))
                print("front:", i[:20])
                print("back:", i[-10:])
            iterator = 0
            for i in range(len(shares)):

                content = shares[i]
                if (len(content) == 0 or len(content) == 1 or len(content) == 2):
                    continue
                print("front:", shares[i][:10])
                print("last:", shares[i][-5:])
                current_key = keys[iterator]
                print(current_key)
                try:
                    x = Decrypter(content)
                    image = x.decrypt_image(current_key, iterator)
                except:
                    content = content + "="
                    x = Decrypter(content)
                    image = x.decrypt_image(current_key, iterator)
                finally:
                    iterator = iterator + 1
                    print(i, "success")

            for i in range(int(k)):
                image_path = "C:\\Users\\krish\\PycharmProjects\\Shamir-Secret-Sharing-using-Django-React\\env\\ImageProcessing\\" + "decryptedImage" + str(
                    i) + ".png"
                images.append(image_path)
            print(images)
            matrix = reconstruct_image(images, int(k), 257, sharesRGB)
            new_img = Image.fromarray(matrix.astype('uint8'), 'RGB')
            new_img.save(
                "C:\\Users\\krish\\PycharmProjects\\Shamir-Secret-Sharing-using-Django-React\env\ImageProcessing\\frontend\\src\\outputs\\originalimage" + ".png")
        finally:
            print("tried")
            print(len(sharesRGB))
        status = 200
    except:
        status = 400
    finally:
        return HttpResponse(status)


@csrf_exempt
def decryptSharedImage(request, id,counter):
    try:
        print(id)
        print(counter)
        obj = Decryption.objects.get(id=id)
        key_file = obj.keys.read()
        print(len(key_file))
        decryption_data = jwt.decode(key_file, "secret", algorithms=["HS256"])
        keys = ast.literal_eval(decryption_data["keys"])
        print(keys, "Keys")
        core_obj = Core.objects.get(id=decryption_data["id"])
        sharesRGB = json.loads(core_obj.sharesRGB)
        k = decryption_data["minShares"]
        print("K:", k)
        main_key = keys[-1]
        print("MainKey", main_key)
        cipherText_file = core_obj.finalOutput
        print(len(cipherText_file))
        cipherText_file = cipherText_file[2:-1]
        print(len(cipherText_file))
        x = Decrypter(cipherText_file)
        print("Start:", cipherText_file[:10])
        print("end:", cipherText_file[-10:])
        try:
            image = x.decrypt_text(main_key)
            # print(image)
            aes = AESCipher(main_key)
            file = open("cipher_1.txt", 'w+')
            images = []
            try:
                print("Inside Try")
                cipher_shares = aes.decrypt(cipherText_file)
                print("step 1 over")
                file.write(cipher_shares)
                shares = cipher_shares.split("=")
                for i in range(len(shares) - 1):
                    shares[i] = shares[i] + '='
                for i in shares:
                    print("length:", len(i))
                    print("front:", i[:20])
                    print("back:", i[-10:])
                iterator = 0
                for i in range(len(shares)):
                    content = shares[i]
                    if (len(content) == 0 or len(content) == 1 or len(content) == 2):
                        continue
                    print("front:", shares[i][:10])
                    print("last:", shares[i][-5:])
                    current_key = keys[iterator]
                    print(current_key)
                    try:
                        x = Decrypter(content)
                        image = x.decrypt_image(current_key, iterator)
                    except:
                        content = content + "="
                        x = Decrypter(content)
                        image = x.decrypt_image(current_key, iterator)
                    finally:
                        iterator = iterator + 1
                        print(i, "success")

                for i in range(int(k)):
                    image_path = "C:\\Users\\krish\\PycharmProjects\\Shamir-Secret-Sharing-using-Django-React\\env\\ImageProcessing\\" + "decryptedImage" + str(
                        i) + ".png"
                    images.append(image_path)
                print(images)

                matrix = reconstruct_image(images, int(k), 257, sharesRGB)
                new_img = Image.fromarray(matrix.astype('uint8'), 'RGB')
                new_img.save(
                    "C:\\Users\\krish\\PycharmProjects\\Shamir-Secret-Sharing-using-Django-React\env\ImageProcessing\\frontend\\src\\outputs\\originalimage" + ".png")
            finally:
                print("tried")
                print(len(sharesRGB))
            status = 200
        except:
            print("inner except")
            status = 400
        finally:
            print("inner finally")
            return HttpResponse(status)
    except:
        status = 400
        print("outer except")
        checker(int(counter))
    finally:
        print("outer finally")
        return HttpResponse(status)


@csrf_exempt
def cipherText(request, id):
    obj = Core.objects.get(id=id)
    cipher_total = obj.finalOutput
    response = HttpResponse(cipher_total, content_type='application/text charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="cipher_output.txt"'
    return response


def keysOutput(request, id):
    obj = Core.objects.get(id=id)
    keys = obj.keys
    minShares = obj.k
    shares = obj.n
    data_dict = {"id": id, "keys": keys, "shares": shares, "minShares": minShares}
    encoded_jwt = jwt.encode(data_dict, "secret", algorithm="HS256")
    response = HttpResponse(encoded_jwt, content_type='application/text charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="keys_output.txt"'
    return response


@csrf_exempt
def encryptWithKeys(request, id):
    global identifier
    identifier = id
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    print("body", body)
    mykey = body
    print("Keys:", mykey)
    output_imgs = ImageOutputs.objects.filter(un_id=identifier)
    print(output_imgs)
    output_list = []
    iterator = 0
    ct = []
    for i in output_imgs:
        val = ImageOutputsSerializer(i)
        print("share: ", i.shares)
        strimg = base64.b64encode(i.shares.read())
        print("mykey", mykey[iterator])
        x = Encrypter(strimg, mykey[iterator])
        cipher_text = x.encrypt_image()
        obj = ImageOutputs.objects.get(un_id=identifier, id=i.id)
        obj.cipher = cipher_text
        ct.append(cipher_text)
        obj.save()
        item = i.shares.name
        item = item.replace(
            'C:\\Users\\krish\\PycharmProjects\\Shamir-Secret-Sharing-using-Django-React\\env\\ImageProcessing\\frontend\\src\\outputs\\',
            "")
        output_list.append(str(item))
        iterator = iterator + 1
    print(output_list)
    cts = b' '.join(ct)
    print(len(cts))
    obj = Core.objects.get(id=id)
    obj_shares = ImageOutputs.objects.filter(un_id=id)
    cipher_total = ""

    for i in obj_shares:
        cipher_total = cipher_total + i.cipher
        print(len(i.cipher))
    cts = b' '.join(ct)
    obj.cipher = cipher_total
    print("check:", mykey[iterator])
    file = open("cipher_1.txt", 'w+')
    # encoded_cipher_total = bytes(cipher_total, 'utf-8')
    encoded_cipher_total = cts
    final_aes = Encrypter(encoded_cipher_total, mykey[iterator])
    final_cipher_text = final_aes.encrypt_image()
    obj.finalOutput = final_cipher_text
    obj.keys = json.dumps(mykey)
    obj.save()
    file.write(str(final_cipher_text))

    return HttpResponse("Encryption Successful")


@csrf_exempt
def getOutputShares(request, id):
    global identifier
    global sharesRGB
    identifier = id
    obj = Core.objects.get(id=id)
    objData = CoreSerializer(obj)
    n = objData.data['n']
    k = objData.data['k']
    path = objData.data['inputImage']
    paths = path.split("/")
    print(paths)
    path = os.path.join(BASE_DIR, 'uploads', paths[2])
    file_name = paths[2]
    print("totalpath: " + path)
    t1 = datetime.now()
    pic = Image.open(path)
    matrix = np.array(pic, np.int32)
    sharesRGB = split_parts_list(n, k, 257, matrix, path)
    obj.sharesRGB = json.dumps(sharesRGB)
    obj.save()
    file = open("SharesRGB.txt", "w+")
    file.write(json.dumps(sharesRGB))
    print("Partition creation time:")
    print((datetime.now() - t1).seconds)
    context = dict()
    context["n"] = n
    context["k"] = k
    context["path"] = path
    context["time"] = t1

    output_imgs = ImageOutputs.objects.filter(un_id=identifier)
    print(output_imgs)
    output_list = []
    for i in output_imgs:
        val = ImageOutputsSerializer(i)
        print("share: ", i.shares)
        item = i.shares.name
        item = item.replace(
            'C:\\Users\\krish\\PycharmProjects\\Shamir-Secret-Sharing-using-Django-React\\env\\ImageProcessing\\frontend\\src\\outputs\\',
            "")
        output_list.append(str(item))
    print(output_list)
    return HttpResponse(json.dumps({"images": output_list}))


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
                            # print("checking value:",self.X[j][m],type(self.X[j][m]),"value of x:",x,type(x))
                            calc = (x - int(self.X[j][m])) / (int(self.X[i][k]) - int(self.X[j][m]))
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
                r, g, b = pix[0], pix[1], pix[2]  # RGB pixel
            else:  # RGBA pixel
                r, g, b = pix[1], pix[2], pix[3]
            p1, p2, p3 = Scheme(r, n, k, prime), Scheme(g, n, k, prime), Scheme(b, n, k, prime)
            sh1, sh2, sh3 = p1.construct_shares_image(), p2.construct_shares_image(), p3.construct_shares_image()
            for i in range(n):
                new_rows[i][pix_count] = [sh1[i + 1], sh2[i + 1], sh3[i + 1]]
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
    name = name.replace("uploads", "frontend\src\outputs")
    for image in np_lists:
        new_img = Image.fromarray(image.astype('uint8'))
        image_p = name + "_share" + str(i)
        image_p += ".png"
        print(" image_p: " + image_p)
        print("id:", identifier)
        new_img.save(image_p)
        print("Creating Image Object")
        output_obj = ImageOutputs(un_id=identifier, shares=image_p)
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
        # print("polynomial:",values)
        shares = {i: values[i - 1] for i in range(1, self.n + 1)}
        return shares

    def construct_shares_image(self):
        self.coefs.append(self.s)
        values = np.polyval(self.coefs, [i for i in range(1, self.n + 1)]) % self.p
        # print("polynomial:",values)
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
        # print("working....")
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
    def __init__(self, text, key):
        self.text = text
        self.key = key

    def encrypt_image(self):
        aes = AESCipher(self.key)
        cipher = aes.encrypt(self.text)
        return cipher


class Decrypter:
    def __init__(self, cipher):
        self.cipher = cipher

    def decrypt_text(self, k):
        key = k
        cipher = self.cipher
        aes = AESCipher(key)
        base64_decoded = aes.decrypt(cipher)
        return (base64.b64decode(base64_decoded))

    def decrypt_image(self, k, i=0):
        key = k
        cipher = self.cipher
        aes = AESCipher(key)
        base64_decoded = aes.decrypt(cipher)
        file_name = "decryptedImage" + str(i) + ".png"
        fh = open(file_name, "wb")
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
        return s[:-ord(s[len(s) - 1:])]
