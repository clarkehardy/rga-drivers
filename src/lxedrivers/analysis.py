import numpy as np

def get_partial_pressures(isotopes, mass_axis, pressures):
    """Get the partial pressures at a few selected masses.

    Args:
        isotopes (list): the masses of the isotopes of interest.
        mass_axis (list): the full list of masses scanned
        pressures (list): the full list of pressures measured

    Returns:
        list: a list of the partial pressures for the isotopes of interest
    """
    mass_indices = np.array([np.argmin(np.abs(mass_axis - i)) for i in isotopes])
    partial_pressures = np.array(pressures)[mass_indices]

    return partial_pressures


def get_abundances(pressures):
    """Compute the abundances of a set of isotopes.

    Args:
        pressures (list): a list of the partial pressures
        of all the isotopes

    Returns:
        list: a list containing the abundances expressed as percentages
    """
    pressures = np.array(pressures)
    pressures[pressures < 0] = 0
    total_pressure = np.sum(pressures)

    return pressures*100/total_pressure