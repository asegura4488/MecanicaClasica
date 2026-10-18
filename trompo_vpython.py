"""Trompo y ángulos de Euler ZXZ. VPython 7, sin Matplotlib ni NumPy.

Ejecutar desde Python local (terminal o Jupyter local):
    pip install vpython
    python Trompo_Euler_VPython.py

Convención activa: R = Rz(phi) Rx(theta) Rz(psi), de cuerpo a laboratorio.
Ejes del mundo: z vertical. Las tasas de los controles se dan en grados/s;
el cálculo matricial utiliza radianes/s.
"""

from math import sin, cos, pi
from time import perf_counter
from vpython import (canvas, vector, color, arrow, cone, cylinder,
                     sphere, ring, box, label, slider, button, wtext, rate)

RAD = pi / 180.0
DEG = 180.0 / pi

# ============================================================
# 1. MATRICES (solo Python; deliberadamente sin NumPy)
# ============================================================
def Rz(a):
    return [[cos(a), -sin(a), 0.0],
            [sin(a),  cos(a), 0.0],
            [0.0,     0.0,   1.0]]


def Rx(a):
    return [[1.0, 0.0,     0.0],
            [0.0, cos(a), -sin(a)],
            [0.0, sin(a),  cos(a)]]


def mul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(3))
             for j in range(3)] for i in range(3)]


def trans(A):
    return [[A[j][i] for j in range(3)] for i in range(3)]


def suma(A, B):
    return [[A[i][j] + B[i][j] for j in range(3)] for i in range(3)]


def escala(c, A):
    return [[c * A[i][j] for j in range(3)] for i in range(3)]


def columna(A, j):
    return vector(A[0][j], A[1][j], A[2][j])


def vee(W):
    """De [omega]_x a las componentes de omega."""
    return vector(W[2][1], W[0][2], W[1][0])


JZ = [[0.0, -1.0, 0.0],
      [1.0,  0.0, 0.0],
      [0.0,  0.0, 0.0]]
JX = [[0.0, 0.0, 0.0],
      [0.0, 0.0, -1.0],
      [0.0, 1.0, 0.0]]

# Estado: ángulos en radianes, tasas en rad/s.
phi, theta, psi = 40*RAD, 35*RAD, 0*RAD
phi_dot, theta_dot, psi_dot = 35*RAD, 0*RAD, 110*RAD
corriendo = False
cambiando_controles = False
interfaz_lista = False
actualizar = True


def calcular():
    """Cinemática EXACTA: R, dR/dt, R^T dR/dt y (dR/dt) R^T."""
    A = Rz(phi)
    B = Rx(theta)
    C = Rz(psi)
    AB = mul(A, B)
    R = mul(AB, C)

    # Derivada del PRODUCTO de tres rotaciones:
    # dR = phi_dot*Jz*R + theta_dot*Rz(phi)*Jx*Rx(theta)*Rz(psi)
    #                    + psi_dot*R*Jz.
    termino_phi = escala(phi_dot, mul(JZ, R))
    termino_theta = escala(theta_dot, mul(mul(mul(A, JX), B), C))
    termino_psi = escala(psi_dot, mul(R, JZ))
    dR = suma(suma(termino_phi, termino_theta), termino_psi)

    Rt = trans(R)
    Wcuerpo = mul(Rt, dR)      # [omega_cuerpo]_x = R^T dR
    Wlab = mul(dR, Rt)         # [omega_lab]_x    = dR R^T
    w_cuerpo = vee(Wcuerpo)
    w_lab = vee(Wlab)

    e1 = columna(R, 0)
    e2 = columna(R, 1)
    e3 = columna(R, 2)
    k = vector(0, 0, 1)
    n = columna(A, 0)          # Línea de nodos: Rz(phi)*ex

    # Descomposición física (igual a vee(dR*R^T)):
    w_precesion = phi_dot * k
    w_nutacion = theta_dot * n
    w_propio = psi_dot * e3

    return (A, B, C, R, dR, Wcuerpo, Wlab, w_cuerpo, w_lab,
            e1, e2, e3, n, w_precesion, w_nutacion, w_propio)


# ============================================================
# 2. ESCENA 3D: los objetos se construyen UNA sola vez
# ============================================================
scene = canvas(title='<b>Ángulos de Euler — trompo 3D (convención ZXZ)</b>\n'
                     'Rojo/verde/azul: ejes del laboratorio. '
                     'Dorado: velocidad angular total.\n',
               width=980, height=590, background=vector(0.055, 0.07, 0.10))
scene.up = vector(0, 0, 1)
scene.forward = vector(-1.6, -2.2, -1.2)
scene.center = vector(0, 0, 0.90)
scene.range = 3.35

origen = vector(0, 0, 0)
k = vector(0, 0, 1)

# Plano de referencia y ejes fijos.
box(pos=vector(0, 0, -0.11), size=vector(5.3, 5.3, 0.035),
    color=color.gray(0.5), opacity=0.16)
for eje, col, texto in [
    (vector(1, 0, 0), color.red, 'X'),
    (vector(0, 1, 0), color.green, 'Y'),
    (vector(0, 0, 1), color.blue, 'Z')]:
    arrow(pos=origen, axis=2.65*eje, color=col,
          shaftwidth=0.035, headwidth=0.12)
    label(pos=2.86*eje, text=texto, box=False, height=14, color=col)

# Trompo: un cono cuya punta está cerca del origen y una varilla.
cuerpo = cone(pos=vector(0, 0, 1.40), axis=vector(0, 0, -1.30),
              radius=0.78, color=vector(0.24, 0.59, 0.93), opacity=0.95)
tapa = cylinder(pos=vector(0, 0, 1.40), axis=vector(0, 0, 0.09),
                radius=0.78, color=vector(0.10, 0.34, 0.69))
varilla = cylinder(pos=origen, axis=vector(0, 0, 2.48),
                   radius=0.064, color=color.gray(0.83))
aro = ring(pos=vector(0, 0, 1.50), axis=k,
           radius=0.70, thickness=0.03, color=color.white)
punta = sphere(pos=origen, radius=0.095, color=color.white)

# Esta marca rompe la simetría visual: permite VER el ángulo psi.
marca = cylinder(pos=vector(0, 0, 1.52), axis=vector(0.68, 0, 0),
                 radius=0.048, color=color.orange)
bolita = sphere(pos=vector(0.68, 0, 1.52), radius=0.09,
                color=color.orange, emissive=True)

# Base móvil del sólido, línea de nodos y velocidades angulares.
b1 = arrow(pos=origen, axis=vector(1, 0, 0),
           color=color.yellow, shaftwidth=0.035)
b2 = arrow(pos=origen, axis=vector(0, 1, 0),
           color=color.cyan, shaftwidth=0.035)
b3 = arrow(pos=origen, axis=vector(0, 0, 1),
           color=color.white, shaftwidth=0.050)
nodos = arrow(pos=origen, axis=vector(1, 0, 0),
              color=color.magenta, shaftwidth=0.030)

omega_lab_flecha = arrow(pos=origen, axis=vector(0, 0, 1),
                         color=vector(1.0, 0.77, 0.14), shaftwidth=0.085,
                         headwidth=0.20)
omega_phi_flecha = arrow(pos=origen, axis=vector(0, 0, 1),
                         color=vector(0.88, 0.33, 0.89), shaftwidth=0.028)
omega_theta_flecha = arrow(pos=origen, axis=vector(1, 0, 0),
                           color=color.cyan, shaftwidth=0.028)
omega_psi_flecha = arrow(pos=origen, axis=vector(0, 0, 1),
                         color=color.orange, shaftwidth=0.028)

def flecha(obj, origen_flecha, direccion):
    obj.pos = origen_flecha
    obj.axis = direccion
    obj.visible = direccion.mag > 1.0e-7


def dibujar(datos):
    (_, _, _, _, _, _, _, _, wlab,
     e1, e2, e3, n, wphi, wtheta, wpsi) = datos

    # Actualizamos posiciones y ejes sin reconstruir geometría.
    cuerpo.pos = 1.40*e3
    cuerpo.axis = -1.30*e3
    tapa.pos = 1.40*e3
    tapa.axis = 0.09*e3
    varilla.axis = 2.48*e3
    aro.pos = 1.50*e3
    aro.axis = e3
    marca.pos = 1.52*e3
    marca.axis = 0.68*e1
    bolita.pos = 1.52*e3 + 0.68*e1

    flecha(b1, 0.55*e3, 1.18*e1)
    flecha(b2, 0.55*e3, 1.18*e2)
    flecha(b3, origen, 2.85*e3)
    flecha(nodos, origen, 1.35*n)

    # Visualización del vector total y de sus tres contribuciones.
    base = 0.45*e3
    escala_visual = 0.54  # Solo escala gráfica, NO cambia el valor de omega.
    flecha(omega_lab_flecha, base, escala_visual*wlab)
    flecha(omega_phi_flecha, base, escala_visual*wphi)
    flecha(omega_theta_flecha, base, escala_visual*wtheta)
    flecha(omega_psi_flecha, base, escala_visual*wpsi)


# ============================================================
# 3. INTERFAZ: tres ángulos + tres velocidades + botones
# ============================================================
def detener_para_editar():
    global corriendo, actualizar
    corriendo = False
    boton_animacion.text = 'Animar'
    actualizar = True


def al_cambiar_angulo(s):
    global phi, theta, psi
    if not interfaz_lista or cambiando_controles:
        return
    phi = control_phi.value * RAD
    theta = control_theta.value * RAD
    psi = control_psi.value * RAD
    detener_para_editar()


def al_cambiar_velocidad(s):
    global phi_dot, theta_dot, psi_dot, actualizar
    if not interfaz_lista or cambiando_controles:
        return
    phi_dot = control_pdot.value * RAD
    theta_dot = control_tdot.value * RAD
    psi_dot = control_sdot.value * RAD
    actualizar = True


def alternar(b):
    global corriendo, actualizar
    corriendo = not corriendo
    b.text = 'Pausar' if corriendo else 'Animar'
    actualizar = True


def reiniciar(b):
    global corriendo, phi, theta, psi, phi_dot, theta_dot, psi_dot
    global actualizar, cambiando_controles
    corriendo = False
    boton_animacion.text = 'Animar'
    phi, theta, psi = 40*RAD, 35*RAD, 0.0
    phi_dot, theta_dot, psi_dot = 35*RAD, 0.0, 110*RAD
    cambiando_controles = True
    control_phi.value, control_theta.value, control_psi.value = 40, 35, 0
    control_pdot.value, control_tdot.value, control_sdot.value = 35, 0, 110
    cambiando_controles = False
    actualizar = True


scene.append_to_caption('\n<b>ORIENTACIÓN (grados)</b> — mover una barra pausa la animación\n')
scene.append_to_caption('φ (precesión)  ')
control_phi = slider(min=0, max=360, value=40, length=280,
                     step=1, bind=al_cambiar_angulo)
lectura_phi = wtext(text='')
scene.append_to_caption('\nθ (nutación)  ')
control_theta = slider(min=0, max=180, value=35, length=280,
                       step=1, bind=al_cambiar_angulo)
lectura_theta = wtext(text='')
scene.append_to_caption('\nψ (giro propio) ')
control_psi = slider(min=0, max=360, value=0, length=280,
                     step=1, bind=al_cambiar_angulo)
lectura_psi = wtext(text='')

scene.append_to_caption('\n\n<b>VELOCIDADES ANGULARES PROGRAMADAS (grados/s)</b>\n')
scene.append_to_caption('φ̇  ')
control_pdot = slider(min=-150, max=150, value=35, length=240,
                      step=1, bind=al_cambiar_velocidad)
lectura_pdot = wtext(text='')
scene.append_to_caption('\nθ̇  ')
control_tdot = slider(min=-150, max=150, value=0, length=240,
                      step=1, bind=al_cambiar_velocidad)
lectura_tdot = wtext(text='')
scene.append_to_caption('\nψ̇  ')
control_sdot = slider(min=-150, max=150, value=110, length=240,
                      step=1, bind=al_cambiar_velocidad)
lectura_sdot = wtext(text='')
scene.append_to_caption('\n\n')
boton_animacion = button(text='Animar', bind=alternar)
scene.append_to_caption('     ')
button(text='Reiniciar', bind=reiniciar)
scene.append_to_caption('\n\n<b>LECTURA CINEMÁTICA (radianes/s)</b>\n')
lectura_matrices = wtext(text='')
scene.append_to_caption('\n')
interfaz_lista = True


def fmt(A):
    return '\n'.join('  [' + ' '.join(f'{v: 7.3f}' for v in fila) + ' ]'
                     for fila in A)


def vfmt(v):
    return f'({v.x:+.3f}, {v.y:+.3f}, {v.z:+.3f})'


def mostrar_matrices(datos):
    A, B, C, R, dR, Wc, Wl, wc, wl, *resto = datos

    lectura_phi.text = f'  {phi*DEG:6.1f}°'
    lectura_theta.text = f'  {theta*DEG:6.1f}°'
    lectura_psi.text = f'  {psi*DEG:6.1f}°'
    lectura_pdot.text = f'  {phi_dot*DEG:+6.1f}°/s'
    lectura_tdot.text = f'  {theta_dot*DEG:+6.1f}°/s'
    lectura_sdot.text = f'  {psi_dot*DEG:+6.1f}°/s'

    # <pre> conserva el formato matricial monoespaciado en el navegador.
    pantalla = (
        'R = Rz(φ) Rx(θ) Rz(ψ)         (de cuerpo a laboratorio)\n\n'
        + 'Rz(φ) =\n' + fmt(A) + '\n\n'
        + 'Rx(θ) =\n' + fmt(B) + '\n\n'
        + 'Rz(ψ) =\n' + fmt(C) + '\n\n'
        + 'R =\n' + fmt(R) + '\n\n'
        + 'dR/dt =\n' + fmt(dR) + '\n\n'
        + '[ω_cuerpo]× = Rᵀ dR/dt =\n' + fmt(Wc) + '\n\n'
        + '[ω_lab]× = (dR/dt) Rᵀ =\n' + fmt(Wl) + '\n\n'
        + 'ω_cuerpo = ' + vfmt(wc) + ' rad/s\n'
        + 'ω_lab    = ' + vfmt(wl) + ' rad/s\n'
        + f'|ω| = {wl.mag:.3f} rad/s\n\n'
        + 'ω_lab = φ̇ Z + θ̇ n + ψ̇ e₃     con n = Rz(φ) X\n'
        + 'Flechas: dorada = total; violeta = φ̇; cian = θ̇; naranja = ψ̇.\n'
        + 'En pausa se muestran las derivadas asociadas a las tasas elegidas.\n'
        + 'θ se refleja en 0° y 180° para mantener la convención de Euler.\n'
        + 'En θ = 0° o 180° los ángulos de Euler pierden unicidad.'
    )
    lectura_matrices.text = (
    '<pre style="font-size: 24px; line-height: 1.5;">'
    + pantalla +
    '</pre>'
    )


# ============================================================
# 4. ANIMACIÓN: geometría a ~60 FPS, matrices a ~8 FPS
# ============================================================
instante_anterior = perf_counter()
instante_panel = 0.0

while True:
    rate(60)
    instante = perf_counter()
    dt = min(instante - instante_anterior, 0.06)
    instante_anterior = instante

    if corriendo:
        phi = (phi + phi_dot*dt) % (2*pi)
        psi = (psi + psi_dot*dt) % (2*pi)
        theta += theta_dot*dt

        # Para mantener 0 <= theta <= pi, se invierte la nutación al llegar
        # al extremo (un control visual, no una ecuación de dinámica del trompo).
        if theta < 0:
            theta = -theta
            theta_dot = -theta_dot
        elif theta > pi:
            theta = 2*pi - theta
            theta_dot = -theta_dot

        actualizar = True

    if actualizar:
        datos = calcular()
        dibujar(datos)
        if (instante - instante_panel > 0.12) or not corriendo:
            # Sincronizar los 4 controles a ~8 Hz, no a 60 Hz:
            # así la animación 3D puede mantenerse más fluida.
            if corriendo:
                cambiando_controles = True
                control_phi.value = phi*DEG
                control_theta.value = theta*DEG
                control_psi.value = psi*DEG
                control_tdot.value = theta_dot*DEG
                cambiando_controles = False
            mostrar_matrices(datos)
            instante_panel = instante
        actualizar = corriendo

