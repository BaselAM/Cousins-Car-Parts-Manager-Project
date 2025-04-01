"""Additional functions for PyGLM

Reimplementation of MT's GLSL implementation of some linear algebra functions in 3D.

Source: CRL_oven/assets/glsl/linear.glsl
"""


import typing as tp
import glm


__all__ = [
    "mat3diag",
    "diag3",
    "sort3",
    "cbrt",
    "solveCubic",
    "ldu3",
    "lduBSolve3",
    "evd3",
    "svd3",
    "sop3",
    "mat2diag",
    "diag2",
    "rot2",
    "svd2",
    "evd2",
]


def mat3diag(x: glm.vec3) -> glm.mat3:
    """Constructs a 3x3 diagonal matrix."""
    m = glm.mat3()
    m[0][0] = x[0]
    m[1][1] = x[1]
    m[2][2] = x[2]
    return m


def diag3(x: glm.mat3) -> glm.vec3:
    """Extracts the diagonal vector of a 3x3 matrix."""
    return glm.vec3(x[0][0], x[1][1], x[2][2])


def sort3(x: glm.vec3) -> glm.vec3:
    """Sorts 3 elements in descending order in-place."""
    if x.x < x.x:
        x.x += x.y
        x.y = x.x - x.y
        x.x -= x.y

    if x.y < x.z:
        if x.x < x.z:
            x.x += x.z
            x.z = x.x - x.z
            x.x -= x.z
        else:
            x.y += x.z
            x.z = x.y - x.z
            x.y -= x.z

    return x


def cbrt(x: float) -> float:
    """Cubic root."""
    if x < 0:
        return -glm.pow(-x, 1 / 3)
    if x == 0:
        return 0
    return glm.pow(x, 1 / 3)


def solveCubic(c: glm.vec3) -> glm.vec3:
    """Solves cubic polynomial in-place.

    Given polynomial: c[0] + c[1]*x + c[2]*x^2 + x^3 = 0, assuming it has 3 real roots, find the
    roots and store them in c[0], c[1], c[2].
    """

    sq3d2 = 0.86602540378443864676
    c2d3 = c[2] / 3
    c2sq = c[2] * c[2]
    Q = (3 * c[1] - c2sq) / 9
    R = (c[2] * (9 * c[1] - 2 * c2sq) - 27 * c[0]) / 54

    if Q < 0:
        # Instead of computing
        # c_0 = A cos(t) - B
        # c_1 = A cos(t + 2 pi/3) - B
        # c_2 = A cos(t + 4 pi/3) - B
        # Use cos(a+b) = cos(a) cos(b) - sin(a) sin(b)
        # Keeps t small and eliminates 1 function call.
        # cos(2 pi/3) = cos(4 pi/3) = -0.5
        # sin(2 pi/3) = sqrt(3)/2
        # sin(4 pi/3) = -sqrt(3)/2

        tmp = 2 * glm.sqrt(-Q)
        t = glm.acos(R / glm.sqrt(-Q * Q * Q)) / 3
        cost = tmp * glm.cos(t)
        sint = tmp * glm.sin(t)

        c[0] = cost - c2d3

        cost = -0.5 * cost - c2d3
        sint = sq3d2 * sint

        c[1] = cost - sint
        c[2] = cost + sint
    else:
        tmp = cbrt(R)
        c[0] = -c2d3 + 2 * tmp
        c[1] = c[2] = -c2d3 - tmp


def ldu3(A: glm.mat3) -> tp.Tuple[glm.mat3, glm.ivec3]:
    """Computes the LDUP decomposition (LU with partial pivoting) in-place

    Parameters
    ----------
    A : glm.mat3
        the input and output matrix

    Returns
    -------
    A : glm.mat3
        the input and output matrix
    P : glm.ivec3
        the output pivoting integer vector
    """
    P = glm.ivec3(0, 1, 2)

    if abs(A[1][0]) > abs(A[0][0]):
        P[0] = 2 if abs(A[2][0]) > abs(A[1][0]) else 1
    else:
        P[0] = 2 if abs(A[2][0]) > abs(A[0][0]) else 0
    P[P[0]] = 0

    if abs(A[P[2]][1]) > abs(A[P[1]][1]):
        P[1] += P[2]
        P[2] = P[1] - P[2]
        P[1] -= P[2]

    x = A[P[0]][0]
    if x != 0:
        A[P[1]][0] /= x
        A[P[2]][0] /= x
        A[P[0]][1] /= x
        A[P[0]][2] /= x

    A[P[1]][1] -= A[P[0]][1] * A[P[1]][0] * A[P[0]][0]

    x = A[P[1]][1]
    if x != 0:
        A[P[2]][1] = (A[P[2]][1] - A[P[0]][1] * A[P[2]][0] * A[P[0]][0]) / x
        A[P[1]][2] = (A[P[1]][2] - A[P[0]][2] * A[P[1]][0] * A[P[0]][0]) / x

    A[P[2]][2] -= (
        A[P[0]][2] * A[P[2]][0] * A[P[0]][0] + A[P[1]][2] * A[P[2]][1] * A[P[1]][1]
    )

    return A, P


def lduBSolve3(y: glm.vec3, LDU: glm.mat3, P: glm.ivec3) -> glm.vec3:
    """Does the backward-solve step, or `U*x = y`"""
    x = glm.vec3()
    x[P[2]] = y[2]
    x[P[1]] = y[1] - LDU[P[2]][1] * x[P[2]]
    x[P[0]] = y[0] - LDU[P[2]][0] * x[P[2]] - LDU[P[1]][0] * x[P[1]]
    return x


def evd3(A: glm.mat3) -> tp.Tuple[glm.mat3, glm.vec3]:
    """Eigenvalue decomposes a symmetric positive semidefinite 3x3 matrix

    Compute: `A = V mat3diag(S) V.T`. Eigenvalues are sorted in the descending order.

    Parameters
    ----------
    A : glm.mat3
        input 3x3 matrix

    Returns
    -------
    V : glm.mat3
        output rotation matrix
    S : glm.vec3
        output diagonal vector
    """
    # Form the monic characteristic polynomial
    S = glm.vec3()
    S[2] = -A[0][0] - A[1][1] - A[2][2]
    S[1] = (
        A[0][0] * A[1][1]
        + A[2][2] * A[0][0]
        + A[2][2] * A[1][1]
        - A[2][1] * A[1][2]
        - A[2][0] * A[0][2]
        - A[1][0] * A[0][1]
    )
    S[0] = (
        A[2][1] * A[1][2] * A[0][0]
        + A[2][0] * A[0][2] * A[1][1]
        + A[1][0] * A[0][1] * A[2][2]
        - A[0][0] * A[1][1] * A[2][2]
        - A[1][0] * A[2][1] * A[0][2]
        - A[2][0] * A[0][1] * A[1][2]
    )

    # Solve the cubic equation.
    solveCubic(S)

    # All roots should be non-negative
    if S[0] < 0:
        S[0] = 0
    if S[1] < 0:
        S[1] = 0
    if S[2] < 0:
        S[2] = 0

    # Sort from greatest to least
    sort3(S)

    # Form the eigenvector system for the first (largest) eigenvalue
    LDU = glm.mat3(A)
    LDU[0][0] -= S[0]
    LDU[1][1] -= S[0]
    LDU[2][2] -= S[0]

    # Perform LDUP decomposition
    LDU, P = ldu3(LDU)

    # Write LDU = A-I*lambda.  Then an eigenvector can be
    # found by solving LDU x = LD y = L z = 0
    # L is invertible, so L z = 0 implies z = 0
    # D is singular since det(A-I*lambda) = 0 and so
    # D y = z = 0 has a non-unique solution.
    # Pick k so that D_kk = 0 and set y = e_k, the k'th column
    # of the identity matrix.
    # U is invertible so U x = y has a unique solution for a given y.
    # The solution for U x = y is an eigenvector.

    # Pick the component of D nearest to 0
    y = glm.vec3(0)
    if abs(LDU[P[1]][1]) < abs(LDU[P[0]][0]):
        k = 2 if abs(LDU[P[2]][2]) < abs(LDU[P[1]][1]) else 1
    else:
        k = 2 if abs(LDU[P[2]][2]) < abs(LDU[P[0]][0]) else 0
    y[k] = 1

    # Do a backward solve for the eigenvector
    V = glm.mat3()
    V[0] = lduBSolve3(y, LDU, P)

    # Form the eigenvector system for the last (smallest) eigenvalue
    LDU = glm.mat3(A)
    LDU[0][0] -= S[2]
    LDU[1][1] -= S[2]
    LDU[2][2] -= S[2]

    # Perform LDUP decomposition
    LDU, P = ldu3(LDU)

    # NOTE: The arrangement of the ternary operator output is IMPORTANT!
    # It ensures a different system is solved if there are 3 repeat eigenvalues.

    # Pick the component of D nearest to 0
    y = glm.vec3(0)
    if abs(LDU[P[0]][0]) < abs(LDU[P[2]][2]):
        k = 0 if abs(LDU[P[0]][0]) < abs(LDU[P[1]][1]) else 1
    else:
        k = 1 if abs(LDU[P[1]][1]) < abs(LDU[P[2]][2]) else 2
    y[k] = 1

    # Do a backward solve for the eigenvector
    V[2] = lduBSolve3(y, LDU, P)

    # The remaining column must be orthogonal (A is symmetric)
    V[1] = glm.cross(V[2], V[0])

    # Normalize the columns of V
    V[0] /= glm.length(V[0])
    V[1] /= glm.length(V[1])
    V[2] /= glm.length(V[2])

    return V, S


def svd3(A: glm.mat3, thr: float = 1e-6) -> tp.Tuple[glm.mat3, glm.vec3, glm.mat3]:
    """Singularvalue decomposes a 3x3 matrix.

    Compute `A = U mat3diag(S) V^T`. Singularvalues are sorted in descending order.

    Parameters
    ----------
    A : glm.mat3
        input 3x3 matrix
    thr : float
        small threshold for computing the rank

    Returns
    -------
    U : glm.mat3
        output rotation matrix
    S : glm.vec3
        output diagonal vector
    V : glm.mat3
        output rotation matrix
    """
    # Steps:
    # 1) Use eigendecomposition on A^T A to compute V.
    # Since A = U S V^T then A^T A = V S^T S V^T with D = S^T S and V the
    # eigenvalues and eigenvectors respectively (V is orthogonal).
    # 2) Compute U from A and V.
    # 3) Normalize columns of U and V and square-root the eigenvalues to obtain
    # the singular values.

    # Eigen-value decomposition of A^T A
    V, S = evd3(glm.transpose(A) * A)

    # Count the rank
    k = int(S[0] > thr) + int(S[1] > thr) + int(S[2] > thr)

    if k == 0:
        # Zero matrix.
        # Since V is already orthogonal, just copy it into U.
        U = glm.mat3(V)
    elif k == 1:
        # The first singular value is non-zero.
        # Since A = U S V^T, then A V = U S.
        # A V_1 = S_11 U_1 is non-zero. Here V_1 and U_1 are
        # column vectors. Since V_1 is known, we may compute
        # U_1 = A V_1.  The S_11 factor is not important as
        # U_1 will be normalized later.
        U[0] = A * V[0]

        # The other columns of U do not contribute to the expansion
        # and we may arbitrarily choose them (but they do need to be
        # orthogonal). To ensure the first cross product does not fail,
        # pick k so that U_k1 is nearest 0 and then cross with e_k to
        # obtain an orthogonal vector to U_1.
        y = glm.vec3(0)
        if abs(U[0][0]) < abs(U[0][2]):
            k = 0 if abs(U[0][0]) < abs(U[0][1]) else 1
        else:
            k = 1 if abs(U[0][1]) < abs(U[0][2]) else 2
        y[k] = 1

        U[1] = glm.cross(y, U[0])

        # Cross the first two to obtain the remaining column
        U[2] = glm.cross(U[0], U[1])
    elif k == 2:
        # The first two singular values are non-zero.
        # Compute U_1 = A V_1 and U_2 = A V_2. See case 1
        # for more information.
        U[0] = A * V[0]
        U[1] = A * V[1]

        # Cross the first two to obtain the remaining column
        U[2] = glm.cross(U[0], U[1])
    else:
        # All singular values are non-zero.
        # We may compute U = A V. See case 1 for more information.
        U = A * V

    # Normalize the columns of U
    U[0] /= glm.length(U[0])
    U[1] /= glm.length(U[1])
    U[2] /= glm.length(U[2])

    # S was initially the eigenvalues of A^T A = V S^T S V^T which are squared.
    S[0] = glm.sqrt(S[0])
    S[1] = glm.sqrt(S[1])
    S[2] = glm.sqrt(S[2])

    return U, S, V


def sop3(A: glm.mat3) -> glm.mat3:
    """Finds the nearest rotation."""
    U, D, V = svd3(A, 1e-10)
    VT = glm.transpose(V)
    R = U * VT
    if glm.determinant(R) < 0:
        # fix the sign by switching the last column
        U[2] = -U[2]
        R = U * VT

    return R


def mat2diag(x: glm.vec2) -> glm.mat2:
    """Constructs a 2x2 diagonal matrix."""
    m = glm.mat2()
    m[0][0] = x[0]
    m[1][1] = x[1]
    return m


def diag2(x: glm.mat2) -> glm.vec2:
    """Extracts the diagonal vector of a 2x2 matrix."""
    return glm.vec2(x[0][0], x[1][1])


def rot2(angle: float) -> glm.mat2:
    """Gets a 2D rotation matrix given the rotation angle in radian."""

    sa = glm.sin(angle)
    ca = glm.cos(angle)
    return glm.mat2(glm.vec2(ca, sa), glm.vec2(-sa, ca))


def svd2(A: glm.mat2) -> glm.vec4:
    """Singularvalue decomposes a 2x2 matrix.

    Compute `A = U mat2diag(S) V^T`. Singularvalues are sorted in descending order.

    Source from `here <https://lucidar.me/en/mathematics/singular-value-decomposition-of-a-2x2-matrix/>`_

    Parameters
    ----------
    A : glm.mat2
        input 2x2 matrix

    Returns
    -------
    glm.vec4
        Parameter (s1, s2, u, v) where `A = rot2(u) * mat2diag(s1, s2) * rot2(-v)`.
    """

    # compute u
    a, c = A[0]
    b, d = A[1]
    t1 = a * a + b * b
    t2 = c * c + d * d
    t3 = a * c + b * d
    u = 0.5 * glm.atan2(2 * t3, t1 - t2)
    su = glm.sin(u)
    cu = glm.cos(u)

    # compute s1 and s2
    S1 = t1 + t2
    S2 = glm.sqrt((t1 - t2) * (t1 - t2) + 4 * t3 * t3)
    s1 = glm.sqrt(0.5 * (S1 + S2))
    s2 = glm.sqrt(0.5 * (S1 - S2))

    # compute v
    t4 = a * b + c * d
    t5 = a * a + c * c - b * b - d * d
    v = 0.5 * glm.atan2(2 * t4, t5)
    sv = glm.sin(v)
    cv = glm.cos(v)

    # correct v, s1 and s2
    s11 = (a * cu + c * su) * cv + (b * cu + d * su) * sv
    if s11 == 0:
        s1 = 0
    elif s11 < 0:
        s1 = -s1
    s22 = (a * cu - c * cu) * sv + (d * cu - b * su) * cv
    if s22 == 0:
        s2 = 0
    elif s22 < 0:
        s2 = -s2
    if s1 < s2:
        s1 = -s1
        s2 = -s2
        v += glm.pi()

    return glm.vec4(s1, s2, u, v)


def evd2(A: glm.mat2) -> glm.vec3:
    """Eigenvalue decomposes a symmetric positive semidefinite 2x2 matrix

    Compute: `A = V mat2diag(S) V.T`. Eigenvalues are sorted in the descending order.

    Parameters
    ----------
    A : glm.mat2
        input 2x2 matrix

    Returns
    -------
    glm.vec3
        Parameter (s1, s2, u) where `A = rot2(u) * mat2diag(s1, s2) * rot2(-u)`.
    """

    # Cholesky decomposition
    L11 = glm.sqrt(A[0][0])
    L21 = A[0][1] / L11
    L22 = glm.sqrt(A[1][1] - L21 * L21)
    L = glm.mat2(glm.vec2(L11, L21), glm.vec2(0, L22))

    # svd2 it
    v = svd2(L)

    r = glm.vec3(v.x * v.x, v.y * v.y, v.z)
    if r.x < r.y:
        r = glm.vec3(r.y, r.x, r.z + glm.pi() / 2)
    return r
