
def rhoddw(temperature):

    """
    Calculates the density of pure water
    :param temperature:
    :return: water density
    """

    z0 = 999.83952
    z1 = 16.945176
    z2 = -0.0079870401
    z3 = -0.000046170461
    z4 = 0.00000010556302
    z5 = -2.8054253E-10
    z6 = 0.01687985

    rhot2 = z2 + float(temperature) * (z3 + float(temperature) * (z4 + float(temperature * z5)))
    rhot1 = z0 + float(temperature) * (z1 + float(temperature) * rhot2)
    rhoddw = rhot1 * 0.001 / (1 + z6 * float(temperature))

    return rhoddw

def h2odvdt1(vol1, temp1, temp2):

    # Calculates the given volume that an aqueous liquid would occupy at a given temp (temp2)
    # Uses the change from temp1 to temp2
    # See F4 Volume Properties of Water, CRC Handbook

    if temp1 == 0 or temp1 == -9:
        h2odvdt1 = 0
    else:
        rhoratio = rhoddw(float(temp1)) / rhoddw(float(temp2))
        h2odvdt1 = float(vol1) * rhoratio

    return h2odvdt1


def glassdvdt(volume, known_temp, desired_temp):

    # Calculates the actual volume of a glass container at a given temperature, from the known volume at 20
    expansion_coef = 0.00000975  # For borosilicate glass

    glass_dvdt = float(volume) * (1 + expansion_coef * (float(desired_temp) - float(known_temp)))

    return glass_dvdt


def oxycalc(thio20n, titer20, blank, botvol):
    # Constants
    o2mlpmeq = 5.598  # mL of O2 (STP) per milliequiv of O2 gas (5.598mL)
    doreag = 0.0017  # Dissolved O2 in reagents @ 25deg
    vreag = 2  # Volume of reagents used (2.0mL)

    if float(thio20n) == 0 or float(titer20) == 0 or float(blank) == 0 or float(botvol) == 0 or float(
            titer20) == -9:
        oxycalc = 0
    else:
        o2ml = (float(titer20) - float(blank)) * float(thio20n) * o2mlpmeq - doreag
        oxycalc = round(o2ml / ((float(botvol) - vreag) * 0.001), 3)

    return oxycalc

def corrthionorm(iodatevol, iodatenorm, blank, stdtiter):

    thio20N = (float(iodatevol) * float(iodatenorm)) / (float(stdtiter) - float(blank))

    return thio20N

def get_index(arr, searchitem):
    for i, x in enumerate(arr):
        for j, y in enumerate(x):
            if y == searchitem:
                return i, j
    return None  # if not found, but shouldn't happen unless doing check
