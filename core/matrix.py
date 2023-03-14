from random import randint
import copy


class MatrixError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = 'Error'

    def __str__(self):
        return self.message


class Matrix:
    def __init__(self, mtrx):
        for i in range(1, len(mtrx)):
            if len(mtrx[i]) != len(mtrx[0]):
                raise ValueError('It is not a matrix')
        self.size_n = len(mtrx)
        self.size_m = len(mtrx[0])
        self.mtrx = mtrx

    def __str__(self):
        width = 0
        s = '\n'
        for i in range(self.size_n):
            for j in range(self.size_m):
                try:
                    width = max(width, len('{:6g}'.format(self.mtrx[i][j])))
                except Exception:
                    width = max(width, len(str(self.mtrx[i][j])))
        for i in range(self.size_n):
            for j in range(self.size_m):
                try:
                    s += '{0:<{1}.6g}'.format(self.mtrx[i][j], width) + '  '
                except Exception:
                    s += '{0:<{1}}'.format(self.mtrx[i][j], width) + '  '
            s += '\n'
        return s + '\b\b\b'

    def transpose(self):
        """Транспонирует квадратную матрицу"""
        if self.size_n == self.size_m:
            for i in range(self.size_n):
                for j in range(i + 1, self.size_m):
                    self.mtrx[i][j], self.mtrx[j][i] = self.mtrx[j][i], self.mtrx[i][j]
        elif self.size_n < self.size_m:
            for i in range(self.size_m - self.size_n):
                self.mtrx.append([0] * self.size_m)
            for i in range(self.size_m):
                for j in range(i + 1, self.size_m):
                    self.mtrx[i][j], self.mtrx[j][i] = self.mtrx[j][i], self.mtrx[i][j]
            self.size_n, self.size_m = self.size_m, self.size_n
            for j in range(self.size_n):
                self.mtrx[j] = self.mtrx[j][:self.size_m]
        else:
            for j in range(self.size_n):
                self.mtrx[j] += [0] * (self.size_n - self.size_m)
            for i in range(self.size_n):
                for j in range(i + 1, self.size_n):
                    self.mtrx[i][j], self.mtrx[j][i] = self.mtrx[j][i], self.mtrx[i][j]
            self.size_n, self.size_m = self.size_m, self.size_n
            self.mtrx = self.mtrx[:self.size_n]

    def determinant(self):
        """Нахождение определителя квадратной матрицы"""
        if self.size_n != self.size_m:
            raise MatrixError('Matrix is not square')
        a = copy.deepcopy(self.mtrx)
        det = 1
        for i in range(self.size_n):
            for j in range(i):
                if a[i][j] != 0:
                    if abs(a[j][j]) > 1e-12:
                        c = a[i][j] / a[j][j]
                        a[i][j] = 0
                        for k in range(j + 1, self.size_n):
                            a[i][k] -= c * a[j][k]
                    else:
                        for k in range(self.size_n):
                            a[i][k], a[j][k] = a[j][k], a[i][k]
                        det *= (-1)
        for i in range(self.size_n):
            det *= a[i][i]
        return det

    def __mul__(self, other):
        if other.__class__.__name__ != 'Matrix':
            a = []
            for i in range(self.size_n):
                a.append([])
                for j in range(self.size_m):
                    a[i].append(self.mtrx[i][j] * other)
            return Matrix(a)
        if self.size_m != other.size_n:
            raise MatrixError('Matrices have different sizes')
        c = Matrix([[0] * other.size_m for i in range(self.size_n)])
        for i in range(self.size_n):
            for j in range(other.size_m):
                s = 0
                for k in range(other.size_n):
                    s += self.mtrx[i][k] * other.mtrx[k][j]
                c.mtrx[i][j] = s
        return c

    def __add__(self, other):
        if other.__class__.__name__ != 'Matrix':
            a = []
            for i in range(self.size_n):
                a.append([])
                for j in range(self.size_m):
                    a[i].append(self.mtrx[i][j] + other)
            return Matrix(a)
        if self.size_n != other.size_n or self.size_m != other.size_m:
            raise MatrixError('Matrices have different sizes')
        c = Matrix([[0] * self.size_m for i in range(self.size_n)])
        for i in range(self.size_n):
            for j in range(self.size_m):
                c.mtrx[i][j] = self.mtrx[i][j] + other.mtrx[i][j]
        return c

    def __eq__(self, other):
        if other.__class__.__name__ != 'Matrix':
            return False
        if self.size_n != other.size_n or self.size_m != other.size_m:
            return False
        for i in range(self.size_n):
            if self.mtrx[i] != other.mtrx[i]:
                return False
        return True

    def __sub__(self, other):
        if other.__class__.__name__ != 'Matrix':
            a = []
            for i in range(self.size_n):
                a.append([])
                for j in range(self.size_m):
                    a[i].append(self.mtrx[i][j] - other)
            return Matrix(a)
        if self.size_n != other.size_n or self.size_m != other.size_m:
            raise MatrixError('Matrices have different sizes')
        c = Matrix([[0] * self.size_m for i in range(self.size_n)])
        for i in range(self.size_n):
            for j in range(self.size_m):
                c.mtrx[i][j] = self.mtrx[i][j] - other.mtrx[i][j]
        return c

    def __pow__(self, power, modulo=None):
        if not self.is_square():
            raise MatrixError('Matrix is not square')
        if power < 0:
            a = self.opposite()
            power = -power
        elif power == 0:
            return Matrix([[0] * i + [1] + [0] * (self.size_n - i - 1) for i in range(self.size_n)])
        else:
            a = self.__copy__()
        for i in range(power - 1):
            a *= a
        return a

    def __copy__(self):
        return Matrix(copy.deepcopy(self.mtrx))

    def is_square(self):
        if self.size_n == self.size_m:
            return True
        return False

    def make_square(self):
        if self.is_square():
            return
        if self.size_n < self.size_m:
            self.mtrx += [[0] * self.size_m for i in range(self.size_m - self.size_n)]
        self.size_n = self.size_m
        for i in range(self.size_n):
            self.mtrx[i] += [0] * (self.size_n - self.size_m)
        self.size_m = self.size_n

    def rang(self):
        a = self.__copy__()
        if not a.is_square():
            a.make_square()
        a = a.mtrx
        rank = 0
        for i in range(self.size_n):
            for j in range(i):
                if a[i][j] != 0:
                    if abs(a[j][j]) > 1e-12:
                        c = a[i][j] / a[j][j]
                        a[i][j] = 0
                        for k in range(j + 1, self.size_n):
                            a[i][k] -= c * a[j][k]
                    else:
                        for k in range(self.size_n):
                            a[i][k], a[j][k] = a[j][k], a[i][k]
        for i in range(self.size_n):
            if abs(a[i][i]) > 1e-10:
                rank += 1
        return rank

    def opposite(self):
        """Нахождение обратной матрицы"""
        if not self.is_square():
            raise MatrixError('Matrix is not square')
        n = self.size_n
        a = [self.mtrx[i] + [0] * i + [1] + [0] * (n - i - 1) for i in range(n)]
        for i in range(1, n):
            for j in range(i):
                if a[j][j] != 0:
                    v = a[i][j] / a[j][j]
                    for k in range(2 * n):
                        a[i][k] -= v * a[j][k]
                else:
                    for k in range(2 * n):
                        a[i][k], a[j][k] = a[j][k], a[i][k]
        for i in range(n - 1, -1, -1):
            for j in range(i + 1, n):
                if a[j][j] != 0:
                    v = a[i][j] / a[j][j]
                    for k in range(2 * n):
                        a[i][k] -= v * a[j][k]
                else:
                    raise MatrixError('this matrix is degenerate')
        for i in range(n):
            if a[i][i] != 0:
                for j in range(n, 2 * n):
                    a[i][j] /= a[i][i]
            else:
                raise MatrixError('this matrix is degenerate')
            a[i] = a[i][n:]
        return Matrix(a)


def transpose(matrix):
    """Транспонирует квадратную матрицу"""
    if len(matrix) != len(matrix[0]):
        raise MatrixError('Matrix is not square')
    a = []
    for i in range(len(matrix)):
        a.append(matrix[i].copy())
    for i in range(len(matrix)):
        for j in range(i + 1, len(matrix)):
            matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
    return matrix


def determinant_minor(matrix):
    """Нахождение определителя квадратной матрицы"""
    if len(matrix) != len(matrix[0]):
        raise MatrixError('Matrix is not square')
    if len(matrix) == 1:
        return matrix[0][0]
    first_column = []
    a = []
    for i in range(len(matrix)):
        first_column.append(matrix[i][0])
        a.append(matrix[i].copy())
        a[i].pop(0)
    det = 0
    for i in range(len(first_column)):
        b = a.copy()
        b.pop(i)
        det += (-1) ** i * first_column[i] * determinant_minor(b)
    return det


def multiply(matrix1, matrix2):
    """Умножает две матрицы"""
    if len(matrix1[0]) != len(matrix2):
        raise MatrixError('Matrices have different sizes')
    c = [[0] * len(matrix2[0]) for i in range(len(matrix1))]
    for i in range(len(matrix1)):
        for j in range(len(matrix2[0])):
            s = 0
            for k in range(len(matrix2)):
                s += matrix1[i][k] * matrix2[k][j]
            c[i][j] = s
    return c


def opposite_whis_det(matrix):
    det = 1 / determinant(matrix)
    a = []
    for i in range(len(matrix)):
        a.append([])
        for j in range(len(matrix)):
            b = []
            for k in range(len(matrix)):
                if k != i:
                    c = matrix[k].copy()
                    c.pop(j)
                    b.append(c)
            a[i].append((-1) ** (i + j) * determinant(b) * det)
    return transpose(a)


def opposite(matrix):
    """Нахождение обратной матрицы"""
    if len(matrix) != len(matrix[0]):
        raise MatrixError('Matrix is not square')
    n = len(matrix)
    a = [matrix[i] + [0] * i + [1] + [0] * (n - i - 1) for i in range(n)]
    for i in range(1, n):
        for j in range(i):
            if a[j][j] != 0:
                v = a[i][j] / a[j][j]
                for k in range(2 * n):
                    a[i][k] -= v * a[j][k]
            else:
                for k in range(2 * n):
                    a[i][k], a[j][k] = a[j][k], a[i][k]
    for i in range(n - 1, -1, -1):
        for j in range(i + 1, n):
            if a[j][j] != 0:
                v = a[i][j] / a[j][j]
                for k in range(2 * n):
                    a[i][k] -= v * a[j][k]
            else:
                raise MatrixError('this matrix is degenerate')
    for i in range(n):
        if a[i][i] != 0:
            for j in range(n, 2 * n):
                a[i][j] /= a[i][i]
        else:
            raise MatrixError('this matrix is degenerate')
        a[i] = a[i][n:]
    return a


def determinant(matrix):
    """Нахождение определителя квадратной матрицы"""
    if len(matrix) != len(matrix[0]):
        raise MatrixError('Matrix is not square')
    a = copy.deepcopy(matrix)
    det = 1
    n = len(matrix)
    for i in range(n):
        for j in range(i):
            if a[i][j] != 0:
                if abs(a[j][j]) > 1e-12:
                    c = a[i][j] / a[j][j]
                    a[i][j] = 0
                    for k in range(j + 1, n):
                        a[i][k] -= c * a[j][k]
                else:
                    for k in range(n):
                        a[i][k], a[j][k] = a[j][k], a[i][k]
                    det *= (-1)
    for i in range(n):
        det *= a[i][i]
    return det


def generate_random_matrix(size):
    return [[randint(-size, size) for j in range(size)] for i in range(size)]
