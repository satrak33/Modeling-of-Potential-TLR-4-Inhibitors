"""OpenBabel runtime setup and checked charge assignment."""
import math
import os
from contextlib import contextmanager
from pathlib import Path

import openbabel
from loguru import logger

_bin = Path(openbabel.__file__).resolve().parent / "bin"
for variable, folder in (("BABEL_DATADIR", _bin / "data"), ("BABEL_LIBDIR", _bin)):
    configured = os.environ.get(variable)
    if folder.is_dir() and (not configured or not Path(configured).is_dir()):
        os.environ[variable] = str(folder)

from openbabel import openbabel as ob
from openbabel import pybel


@contextmanager
def babel_diagnostics():
    """Forward native diagnostics to the active pipeline logger."""
    level = ob.obErrorLog.GetOutputLevel()
    ob.obErrorLog.ClearLog()
    ob.obErrorLog.SetOutputLevel(-1)
    try:
        yield
    finally:
        for severity, emit in ((ob.obError, logger.error), (ob.obWarning, logger.warning)):
            for message in ob.obErrorLog.GetMessagesOfLevel(severity):
                emit("OpenBabel: {}", message.strip())
        ob.obErrorLog.SetOutputLevel(level)


def prepare_receptor(path):
    with babel_diagnostics():
        receptor = next(pybel.readfile("pdb", str(path)))
        receptor.OBMol.DeleteHydrogens()
        for atom in ob.OBMolAtomIter(receptor.OBMol):
            if atom.GetAtomicNum() == 12:
                if atom.GetExplicitDegree() != 0:
                    raise RuntimeError("Bonded magnesium requires explicit receptor preparation")
                atom.SetFormalCharge(2)
                atom.SetImplicitHCount(0)
        receptor.addh()
        assign_charges(receptor.OBMol, allow_magnesium=True)
    return receptor


def assign_charges(molecule, allow_magnesium=False):
    ions = {}
    if allow_magnesium:
        ions = {a.GetIdx(): 2.0 for a in ob.OBMolAtomIter(molecule)
                if a.GetAtomicNum() == 12 and a.GetExplicitDegree() == 0 and a.GetFormalCharge() == 2}
    work = ob.OBMol(molecule)
    for index in sorted(ions, reverse=True):
        work.DeleteAtom(work.GetAtom(index))
    model = ob.OBChargeModel.FindType("gasteiger")
    if not model or not model.ComputeCharges(work):
        raise RuntimeError("Gasteiger charge calculation failed; unsupported element or atom typing")
    charges = iter(a.GetPartialCharge() for a in ob.OBMolAtomIter(work))
    for atom in ob.OBMolAtomIter(molecule):
        charge = ions[atom.GetIdx()] if atom.GetIdx() in ions else next(charges)
        if not math.isfinite(charge):
            raise RuntimeError(f"Non-finite charge on atom {atom.GetIdx()}")
        atom.SetPartialCharge(charge)
    molecule.SetPartialChargesPerceived()
    if ions:
        logger.info("Preserved {} isolated Mg2+ ions with ionic charges; Gasteiger assigned to remaining atoms", len(ions))
